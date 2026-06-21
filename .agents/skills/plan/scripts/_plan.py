#!/usr/bin/env python3
"""plan.py — deterministic PLAN.md manager with atomic updates.

All reads and writes of PLAN.md are done via this script.
Uses only Python 3.10+ built-in modules.

Concurrency model:
  - All mutating commands use _safe_edit() which holds an exclusive
    file lock (fcntl.flock) for the entire read-transform-write cycle.
  - Read-only commands use a shared lock so they never see partial state.
  - Writes are crash-safe: temp file + fsync + atomic rename on same
    filesystem. Orphaned temp files from crashes are cleaned up.
  - A SHA-256 checksum comment at the bottom of each PLAN.md allows
    detecting corruption after any write.
"""
__all__ = ['parse_plan_data']

import argparse
import fcntl
import hashlib
import json as _json_mod
import os
import re
import shlex
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STATUS_TODO = "\u2610"          # ☐ Not Started / To Do
STATUS_QUESTION = "\u2753"      # ❓ Needs Clarification / Question
STATUS_DOING = "\u2699\uFE0F"   # ⚙️ Active / Doing
STATUS_ERROR = "\u274C"         # ❌ Blocked / Error
STATUS_DONE = "\u2611"          # ☑ Completed / Done

ALL_STATUSES = {STATUS_TODO, STATUS_QUESTION, STATUS_DOING, STATUS_ERROR, STATUS_DONE}

# Valid transitions for tasks and phases: from_emoji -> set of allowed to_emojis
VALID_TRANSITIONS = {
    STATUS_TODO:     {STATUS_DOING, STATUS_QUESTION},
    STATUS_DOING:    {STATUS_QUESTION, STATUS_ERROR, STATUS_DONE},
    STATUS_QUESTION: {STATUS_DOING},
    STATUS_ERROR:    {STATUS_DOING, STATUS_QUESTION},
}

# Plan-level transitions: same as task/phase plus ❓→❌.
# During scope clarification (❓), a critical blocker may be discovered
# that makes the plan unactionable — marking it ❌ signals "cannot proceed
# until this blocker is resolved" without requiring ⚙️ first.
PLAN_TRANSITIONS = {
    STATUS_TODO:     {STATUS_DOING, STATUS_QUESTION},
    STATUS_DOING:    {STATUS_QUESTION, STATUS_ERROR, STATUS_DONE},
    STATUS_QUESTION: {STATUS_DOING, STATUS_ERROR},
    STATUS_ERROR:    {STATUS_DOING, STATUS_QUESTION},
}

# Default lock-acquire timeout in seconds.
# Raised with TimeoutError if another process holds the lock longer.
LOCK_TIMEOUT = 10.0

# ---------------------------------------------------------------------------
# JSON output helpers
# ---------------------------------------------------------------------------

class PlanError(Exception):
    """Raised by commands to signal an error. Caught by the JSON wrapper."""
    pass


def _result(status: str, command: str, message: str, **kwargs) -> dict:
    """Build a JSON result dict with status, command, message, and optional fields."""
    return {
        "status": status,
        "command": command,
        "message": message,
        **kwargs,
    }


def _print_json_result(result: dict) -> None:
    """Print a result dict as JSON to stdout."""
    print(_json_mod.dumps(result, ensure_ascii=False))


def _run_command(handler, args: argparse.Namespace) -> dict:
    """Run a command handler and return a JSON result dict.

    Catches PlanError and generic exceptions, converting them to error results.
    Handlers that already return a dict pass through unchanged.
    """
    cmd_name = args.command.replace("-", "-")
    try:
        res = handler(args)
        # If handler returned a dict (new style), use it directly
        if isinstance(res, dict):
            return res
        # Legacy: handler printed and returned None — treat as success
        return _result("success", cmd_name, "")
    except PlanError as e:
        return _result("error", cmd_name, str(e))
    except Exception as e:
        return _result("error", cmd_name, f"unexpected error: {e}")

# ---------------------------------------------------------------------------
# Atomic file I/O + locking + checksums
# ---------------------------------------------------------------------------

def _lock_path(plan_path: str) -> str:
    """Return the lock file path for a given PLAN.md."""
    return plan_path + ".lock"


def _acquire_exclusive_lock(plan_path: str, timeout: float = LOCK_TIMEOUT) -> int:
    """Acquire an exclusive (write) advisory lock on the plan.

    Returns the file descriptor holding the lock.
    Caller must call _release_lock(fd, plan_path) when done.

    The lock is held for the ENTIRE read-transform-write cycle so
    concurrent editors serialize deterministically — no lost updates.
    """
    fd = os.open(_lock_path(plan_path), os.O_CREAT | os.O_RDWR)
    # Write our PID so waiters can diagnose contention
    os.write(fd, str(os.getpid()).encode())
    os.lseek(fd, 0, os.SEEK_SET)

    deadline = time.monotonic() + timeout
    while True:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fd
        except BlockingIOError:
            if time.monotonic() > deadline:
                os.lseek(fd, 0, os.SEEK_SET)
                holder_pid = os.read(fd, 32).decode().strip()
                os.close(fd)
                raise TimeoutError(
                    f"Lock on {plan_path} held by PID {holder_pid}, "
                    f"timeout after {timeout}s"
                )
            time.sleep(0.05)


def _acquire_shared_lock(plan_path: str) -> int:
    """Acquire a shared (read) advisory lock on the plan.

    Multiple readers coexist; blocks only when a writer holds LOCK_EX.
    Returns the file descriptor holding the lock.
    Caller must call _release_lock(fd, plan_path) when done.
    """
    fd = os.open(_lock_path(plan_path), os.O_CREAT | os.O_RDWR)
    fcntl.flock(fd, fcntl.LOCK_SH)
    return fd


def _release_lock(fd: int, plan_path: str) -> None:
    """Release an advisory lock, close its file descriptor, and remove the lock file.

    The lock file is unlinked after the fd is closed. On Linux this is safe:
    any other process holding a fd to the same inode (e.g. a reader that opened
    the file before we deleted it) keeps its lock until it closes its own fd.
    The inode is reclaimed automatically when the last fd closes.
    """
    fcntl.flock(fd, fcntl.LOCK_UN)
    os.close(fd)
    lock_file = _lock_path(plan_path)
    try:
        os.unlink(lock_file)
    except FileNotFoundError:
        pass  # another concurrent release already cleaned it up


def write_plan_atomic(path: str, content: str) -> None:
    """Write content to PLAN.md atomically.

    1. Write to a temp file in the SAME directory (same filesystem).
    2. fsync() to flush to disk — crash after this point is safe.
    3. rename() temp → target — atomic on same filesystem.
    4. Preserve original file permissions.

    After a crash: PLAN.md is either the old version or the new one,
    never partial. The orphaned .tmp is cleaned up next invocation.
    """
    p = Path(path)
    dir_ = p.parent
    content_bytes = content.encode("utf-8")

    fd, tmp_path = tempfile.mkstemp(
        dir=str(dir_), prefix=".plan.tmp.", suffix=".md"
    )
    closed = False
    try:
        written = os.write(fd, content_bytes)
        if written != len(content_bytes):
            raise IOError(
                f"Short write: {written} != {len(content_bytes)} bytes"
            )
        os.fsync(fd)
        os.close(fd)
        closed = True

        # Preserve permissions of original file if it exists
        if p.exists():
            st = p.stat()
            os.chmod(tmp_path, st.st_mode)

        os.rename(tmp_path, str(p))
    except BaseException:
        if not closed:
            try:
                os.close(fd)
            except OSError:
                pass
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise


def _cleanup_orphans(plan_path: str) -> None:
    """Remove stale .tmp files from crashed writes.

    Must be called under exclusive lock so no live writer is racing.
    """
    dir_ = Path(plan_path).parent
    for f in dir_.glob(".plan.tmp.*.md"):
        try:
            f.unlink()
        except FileNotFoundError:
            pass


# ---------------------------------------------------------------------------
# Checksums — content integrity verification
# ---------------------------------------------------------------------------

_CHECKSUM_RE = re.compile(r"^<!-- checksum: ([a-f0-9]{16}) -->$")


def _compute_checksum(content: str) -> str:
    """Compute a 16-char hex SHA-256 digest of content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _add_checksum(content: str) -> str:
    """Strip any old checksum line, then append a fresh one.

    The checksum covers everything in the file EXCEPT the checksum
    comment itself, so reads can verify integrity without self-
    reference issues.
    """
    lines = [
        l for l in content.splitlines()
        if not _CHECKSUM_RE.match(l.strip())
    ]
    # Rejoin preserving original line endings style (always \n)
    body = "\n".join(lines)
    if not body.endswith("\n"):
        body += "\n"
    checksum = _compute_checksum(body)
    return body + f"<!-- checksum: {checksum} -->\n"


def _strip_checksum(content: str) -> str:
    """Remove the checksum comment line from content."""
    return "\n".join(
        l for l in content.splitlines()
        if not _CHECKSUM_RE.match(l.strip())
    )


def _verify_checksum(content: str) -> bool:
    """Verify the file's integrity against its stored checksum.

    Returns True if checksum matches or file has no checksum yet
    (pre-atomic era). Returns False on mismatch (corruption detected).
    """
    lines = content.splitlines()
    stored = None
    for line in reversed(lines):
        m = _CHECKSUM_RE.match(line.strip())
        if m:
            stored = m.group(1)
            break
    if stored is None:
        return True  # No checksum — assume valid (new file or legacy)

    # Body is everything except the checksum line
    body_lines = [
        l for l in lines if not _CHECKSUM_RE.match(l.strip())
    ]
    body = "\n".join(body_lines)
    if not body.endswith("\n"):
        body += "\n"
    computed = _compute_checksum(body)
    return stored == computed


# ---------------------------------------------------------------------------
# Safe edit wrapper — lock → read → transform → write → unlock
# ---------------------------------------------------------------------------

def read_plan(path: str) -> str:
    """Read PLAN.md and return its contents (checksum stripped)."""
    p = Path(path)
    if not p.exists():
        raise PlanError(f"{path} does not exist")
    raw = p.read_text(encoding="utf-8")
    return _strip_checksum(raw)


def read_plan_raw(path: str) -> str:
    """Read PLAN.md including the checksum line (for verification)."""
    p = Path(path)
    if not p.exists():
        raise PlanError(f"{path} does not exist")
    return p.read_text(encoding="utf-8")


def _safe_edit(plan_path: str, transform_fn) -> str:
    """Exclusive lock → read → transform → atomic write → unlock.

    The lock is held for the ENTIRE operation so concurrent editors
    serialize deterministically. No lost updates possible.

    Args:
        plan_path: Path to the PLAN.md file.
        transform_fn: Pure function(content: str) -> str that produces
                      the new file content (without checksum).

    Returns:
        The final written content (with checksum appended).
    """
    fd = _acquire_exclusive_lock(plan_path)
    try:
        # 1. Clean orphaned temp files from any prior crash
        _cleanup_orphans(plan_path)

        # 2. Read fresh content under lock (no one else can modify)
        raw = read_plan_raw(plan_path)

        # 3. Verify integrity
        if not _verify_checksum(raw):
            print(
                f"Warning: checksum mismatch in {plan_path} — "
                "file may be corrupted",
                file=sys.stderr,
            )

        content = _strip_checksum(raw)

        # 4. Transform (pure function, no I/O)
        new_content = transform_fn(content)

        # 5. Append checksum and write atomically
        final_content = _add_checksum(new_content)
        write_plan_atomic(plan_path, final_content)

        return final_content
    finally:
        _release_lock(fd, plan_path)


def _safe_read(plan_path: str) -> str:
    """Shared lock → read → unlock.

    Readers don't block each other but block during writes, ensuring
    they never see partial state.
    """
    fd = _acquire_shared_lock(plan_path)
    try:
        raw = read_plan_raw(plan_path)
        if not _verify_checksum(raw):
            print(
                f"Warning: checksum mismatch in {plan_path} — "
                "file may be corrupted",
                file=sys.stderr,
            )
        return _strip_checksum(raw)
    finally:
        _release_lock(fd, plan_path)


def write_plan(path: str, content: str) -> None:
    """Write content to PLAN.md atomically via temp file.

    Kept for backward compatibility / non-locked writes (e.g. cmd_create
    which creates a new file that doesn't need locking).
    """
    write_plan_atomic(path, content)


# ---------------------------------------------------------------------------
# Helpers — header parsing
# ---------------------------------------------------------------------------
# The header is NOT YAML; it's markdown bullet fields.
# We parse lines like:
#   - Depends On: ...
#   - Created: ...
#   - Updated: ...
#   - Current Phase: ...
#   - Current Task: ...

_HEADER_FIELDS = {
    "depends_on": r"^- Depends On:(.+)$",
    "created": r"^- Created:(.+)$",
    "updated": r"^- Updated:(.+)$",
    "current_phase": r"^- Current Phase:(.+)$",
    "current_task": r"^- Current Task:(.+)$",
}


def _parse_header(title_line: str, body_lines: list[str]) -> dict:
    """Return dict with header field values."""
    header = {}
    for key, pattern in _HEADER_FIELDS.items():
        for line in body_lines:
            m = re.match(pattern, line.strip())
            if m:
                header[key] = m.group(1).strip()
                break
        else:
            header[key] = ""
    return header


def _find_header_field_line(lines: list[str], field_name: str) -> int:
    """Return index of line containing `- Field:` or -1."""
    pattern = rf"^- {re.escape(field_name)}:"
    for i, line in enumerate(lines):
        if re.match(pattern, line.strip()):
            return i
    return -1


def _update_header_field(lines: list[str], field_name: str, value: str) -> list[str]:
    """Update or append a header field line. Returns new lines."""
    pattern = rf"^- {re.escape(field_name)}:"
    idx = -1
    for i, line in enumerate(lines):
        if re.match(pattern, line.strip()):
            idx = i
            break
    if idx >= 0:
        lines[idx] = f"- {field_name}: {value}"
    else:
        # Insert after `- Current Task:` or before first phase heading
        current_task_idx = _find_header_field_line(lines, "Current Task")
        if current_task_idx >= 0:
            lines.insert(current_task_idx + 1, f"- {field_name}: {value}")
        else:
            # Find first ## Phase line and insert before it
            for i, line in enumerate(lines):
                if re.match(r"^## ", line):
                    lines.insert(i, f"- {field_name}: {value}")
                    break
            else:
                lines.append(f"- {field_name}: {value}")
    return lines


def _strip_header_comment(line: str) -> str:
    """Remove inline comment from header template line."""
    return re.sub(r"\s*<!--.*?-->\s*$", "", line).strip()


# ---------------------------------------------------------------------------
# Helpers — argument parsing (phase_ref / task_ref with optional description)
# ---------------------------------------------------------------------------

def parse_phase_arg(arg: str) -> int:
    """Extract phase number from a phase argument.

    Accepts: 'Phase 2', 'Phase 2 ➖ Description...'
    Returns: phase number (int).
    """
    # Split on first ' ➖ ' to strip optional description
    id_part = arg.split(" ➖ ", 1)[0].strip()
    m = re.match(r"Phase\s+(\d+)", id_part)
    if not m:
        raise PlanError(f"invalid phase ref: {arg!r}")
    return int(m.group(1))


def parse_task_arg(arg: str) -> tuple[int, int]:
    """Extract (phase_num, task_num) from a task argument.

    Accepts: 'Task 2.4', 'Task 2.4 ➖ Description...',
             'Phase 3 - Task 3.1' (cross-phase reference).
    Returns: (phase_num, task_num).
    """
    id_part = arg.split(" ➖ ", 1)[0].strip()
    # Cross-phase: "Phase X - Task X.Y"
    m = re.match(r"Phase\s+(\d+)\s*-\s*Task\s+(\d+)\.(\d+)", id_part)
    if m:
        return int(m.group(1)), int(m.group(3))
    # Simple: "Task X.Y"
    m = re.match(r"Task\s+(\d+)\.(\d+)", id_part)
    if not m:
        raise PlanError(f"invalid task ref: {arg!r}")
    return int(m.group(1)), int(m.group(2))


def parse_phase_add_arg(arg: str) -> tuple[int, str]:
    """Parse add-phase argument. Returns (phase_num, title).

    If arg matches 'Phase N ➖ Title...', use explicit N.
    Otherwise treat entire arg as the title and return (0, title) for auto-numbering.
    Strips a leading '➖ ' from auto-numbered titles to avoid double delimiters.
    """
    stripped = arg.strip()
    # Match 'Phase N ➖ Title...' — allow empty title after delimiter
    m = re.match(r"^Phase\s+(\d+)\s*➖\s*(.*)$", stripped)
    if m:
        phase_num = int(m.group(1))
        title = m.group(2).strip()
        # If title looks like a repeated Phase ref (e.g. "Phase 2 ➖" with no content),
        # treat it as empty rather than the whole string
        return phase_num, title
    title = stripped
    # Strip leading delimiter if user included it for auto-numbered phase
    if title.startswith("➖ "):
        title = title[2:]
    elif title == "➖":
        title = ""
    return 0, title


def parse_task_add_arg(arg: str) -> tuple[int, int, str]:
    """Parse add-task argument. Returns (phase_num, task_num, title).

    If arg matches 'Task X.Y ➖ Title...', use explicit numbers.
    Otherwise treat entire arg as the title and return (0, 0, title) for auto-numbering.
    Strips a leading '➖ ' from auto-numbered titles to avoid double delimiters.
    """
    stripped = arg.strip()
    # Match 'Task X.Y ➖ Title...' — allow empty title after delimiter
    m = re.match(r"^Task\s+(\d+)\.(\d+)\s*➖\s*(.*)$", stripped)
    if m:
        phase_num = int(m.group(1))
        task_num = int(m.group(2))
        title = m.group(3).strip()
        return phase_num, task_num, title
    title = stripped
    # Strip leading delimiter if user included it for auto-numbered task
    # Handle both "➖ Title" and " ➖ Title" forms
    if title.startswith("➖ "):
        title = title[2:]
    elif title == "➖":
        title = ""
    return 0, 0, title


# ---------------------------------------------------------------------------
# Helpers — title validation
# ---------------------------------------------------------------------------

def validate_title(title: str, label: str = "title") -> str:
    """Validate a title string. Returns stripped title or raises PlanError.

    Checks:
      - Not empty after stripping
      - Contains no newlines (would break line-based file format)
      - Reasonable length (< 2048 chars)
    """
    title = title.strip()
    if not title:
        raise PlanError(f"{label} cannot be empty")
    if "\n" in title or "\r" in title:
        raise PlanError(f"{label} contains newlines — titles must be single-line")
    if len(title) > 2048:
        raise PlanError(f"{label} exceeds maximum length of 2048 characters ({len(title)} chars)")
    return title


# ---------------------------------------------------------------------------
# Helpers — plan title parsing
# ---------------------------------------------------------------------------

_TITLE_RE = re.compile(r"^#\s*(\u2610|\u2753|\u2699\uFE0F|\u274C|\u2611)?\s*Plan\s*➖\s*(.+)$")


def parse_plan_title(line: str) -> tuple[str, str]:
    """Return (emoji, title) from the plan title line."""
    m = _TITLE_RE.match(line.strip())
    if not m:
        raise PlanError(f"invalid plan title line: {line!r}")
    emoji = m.group(1) or STATUS_TODO
    title = m.group(2).strip()
    return emoji, title


def format_plan_title(emoji: str, title: str) -> str:
    """Format plan title line."""
    return f"# {emoji} Plan ➖ {title}"


# ---------------------------------------------------------------------------
# Helpers — phase parsing
# ---------------------------------------------------------------------------

_PHASE_RE = re.compile(r"^##\s*(\u2610|\u2753|\u2699\uFE0F|\u274C|\u2611)?\s*Phase\s+(\d+)\s*➖\s*(.+)$")


def parse_phase_heading(line: str) -> tuple[str, int, str] | None:
    """Return (emoji, phase_number, title) or None."""
    m = _PHASE_RE.match(line.strip())
    if not m:
        return None
    emoji = m.group(1) or STATUS_TODO
    num = int(m.group(2))
    title = m.group(3).strip()
    return emoji, num, title


def format_phase_heading(emoji: str, num: int, title: str) -> str:
    return f"## {emoji} Phase {num} ➖ {title}"


# ---------------------------------------------------------------------------
# Helpers — task parsing
# ---------------------------------------------------------------------------

_TASK_RE = re.compile(
    r"^- (\u2610|\u2753|\u2699\uFE0F|\u274C|\u2611) Task (\d+)\.(\d+)\s*➖\s+(.+)$"
)

# Matches the ⚓ anchor dependency suffix at end of a task title.
# e.g. "Do thing ⚓ Task 2.1 , Task 2.2" → clean="Do thing", deps="Task 2.1 , Task 2.2"
_DEPS_ANCHOR_RE = re.compile(r"^(.+?)\s*⚓\s*(.+)$")

# Matches a single dependency reference: "Task X.Y" or "Phase X - Task X.Y"
_SINGLE_DEP_RE = re.compile(r"(?:Phase\s+\d+\s*-\s*)?Task\s+\d+\.\d+")


def parse_task_deps(raw_title: str) -> tuple[str, list[str]]:
    """Split a task title into (clean_title, [dependency_refs]).

    Handles titles like:
      - "Do thing" → ("Do thing", [])
      - "Do thing ⚓ Task 2.1 , Task 2.2" → ("Do thing", ["Task 2.1", "Task 2.2"])
      - "Do thing ⚓ Phase 3 - Task 3.1" → ("Do thing", ["Phase 3 - Task 3.1"])

    Only treats ⚓ as a dependency anchor if ALL refs after it are valid task
    references. Otherwise the entire string is treated as a plain title.
    """
    m = _DEPS_ANCHOR_RE.match(raw_title.strip())
    if not m:
        return raw_title.strip(), []

    clean = m.group(1).strip()
    deps_str = m.group(2).strip()
    deps = [d.strip() for d in deps_str.split(",")]

    # Only accept as dependencies if ALL refs are valid task references.
    # This avoids false positives when ⚓ appears in description text.
    if not all(_SINGLE_DEP_RE.fullmatch(d) for d in deps):
        return raw_title.strip(), []

    return clean, deps


def format_task_deps(deps: list[str]) -> str:
    """Format dependency refs as ' ⚓ Task A.B , Task C.D' or empty string."""
    if not deps:
        return ""
    return " ⚓ " + " , ".join(deps)


def parse_task_line(line: str) -> tuple[str, int, int, str, list[str]] | None:
    """Return (emoji, phase_num, task_num, clean_title, [deps]) or None.

    clean_title does NOT include the ⚓ anchor suffix.
    deps is a list of dependency references (e.g. ["Task 2.1", "Phase 3 - Task 3.1"]).
    """
    m = _TASK_RE.match(line.strip())
    if not m:
        return None
    emoji = m.group(1)
    phase = int(m.group(2))
    task = int(m.group(3))
    raw_title = m.group(4).strip()
    clean_title, deps = parse_task_deps(raw_title)
    return emoji, phase, task, clean_title, deps


def format_task_line(emoji: str, phase_num: int, task_num: int, title: str, deps: list[str] | None = None) -> str:
    """Format a task line with optional ⚓ dependency anchor.

    title should be the clean title (without ⚓ suffix).
    deps is a list of dependency references.
    """
    suffix = format_task_deps(deps or [])
    return f"- {emoji} Task {phase_num}.{task_num} ➖ {title}{suffix}"


# ---------------------------------------------------------------------------
# Helpers — structure extraction
# ---------------------------------------------------------------------------

def extract_phases(content: str) -> list[tuple[str, int, str, list[tuple[str, int, int, str, list[str]]]]]:
    """Extract all phases with their tasks.

    Returns list of (emoji, phase_num, title, [(emoji, phase, task, clean_title, [deps]), ...]).
    """
    lines = content.splitlines()
    phases: list[tuple[str, int, str, list[tuple[str, int, int, str, list[str]]]]] = []
    current_phase: tuple[str, int, str] | None = None
    current_tasks: list[tuple[str, int, int, str, list[str]]] = []

    for line in lines:
        phase_match = parse_phase_heading(line)
        if phase_match:
            # Save previous phase
            if current_phase is not None:
                phases.append((current_phase[0], current_phase[1], current_phase[2], current_tasks))
            current_phase = phase_match
            current_tasks = []
            continue

        if current_phase is not None:
            task_match = parse_task_line(line)
            if task_match:
                current_tasks.append(task_match)

    # Save last phase
    if current_phase is not None:
        phases.append((current_phase[0], current_phase[1], current_phase[2], current_tasks))

    return phases


def extract_phases_lines(content: str) -> list[tuple[int, int]]:
    """Return list of (start_line, end_line) for each phase section (0-indexed).

    start_line = line with ## Phase heading
    end_line = last line before next ## or EOF
    """
    lines = content.splitlines()
    ranges: list[tuple[int, int]] = []
    phase_starts: list[int] = []

    for i, line in enumerate(lines):
        if parse_phase_heading(line) is not None:
            phase_starts.append(i)

    for idx, start in enumerate(phase_starts):
        end = phase_starts[idx + 1] - 1 if idx + 1 < len(phase_starts) else len(lines) - 1
        ranges.append((start, end))

    return ranges


def _sorted_phase_insert_index(lines: list[str], phase_num: int) -> int:
    """Find the line index where a new phase should be inserted to maintain numeric order.

    Scans for existing ## Phase headings and returns the position just before
    the first phase whose number is >= phase_num, or at the end of all phases
    if no such phase exists.

    The caller should prepend a blank separator line before the new phase heading.
    """
    for i, line in enumerate(lines):
        p = parse_phase_heading(line)
        if p is not None and p[1] >= phase_num:
            return i

    # No phase found with number >= phase_num — insert after last phase section
    last_phase_end = -1
    for i, line in enumerate(lines):
        if parse_phase_heading(line) is not None:
            last_phase_end = i

    if last_phase_end >= 0:
        # Find end of last phase content (tasks + sub-bullets).
        # Skip blank lines that are followed by tasks — the file format
        # uses blank separators between headings and task lists.
        end = last_phase_end + 1
        while end < len(lines):
            if parse_phase_heading(lines[end]) is not None:
                break
            if parse_task_line(lines[end]) is not None:
                # Skip task and its sub-bullets
                end += 1
                while end < len(lines) and lines[end].startswith("  - "):
                    end += 1
            elif lines[end].strip() == "":
                # Blank line — check if tasks follow after it.
                # If yes, keep scanning; if no (checksum/EOF), stop.
                peek = end + 1
                while peek < len(lines) and lines[peek].strip() == "":
                    peek += 1
                if peek < len(lines) and parse_task_line(lines[peek]) is not None:
                    end = peek  # continue scanning from the task
                else:
                    break  # truly trailing blank
            else:
                end += 1
        return end
    else:
        # No phases exist yet — insert after header fields
        for i, line in enumerate(lines):
            if line.startswith("## "):
                return i
        return len(lines)


def _sorted_task_insert_index(lines: list[str], target_phase: int, task_num: int) -> tuple[int | None, str]:
    """Find the line index where a new task should be inserted within its phase.

    Returns (insert_index, error_message). insert_index is None on error.
    Inserts in sorted position relative to existing task numbers in the phase.
    Also accounts for sub-bullets under each task.
    """
    phase_heading_idx = None
    for i, line in enumerate(lines):
        p = parse_phase_heading(line)
        if p and p[1] == target_phase:
            phase_heading_idx = i
            break

    if phase_heading_idx is None:
        return None, f"Phase {target_phase} not found"

    # Collect existing tasks in this phase with their line indices and sub-bullet spans
    task_entries: list[tuple[int, int, int]] = []  # (task_num, task_line_idx, end_of_subbullets_idx)
    j = phase_heading_idx + 1
    while j < len(lines):
        t = parse_task_line(lines[j])
        if t and t[1] == target_phase:
            end = j + 1
            k = end
            # Sub-bullets are indented (start with "  - "), not task lines ("- [emoji] Task")
            while k < len(lines) and lines[k].startswith("  - "):
                k += 1
            task_entries.append((t[2], j, k))
            j = k
        elif parse_phase_heading(lines[j]) is not None:
            break
        else:
            j += 1

    # Find insertion point: first task with number >= task_num
    for idx, (tnum, tline, tend) in enumerate(task_entries):
        if tnum >= task_num:
            return tline, ""

    # Insert after last task's sub-bullets
    if task_entries:
        _, _, last_end = task_entries[-1]
        return last_end, ""
    else:
        # No tasks yet — insert right after phase heading.
        # Preserve any existing blank separator line.
        insert_at = phase_heading_idx + 1
        if insert_at < len(lines) and lines[insert_at].strip() == "":
            insert_at += 1
        # Add blank separator after heading if none exists
        if insert_at == phase_heading_idx + 1:
            lines.insert(insert_at, "")
            insert_at += 1
        return insert_at, ""


def _extract_phase_sections(content: str) -> list[tuple[int, list[str]]]:
    """Extract each phase section as (phase_num, lines).

    Each section includes the ## heading line and all lines until the next
    phase heading or EOF. Leading blank separator lines are included.
    """
    lines = content.splitlines()
    sections: list[tuple[int, list[str]]] = []
    i = 0
    # Skip header (title + bullet fields) — find first ## Phase line
    while i < len(lines) and parse_phase_heading(lines[i]) is None:
        i += 1

    header_lines = lines[:i]

    while i < len(lines):
        p = parse_phase_heading(lines[i])
        if p is None:
            i += 1
            continue

        start = i
        # Include leading blank line if present
        if start > 0 and lines[start - 1].strip() == "" and start - 1 >= len(header_lines):
            start -= 1

        # Find end of this phase section
        j = i + 1
        while j < len(lines) and parse_phase_heading(lines[j]) is None:
            j += 1

        section_lines = lines[start:j]
        sections.append((p[1], section_lines))
        i = j

    return header_lines, sections


# ---------------------------------------------------------------------------
# Status derivation
# ---------------------------------------------------------------------------

def derive_phase_status(tasks: list[tuple[str, int, int, str]], warn: bool = False) -> str:
    """Derive phase emoji from its tasks.

    Rules (matching SKILL.md):
      - Done     — all tasks are ☑
      - Doing    — at least one task is ⚙️
      - Question — no task is ⚙️ or ☑, but at least one is ❓
      - Error    — no task is ⚙️ or ☑, but at least one is ❌
      - Todo     — fallback (e.g., all ☐, or mixed ☑+☐ with no other active status)
    """
    if not tasks:
        if warn:
            print(f"Warning: Phase has zero tasks — it can never reach {STATUS_DONE}", file=sys.stderr)
        return STATUS_TODO

    emojis = {t[0] for t in tasks}

    if all(t[0] == STATUS_DONE for t in tasks):
        return STATUS_DONE
    if STATUS_DOING in emojis:
        return STATUS_DOING
    # Question/Error only when no task is ⚙️ or ☑
    if STATUS_DONE not in emojis and STATUS_QUESTION in emojis:
        return STATUS_QUESTION
    if STATUS_DONE not in emojis and STATUS_ERROR in emojis:
        return STATUS_ERROR
    return STATUS_TODO


def derive_plan_status(phases: list[tuple[str, int, str, list]]) -> str:
    """Derive plan emoji from all phases.

    Rules (matching SKILL.md):
      - Done     — all phases are ☑
      - Doing    — at least one phase is ⚙️
      - Question — no phase is ⚙️ or ☑, but at least one is ❓
      - Error    — no phase is ⚙️ or ☑, but at least one is ❌
      - Todo     — fallback
    """
    if not phases:
        return STATUS_TODO

    # Derive each phase status from its tasks
    phase_statuses = [derive_phase_status(tasks) for _, _, _, tasks in phases]

    if all(s == STATUS_DONE for s in phase_statuses):
        return STATUS_DONE
    if STATUS_DOING in phase_statuses:
        return STATUS_DOING
    # Question/Error only when no phase is ⚙️ or ☑
    if STATUS_DONE not in set(phase_statuses) and STATUS_QUESTION in phase_statuses:
        return STATUS_QUESTION
    if STATUS_DONE not in set(phase_statuses) and STATUS_ERROR in phase_statuses:
        return STATUS_ERROR
    return STATUS_TODO


# ---------------------------------------------------------------------------
# Check / Validate — consistency checker with optional --fix
# ---------------------------------------------------------------------------


def check_plan(plan_path: str, fix: bool = False) -> tuple[int, list[str]]:
    """Check PLAN.md for consistency issues.

    Two-pass approach:
      Pass 1: Collect ALL issues (without modifying content)
      Pass 2 (if fix=True): Apply all auto-fixable changes, write file

    Returns (exit_code, messages) where exit_code is 0 if clean, 1 if issues found.
    In fix mode, exit_code is 0 if all fixable issues were resolved.

    Checks performed:
      1. Checksum integrity
      2. Plan emoji derivation (must match derived status from phases)
      3. Phase emoji derivation (must match derived status from tasks)
      4. Phase numbering — sequential 1,2,3… without gaps or duplicates
      5. Task numbering — within each phase, sequential X.1,X.2,… without gaps/duplicates
      6. Number ordering — phases and tasks appear in ascending numeric order
      7. Dependency references — all ⚓ deps must reference existing tasks
      8. Empty phases — phases with zero tasks (warning)
      9. Duplicate task IDs — no two tasks share the same (phase, task) number
    """
    # Use read_plan_raw so it works in both standalone and batch mode
    # (batch mode intercepts read_plan_raw to use in-memory content)
    try:
        raw = read_plan_raw(plan_path)
    except PlanError:
        raise PlanError(f"{plan_path} does not exist")

    # --- Check 1: Checksum integrity (always fix immediately) ---
    checksum_ok = _verify_checksum(raw)
    checksum_was_fixed = False
    if not checksum_ok:
        if fix:
            body = _strip_checksum(raw)
            fixed = _add_checksum(body)
            write_plan_atomic(plan_path, fixed)
            raw = fixed
            checksum_ok = True
            checksum_was_fixed = True

    content = _strip_checksum(raw)
    lines = content.splitlines()
    phases = extract_phases(content)

    # Build task lookup: (phase_num, task_num) -> emoji
    task_status_map: dict[tuple[int, int], str] = {}
    for _, phase_num, _, tasks in phases:
        for t in tasks:
            task_status_map[(t[1], t[2])] = t[0]

    # ─── PASS 1: Collect all issues ───
    issues: list[tuple[str, bool]] = []  # (message, is_fixable)
    needs_sort = False
    needs_emoji_fix = False
    phase_num_map: dict[int, int] | None = None  # old_num -> new_num
    task_num_maps: dict[int, dict[int, int]] = {}  # phase -> {old_task -> new_task}

    # Checksum issue
    if not checksum_ok:
        issues.append(("checksum: FAILED — stored checksum does not match content (file may be corrupted)", False))

    # --- Check 9: Duplicate task IDs ---
    seen_task_ids: set[tuple[int, int]] = set()
    for _, phase_num, _, tasks in phases:
        for t in tasks:
            key = (t[1], t[2])
            if key in seen_task_ids:
                issues.append((f"duplicate-task-id: Task {key[0]}.{key[1]} appears more than once", False))
            seen_task_ids.add(key)

    # --- Check 4: Phase numbering ---
    phase_nums = [ph[1] for ph in phases]
    expected_phase_nums = list(range(1, len(phases) + 1)) if phases else []
    if phase_nums != expected_phase_nums:
        msg = (f"phase-numbering: got {phase_nums}, expected {expected_phase_nums} "
               f"(phases must be numbered 1..{len(phases)} sequentially)")
        issues.append((msg, True))
        phase_num_map = {}
        for i, old_num in enumerate(phase_nums):
            phase_num_map[old_num] = i + 1

    # --- Check 5: Task numbering within each phase ---
    for emoji, phase_num, title, tasks in phases:
        task_nums = [t[2] for t in tasks]
        expected_task_nums = list(range(1, len(tasks) + 1)) if tasks else []
        if task_nums != expected_task_nums:
            msg = (f"task-numbering: Phase {phase_num} tasks got {task_nums}, "
                   f"expected {expected_task_nums}")
            issues.append((msg, True))
            tmap = {}
            for i, old_t in enumerate(task_nums):
                tmap[old_t] = i + 1
            task_num_maps[phase_num] = tmap

    # --- Check 6: Number ordering ---
    if phase_nums != sorted(phase_nums):
        msg = (f"phase-ordering: phases appear as {phase_nums}, "
               f"expected {sorted(phase_nums)}")
        issues.append((msg, True))
        needs_sort = True

    for emoji, phase_num, title, tasks in phases:
        task_nums_in_order = [t[2] for t in tasks]
        if task_nums_in_order != sorted(task_nums_in_order):
            msg = (f"task-ordering: Phase {phase_num} tasks appear as {task_nums_in_order}, "
                   f"expected {sorted(task_nums_in_order)}")
            issues.append((msg, True))
            needs_sort = True

    # --- Check 7: Dangling dependency references ---
    dangling_deps: list[tuple[int, int, str]] = []  # (phase_num, task_num, dep_ref)
    for _, phase_num, title, tasks in phases:
        for t in tasks:
            for dep_ref in t[4]:
                dp, dt = _resolve_dep_ref(dep_ref, phase_num)
                if dp is None or (dp, dt) not in task_status_map:
                    msg = (f"dangling-dep: Task {t[1]}.{t[2]} depends on {dep_ref!r} "
                           f"which does not exist")
                    issues.append((msg, True))  # fixable — remove dangling ref
                    dangling_deps.append((t[1], t[2], dep_ref))

    # --- Check 8: Empty phases (warning) ---
    for emoji, phase_num, title, tasks in phases:
        if not tasks:
            msg = f"empty-phase: Phase {phase_num} has zero tasks (can never reach {STATUS_DONE})"
            issues.append((msg, False))  # warning, not error

    # --- Check 2: Plan emoji derivation ---
    plan_status_derived = derive_plan_status(phases)
    current_plan_emoji = STATUS_TODO
    for line in lines:
        m = _TITLE_RE.match(line.strip())
        if m:
            current_plan_emoji = m.group(1) or STATUS_TODO
            break
    if current_plan_emoji != plan_status_derived:
        msg = (f"plan-emoji: got {current_plan_emoji} ({_STATUS_LABEL.get(current_plan_emoji, 'unknown')}), "
               f"expected {plan_status_derived} ({_STATUS_LABEL.get(plan_status_derived, 'derived')})")
        issues.append((msg, True))
        needs_emoji_fix = True

    # --- Check 3: Phase emoji derivation ---
    for emoji, phase_num, title, tasks in phases:
        derived = derive_phase_status(tasks)
        if emoji != derived:
            msg = (f"phase-emoji: Phase {phase_num} got {emoji} ({_STATUS_LABEL.get(emoji, 'unknown')}), "
                   f"expected {derived} ({_STATUS_LABEL.get(derived, 'derived')})")
            issues.append((msg, True))
            needs_emoji_fix = True

    # ─── PASS 2: Apply fixes if requested ───
    fixed_issues: list[str] = []
    if checksum_was_fixed:
        fixed_issues.append("checksum: FIXED — recomputed checksum")
    if fix and any(is_fixable for _, is_fixable in issues):
        working = content

        # Fix phase numbering
        if phase_num_map:
            working = _fix_phase_numbering(working, phases, task_status_map)
            fixed_issues.append(f"phase-numbering: FIXED — renumbered to {expected_phase_nums}")

        # Fix task numbering per phase
        for pn, tmap in task_num_maps.items():
            working = _fix_task_numbering(working, pn, task_status_map)
            phases = extract_phases(working)
            task_status_map.clear()
            for _, pnum, _, tasks in phases:
                for t in tasks:
                    task_status_map[(t[1], t[2])] = t[0]
            expected_nums = list(range(1, len([t for _,p,_,ts in phases if p==pn for t in ts]) + 1))
            fixed_issues.append(f"task-numbering: FIXED Phase {pn} — renumbered to {expected_nums}")

        # Fix ordering (sort)
        if needs_sort:
            working = cmd_sort_inline(plan_path, working)
            fixed_issues.append("ordering: FIXED — sorted phases and tasks")
            phases = extract_phases(working)
            task_status_map.clear()
            for _, pnum, _, tasks in phases:
                for t in tasks:
                    task_status_map[(t[1], t[2])] = t[0]

                # Fix dangling dependencies
        if dangling_deps:
            for phase_num, task_num, dep_ref in dangling_deps:
                working = _remove_task_dep(working, phase_num, task_num, dep_ref)
            fixed_issues.append(f"dangling-dep: FIXED — removed {len(dangling_deps)} dangling reference(s)")

        # Fix emoji derivation
        if needs_emoji_fix:
            working = validate_status_set(working)
            fixed_issues.append("emoji-derivation: FIXED — re-derived plan and phase statuses")

        # Write fixed content atomically
        final = _add_checksum(working)
        write_plan_atomic(plan_path, final)

    # ─── Build output messages ───
    messages: list[str] = []
    if not checksum_ok and fix:
        messages.append("checksum: FIXED — recomputed checksum")

    # Report original issues, replacing fixable ones with FIXED messages
    non_fixable_count = 0
    for msg, is_fixable in issues:
        if is_fixable and fix:
            continue  # replaced by fixed_issues below
        if is_fixable and not fix:
            messages.append(msg)
            non_fixable_count += 1
        elif not is_fixable:
            # Warnings (empty-phase) don't count as errors
            if "empty-phase" in msg:
                messages.append(msg)
            else:
                messages.append(msg)
                non_fixable_count += 1

    if fix and fixed_issues:
        for fi in fixed_issues:
            messages.append(fi)

    # Exit code:
    #   non-fix mode: 1 if ANY error exists (except empty-phase warning)
    #   fix mode: 0 if all fixable issues were resolved, 1 if unfixable remain
    has_issues = any(
        "empty-phase" not in msg
        for msg, is_fixable in issues
    )
    has_unfixable_errors = any(
        not is_fixable and "empty-phase" not in msg
        for msg, is_fixable in issues
    )
    if fix:
        exit_code = 1 if has_unfixable_errors else 0
    else:
        exit_code = 1 if has_issues else 0

    return (exit_code, messages)


def _fix_phase_numbering(content: str, phases, task_status_map: dict) -> str:
    """Renumber phases sequentially (1, 2, 3, ...) and update all references.

    Uses position-based mapping so duplicate phase numbers are handled correctly:
    the Nth phase heading in file order always becomes Phase N.
    """
    lines = content.splitlines()

    # Build position-based old_num -> new_num mapping.
    # Each (old_num, new_num) pair corresponds to a phase in file order.
    phase_nums = [p[1] for p in phases]
    num_map_pairs: list[tuple[int, int]] = [(old, i + 1) for i, old in enumerate(phase_nums)]
    # For non-duplicate numbers, build a quick dict lookup
    unique_nums = set(phase_nums)
    simple_map: dict[int, int] = {}
    if len(unique_nums) == len(phase_nums):
        for old, new in num_map_pairs:
            simple_map[old] = new

    changed = False
    new_lines = list(lines)

    # --- Update phase headings (position-based) ---
    heading_idx = 0
    for i, line in enumerate(new_lines):
        p = parse_phase_heading(line)
        if p:
            old_num = p[1]
            if heading_idx < len(num_map_pairs):
                new_num = num_map_pairs[heading_idx][1]
                if old_num != new_num:
                    new_lines[i] = format_phase_heading(p[0], new_num, p[2])
                    changed = True
            heading_idx += 1

    # --- Build context-aware phase mapping for tasks.
    #    Walk lines tracking which phase section each task belongs to. ---
    # For each task line, we need to know its *new* phase number based on
    # which phase heading it falls under (by position, not by old number).
    current_phase_idx = -1
    for i, line in enumerate(new_lines):
        p = parse_phase_heading(line)
        if p:
            current_phase_idx += 1
    # Reset and do the actual update pass
    current_phase_idx = -1
    for i, line in enumerate(new_lines):
        p = parse_phase_heading(line)
        if p:
            current_phase_idx += 1
            continue
        t = parse_task_line(line)
        if t and current_phase_idx >= 0 and current_phase_idx < len(num_map_pairs):
            old_phase = t[1]
            new_phase = num_map_pairs[current_phase_idx][1]
            if old_phase != new_phase:
                new_lines[i] = format_task_line(t[0], new_phase, t[2], t[3], t[4])
                changed = True

    # --- Update dependency references in task lines (position-aware) ---
    current_phase_idx = -1
    for i, line in enumerate(new_lines):
        p = parse_phase_heading(line)
        if p:
            current_phase_idx += 1
            continue
        t = parse_task_line(line)
        if t and current_phase_idx >= 0:
            my_new_phase = num_map_pairs[current_phase_idx][1] if current_phase_idx < len(num_map_pairs) else t[1]
            new_deps = []
            for dep_ref in t[4]:
                dp, dt = _resolve_dep_ref(dep_ref, t[1])
                if dp is not None:
                    # Find new phase number for the dependency's phase
                    new_dp = _find_new_phase_num(dp, num_map_pairs)
                    if new_dp is not None:
                        if new_dp == my_new_phase:
                            new_deps.append(f"Task {new_dp}.{dt}")
                        else:
                            new_deps.append(f"Phase {new_dp} - Task {new_dp}.{dt}")
                    else:
                        new_deps.append(dep_ref)
                else:
                    new_deps.append(dep_ref)
            if new_deps != t[4]:
                new_lines[i] = format_task_line(t[0], my_new_phase, t[2], t[3], new_deps)
                changed = True

    # --- Update header fields referencing phases/tasks ---
    for field in ("Current Phase", "Current Task"):
        idx = _find_header_field_line(new_lines, field)
        if idx >= 0:
            val = new_lines[idx].split(":", 1)[1].strip()
            pm = re.match(r"(.*)Phase\s+(\d+)(.*)", val)
            if pm:
                prefix, old_num_str, suffix = pm.group(1), int(pm.group(2)), pm.group(3)
                new_num = _find_new_phase_num(old_num_str, num_map_pairs)
                if new_num is not None and new_num != old_num_str:
                    new_lines[idx] = f"- {field}: {prefix}{new_num}{suffix}"
                    changed = True

    # Remove self-dependencies created by renumbering.
    current_phase_idx = -1
    for i, line in enumerate(new_lines):
        p = parse_phase_heading(line)
        if p:
            current_phase_idx += 1
            continue
        t = parse_task_line(line)
        if t and current_phase_idx >= 0:
            my_phase = num_map_pairs[current_phase_idx][1] if current_phase_idx < len(num_map_pairs) else t[1]
            my_task = t[2]
            new_deps = [
                d for d in t[4]
                if not _is_self_dep(d, my_phase, my_task)
            ]
            if new_deps != t[4]:
                new_lines[i] = format_task_line(t[0], my_phase, my_task, t[3], new_deps)
                changed = True

    if changed:
        return "\n".join(new_lines)
    return content


def _find_new_phase_num(old_num: int, num_map_pairs: list[tuple[int, int]]) -> int | None:
    """Find the new phase number for a given old phase number.

    If the old number appears only once, returns its unique mapping.
    If it appears multiple times (duplicates), returns the first occurrence's
    new number as a best-effort fallback — exact resolution requires context.
    """
    matches = [new for old, new in num_map_pairs if old == old_num]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        return matches[0]  # Best-effort: use first occurrence
    return None


def _fix_task_numbering(content: str, phase_num: int, task_status_map: dict) -> str:
    """Renumber tasks within a specific phase sequentially (X.1, X.2, ...)."""
    lines = content.splitlines()
    phases = extract_phases(content)

    # Find the phase
    target_tasks = None
    for _, pn, _, tasks in phases:
        if pn == phase_num:
            target_tasks = tasks
            break
    if target_tasks is None:
        return content

    # Build old_task_num -> new_task_num mapping
    old_nums = [t[2] for t in target_tasks]
    num_map: dict[int, int] = {}
    for i, old_num in enumerate(old_nums):
        num_map[old_num] = i + 1

    changed = False
    new_lines = list(lines)

    # Update task lines in this phase
    for i, line in enumerate(new_lines):
        t = parse_task_line(line)
        if t and t[1] == phase_num and t[2] in num_map:
            old_task = t[2]
            new_task = num_map[old_task]
            if old_task != new_task:
                new_lines[i] = format_task_line(t[0], phase_num, new_task, t[3], t[4])
                changed = True

    # Update dependency references pointing to tasks in this phase
    for i, line in enumerate(new_lines):
        t = parse_task_line(line)
        if t:
            new_deps = []
            for dep_ref in t[4]:
                dp, dt = _resolve_dep_ref(dep_ref, t[1])
                if dp is not None and dp == phase_num and dt in num_map:
                    new_dt = num_map[dt]
                    if dp == t[1]:
                        new_deps.append(f"Task {dp}.{new_dt}")
                    else:
                        new_deps.append(f"Phase {dp} - Task {dp}.{new_dt}")
                else:
                    new_deps.append(dep_ref)
            if new_deps != t[4]:
                new_lines[i] = format_task_line(t[0], t[1], t[2], t[3], new_deps)
                changed = True

    # Update header Current Task field if it references a task in this phase
    idx = _find_header_field_line(new_lines, "Current Task")
    if idx >= 0:
        val = new_lines[idx].split(":", 1)[1].strip()
        tm = re.match(r"(.*)Task\s+(\d+)\.(\d+)(.*)", val)
        if tm:
            prefix, p_str, t_str, suffix = tm.group(1), int(tm.group(2)), int(tm.group(3)), tm.group(4)
            if p_str == phase_num and t_str in num_map:
                new_t = num_map[t_str]
                new_lines[idx] = f"- Current Task: {prefix}{phase_num}.{new_t}{suffix}"
                changed = True

    # Remove self-dependencies created by renumbering.
    # After renaming (e.g., Task 1.2 -> Task 1.1), a dep on "Task 1.1" may now
    # point to the task itself. Detect and remove such self-refs.
    for i, line in enumerate(new_lines):
        t = parse_task_line(line)
        if t:
            my_phase, my_task = t[1], t[2]
            new_deps = [
                d for d in t[4]
                if not _is_self_dep(d, my_phase, my_task)
            ]
            if new_deps != t[4]:
                new_lines[i] = format_task_line(t[0], my_phase, my_task, t[3], new_deps)
                changed = True

    if changed:
        return "\n".join(new_lines)
    return content


def cmd_sort_inline(plan_path: str, content: str) -> str:
    """Apply sort transformation in-place (used by check --fix)."""
    # Reuse cmd_sort logic but operate on content string directly
    lines = content.splitlines()

    header_end = 0
    for i, line in enumerate(lines):
        if parse_phase_heading(line) is not None:
            header_end = i
            break
    else:
        return content

    header_lines = lines[:header_end]
    while header_lines and header_lines[-1].strip() == "":
        header_lines.pop()
    phase_block = lines[header_end:]

    last_content_idx = -1
    for i, line in enumerate(phase_block):
        if parse_phase_heading(line) is not None:
            last_content_idx = i
        elif parse_task_line(line) is not None:
            last_content_idx = i
        elif line.startswith("  - "):
            last_content_idx = i
    actual_end = last_content_idx + 1
    while actual_end < len(phase_block) and phase_block[actual_end].strip() == "":
        actual_end += 1

    sections: list[tuple[int, list[str]]] = []
    i = 0
    while i < actual_end:
        p = parse_phase_heading(phase_block[i])
        if p is None:
            i += 1
            continue
        start = i
        j = i + 1
        while j < actual_end and parse_phase_heading(phase_block[j]) is None:
            j += 1
        section_lines = phase_block[start:j]
        sorted_section = _sort_tasks_in_section(section_lines)
        sections.append((p[1], sorted_section))
        i = j

    sections.sort(key=lambda s: s[0])
    sorted_phase_lines = []
    for idx, (_, section) in enumerate(sections):
        sorted_phase_lines.append("")
        sorted_phase_lines.extend(section)

    new_lines = header_lines + sorted_phase_lines
    result = "\n".join(new_lines) + "\n"
    # Touch updated timestamp
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rlines = result.splitlines()
    rlines = _update_header_field(rlines, "Updated", now)
    result = "\n".join(rlines)
    return validate_status_set(result)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_transition(current: str, new: str) -> bool:
    """Check if transition is valid. Returns True if valid."""
    if current == new:
        return True
    allowed = VALID_TRANSITIONS.get(current, set())
    return new in allowed


def check_dependency_cycle(plan_path: str, depends_on: list[str]) -> None:
    """Check for cycles in dependency graph. Raises PlanError if cycle found.

    Walks from each dependency transitively and checks if we can reach back
    to plan_path.

    All dependency paths are resolved relative to CWD — both the initial deps
    from CLI arguments and transitive deps read from other PLAN.md files.
    """
    base_resolved = str(Path(plan_path).resolve())
    visited = set()
    # Resolve initial deps relative to CWD (they come from CLI arguments)
    stack = [str(Path(d).resolve()) for d in depends_on]

    while stack:
        current_resolved = stack.pop()
        if current_resolved == base_resolved:
            raise PlanError(f"dependency cycle detected involving {plan_path}")
        if current_resolved in visited:
            continue
        visited.add(current_resolved)

        # Read the dependency file and follow its own depends_on chain.
        # Stored paths are resolved relative to CWD (same as CLI arguments).
        try:
            dep_content = Path(current_resolved).read_text(encoding="utf-8")
            dep_header = _parse_header("", dep_content.splitlines())
            deps_str = dep_header.get("depends_on", "NONE").strip()
            if deps_str and deps_str != "NONE":
                deps = [d.strip() for d in deps_str.split(",")]
                for d in deps:
                    # Resolve relative to CWD (paths are always CWD-relative)
                    resolved_d = str(Path(d).resolve())
                    stack.append(resolved_d)
        except (FileNotFoundError, SystemExit, PermissionError):
            pass  # plan doesn't exist, skip


def _remove_task_dep(content: str, phase_num: int, task_num: int, dep_ref: str) -> str:
    """Remove a specific dependency reference from a task line.

    Finds the task by (phase_num, task_num) and removes `dep_ref` from its
    ⚓ dependency list. Uses existing parse/format helpers for correctness.
    Returns updated content.
    """
    lines = content.splitlines()
    in_phase = False
    current_phase_num = 0

    for i, line in enumerate(lines):
        # Track which phase we're in
        ph = parse_phase_heading(line)
        if ph:
            in_phase = True
            current_phase_num = ph[1]
            continue

        # Look for the target task line
        if not in_phase or current_phase_num != phase_num:
            continue

        parsed = parse_task_line(line)
        if not parsed:
            continue

        emoji, t_phase, t_num, clean_title, deps = parsed
        if t_phase != phase_num or t_num != task_num:
            continue

        # Found the task — remove the dependency
        new_deps = [d for d in deps if d.strip() != dep_ref.strip()]
        lines[i] = format_task_line(emoji, phase_num, task_num, clean_title, new_deps)
        return "\n".join(lines)

    return content  # task not found, return unchanged


def validate_status_set(content: str) -> str:
    """Re-derive all phase and plan statuses from tasks. Returns updated content."""
    lines = content.splitlines()
    phases = extract_phases("\n".join(lines))

    # Update phase headings with derived statuses
    for emoji, num, title, tasks in phases:
        derived = derive_phase_status(tasks)
        old_heading = format_phase_heading(emoji, num, title)
        new_heading = format_phase_heading(derived, num, title)
        for i, line in enumerate(lines):
            if line.strip() == old_heading:
                lines[i] = new_heading
                break

    # Update plan title with derived status
    plan_status = derive_plan_status(phases)
    for i, line in enumerate(lines):
        m = _TITLE_RE.match(line.strip())
        if m:
            title_text = m.group(2).strip()
            lines[i] = format_plan_title(plan_status, title_text)
            break

    return "\n".join(lines)


def check_task_deps_satisfied(content: str, task_phase: int, task_num: int) -> bool:
    """Check if all dependencies of a task are in ☑ (Done) state.

    Returns True if satisfied (no deps or all deps are ☑), False otherwise.
    """
    lines = content.splitlines()
    phases = extract_phases("\n".join(lines))

    # Build a lookup: (phase, task) -> emoji
    task_status_map: dict[tuple[int, int], str] = {}
    for _, phase_num, _, tasks in phases:
        for t in tasks:
            task_status_map[(t[1], t[2])] = t[0]

    # Find the target task and its deps
    for _, phase_num, _, tasks in phases:
        for t in tasks:
            if t[1] == task_phase and t[2] == task_num:
                deps = t[4]  # list of dep refs like "Task 2.1" or "Phase 3 - Task 3.1"
                if not deps:
                    return True
                for dep_ref in deps:
                    dep_phase, dep_task = _resolve_dep_ref(dep_ref, task_phase)
                    if dep_phase is None:
                        continue  # malformed ref, skip
                    dep_status = task_status_map.get((dep_phase, dep_task))
                    if dep_status != STATUS_DONE:
                        return False
                return True

    return True  # task not found, let caller handle error


def _resolve_dep_ref(dep_ref: str, current_phase: int) -> tuple[int | None, int | None]:
    """Resolve a dependency reference to (phase_num, task_num).

    Handles:
      - "Task X.Y" → (X, Y)
      - "Phase X - Task X.Y" → (X, Y)
    """
    dep_ref = dep_ref.strip()
    # Cross-phase: "Phase X - Task X.Y"
    m = re.match(r"Phase\s+(\d+)\s*-\s*Task\s+(\d+)\.(\d+)", dep_ref)
    if m:
        return int(m.group(1)), int(m.group(3))
    # Same-phase or explicit: "Task X.Y"
    m = re.match(r"Task\s+(\d+)\.(\d+)", dep_ref)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


def _is_self_dep(dep_ref: str, my_phase: int, my_task: int) -> bool:
    """Check if a dependency reference points to the task itself."""
    dp, dt = _resolve_dep_ref(dep_ref, my_phase)
    if dp is None:
        return False
    return dp == my_phase and dt == my_task


# ---------------------------------------------------------------------------
# Commands — batch (chain multiple ops under one lock)
# ---------------------------------------------------------------------------

# Maps a batch command name to the positional attribute names expected by cmd_*. 
# These match the argparse subparser definitions in build_parser().
_BATCH_CMD_ATTRS: dict[str, list[str]] = {
    "create": ["title"],
    "add-phase": ["phase_ref", "phase_title"],
    "add-task": ["phase_ref", "task_ref", "task_title"],
    "remove-phase": ["phase_ref"],
    "remove-task": ["phase_ref", "task_ref"],
    "set-plan-title": ["title"],
    "set-plan-depends-on": ["deps_raw"],
    "set-plan-created": ["value"],
    "set-plan-updated": ["value"],
    "set-plan-current-phase": ["phase_ref"],
    "set-plan-current-task": ["task_ref"],
    "set-plan-status": ["status"],
    "set-phase-status": ["phase_ref", "status"],
    "set-task-status": ["task_ref", "status"],
    "update-phase": ["phase_ref", "phase_title"],
    "update-task": ["phase_ref", "task_ref", "task_title"],
    "add-task-dependency": ["phase_ref", "task_ref", "dep_task_ref"],
    "remove-task-dependency": ["phase_ref", "task_ref", "dep_task_ref"],
    "set-all-statuses": ["status"],
    "sort": [],
    "check": [],
}


def _parse_batch_line(line: str) -> tuple[str, list[str]] | None:
    """Parse a batch input line into (command_name, [args...]).

    Uses shlex for proper shell-style quoting support.
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    try:
        tokens = shlex.split(line)
    except ValueError as e:
        raise PlanError(f"cannot parse line: {e}")
    if not tokens:
        return None
    cmd_name = tokens[0]
    if cmd_name not in _BATCH_CMD_ATTRS:
        raise PlanError(f"unrecognized command: {cmd_name!r}")
    return cmd_name, tokens[1:]


def _parse_batch_json(raw: str) -> list[tuple[str, list[str]]]:
    """Parse a JSON array of command objects into [(cmd_name, [args...])].

    Expected format:
      [
        {"command": "create", "args": ["My Project"]},
        {"command": "add-phase", "args": ["Phase 1", "Planning"]},
        {"command": "add-task", "args": ["Phase 1", "Task 1.1", "Define scope"]},
        ...
      ]
    """
    try:
        data = _json_mod.loads(raw)
    except _json_mod.JSONDecodeError as e:
        raise PlanError(f"invalid JSON: {e}")

    if not isinstance(data, list):
        raise PlanError("JSON input must be an array of command objects")

    operations = []
    for idx, obj in enumerate(data):
        if not isinstance(obj, dict):
            raise PlanError(f"item {idx} is not an object")
        cmd_name = obj.get("command")
        if not cmd_name:
            raise PlanError(f"item {idx} missing 'command' key")
        if cmd_name not in _BATCH_CMD_ATTRS:
            raise PlanError(f"unrecognized command: {cmd_name!r}")
        args = obj.get("args", [])
        if not isinstance(args, list):
            raise PlanError(f"'args' for item {idx} must be an array")
        # Ensure all args are strings
        str_args = [str(a) for a in args]
        operations.append((cmd_name, str_args))
    return operations


def _make_namespace(cmd_name: str, args: list[str], path: str) -> argparse.Namespace:
    """Build an argparse.Namespace from batch-parsed command + positional args."""
    d = {"path": path}
    attr_names = _BATCH_CMD_ATTRS.get(cmd_name, [])
    # Optional title fields: None when not provided (matches argparse nargs="?" default)
    _OPTIONAL_TITLE_FIELDS = {"phase_title", "task_title"}
    for i, name in enumerate(attr_names):
        if i < len(args):
            val = args[i]
        elif name in _OPTIONAL_TITLE_FIELDS:
            val = None  # Missing optional title → None (legacy form)
        else:
            val = ""
        if name == "value" and val == "":
            val = "__NOW__"
        if name == "deps_raw":
            d["deps"] = [x.strip() for x in val.split(",") if x.strip()] if val != "NONE" else []
        else:
            d[name] = val
    return argparse.Namespace(**d)


def _mark_failed_task_error(content: str, ns: argparse.Namespace) -> str:
    """Mark a task as ❌ (Error) when set-task-status fails in batch mode.

    Returns modified content so PLAN.md reflects what actually happened.
    Only sets to ERROR if the current status allows it (always valid from ☐, ⚙️, ❓).
    """
    task_ref = getattr(ns, "task_ref", None)
    if not task_ref:
        return content

    target_phase, target_task = parse_task_arg(task_ref)
    lines = content.splitlines()
    for i, line in enumerate(lines):
        t = parse_task_line(line)
        if t and t[1] == target_phase and t[2] == target_task:
            current_status = t[0]
            # ERROR is reachable from TODO, DOING, QUESTION — never from DONE
            if current_status != STATUS_DONE:
                lines[i] = format_task_line(STATUS_ERROR, t[1], t[2], t[3], t[4])
            break
    return "\n".join(lines)


def cmd_batch(args: argparse.Namespace) -> dict:
    """Execute multiple plan operations on the same PLAN.md under one lock.

    Reads commands from stdin or a file (--input FILE). Two input modes:

    1. Line mode: one command per line, shell-style quoting:
        create "My Project"
        add-phase "Phase 1 ➖ Planning"
        add-task "Phase 1" "Task 1.1 ➖ Define scope"

    2. JSON mode: array of objects with {"command": ..., "args": [...]}:
        [{"command": "create", "args": ["My Project"]}, ...]

    Mode detection:
      - --json flag forces JSON mode
      - File extension: .json → JSON mode, .txt/.md → line mode
      - Stdin without --json: line mode (default)

    All operations share a single exclusive lock and atomic write at the end.
    On error, remaining steps are marked as "skipped" and not executed.
    Output is a JSON object with "status" and "results" array.
    """
    path = args.path
    input_file = getattr(args, "input", None)
    json_flag = getattr(args, "json", False)

    # Read raw content from file or stdin
    if input_file:
        p = Path(input_file)
        if not p.exists():
            raise PlanError(f"input file {input_file} does not exist")
        raw = p.read_text(encoding="utf-8").strip()
    else:
        raw = sys.stdin.read().strip()

    if not raw:
        src = input_file or "stdin"
        raise PlanError(f"no commands provided in {src}")

    # Determine mode: --json flag wins, then auto-detect from file extension
    json_mode = json_flag
    if not json_flag and input_file:
        suffix = Path(input_file).suffix.lower()
        if suffix == ".json":
            json_mode = True
        elif suffix in (".txt", ".md"):
            json_mode = False

    # Parse input — JSON mode or line mode
    if json_mode:
        operations = _parse_batch_json(raw)
    else:
        operations = []
        for line in raw.splitlines():
            result = _parse_batch_line(line)
            if result is None:
                continue
            operations.append(result)

    if not operations:
        raise PlanError("no valid commands found")

    # If file doesn't exist, first command MUST be 'create'.
    # This prevents malformed files (mutations on empty content) and
    # silent data loss when create is not first.
    if not Path(path).exists():
        first_cmd = operations[0][0]
        if first_cmd != "create":
            raise PlanError(
                f"file {path} does not exist — first batch command must be 'create'",
            )

    # Results list for JSON output
    results: list[dict] = []
    hit_error = False

    # Hold exclusive lock for the entire batch
    fd = _acquire_exclusive_lock(path)
    try:
        # Clean orphans
        _cleanup_orphans(path)

        # If file doesn't exist, create empty content (create cmd will handle it)
        if Path(path).exists():
            raw_content = read_plan_raw(path)
            if not _verify_checksum(raw_content):
                pass  # warning logged by caller
            content = _strip_checksum(raw_content)
        else:
            content = ""

        for cmd_name, op_args in operations:
            # If we already hit an error, skip remaining steps
            if hit_error:
                results.append(_result("skipped", cmd_name,
                                        "skipped — previous step failed"))
                continue

            ns = _make_namespace(cmd_name, op_args, path)

            if cmd_name == "create":
                # create is special — it writes directly without _safe_edit
                now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                deps_str = "NONE"
                content = f"""# {STATUS_TODO} Plan ➖ {ns.title}
- Depends On: {deps_str}
- Created: {now}
- Updated: {now}
- Current Phase: NONE
- Current Task: NONE
"""
                results.append(_result("success", "create",
                                        f"Created {path}", path=path))
                continue

            # For all other commands, call the transform directly
            handler = COMMAND_MAP.get(cmd_name)
            if handler is None:
                results.append(_result("error", cmd_name,
                                        f"unknown command {cmd_name!r}"))
                hit_error = True
                continue

            # Wrap handler to apply its transform in-place instead of via _safe_edit.
            # Each cmd_* function calls _safe_edit(path, transform_fn) internally.
            # Some also pre-read via read_plan() / read_plan_raw().
            # We intercept all three so they operate on in-memory content.
            original_safe_edit = globals()["_safe_edit"]
            original_read_plan = globals()["read_plan"]
            original_read_plan_raw = globals()["read_plan_raw"]

            def _inline_edit(_p: str, transform_fn) -> str:
                nonlocal content
                content = transform_fn(content)
                return content

            def _inline_read_plan(_p: str) -> str:
                return content

            def _inline_read_plan_raw(_p: str) -> str:
                # Return content with a dummy checksum so _verify_checksum passes
                return _add_checksum(content)

            globals()["_safe_edit"] = _inline_edit
            globals()["read_plan"] = _inline_read_plan
            globals()["read_plan_raw"] = _inline_read_plan_raw

            try:
                res = handler(ns)
                # Handler now returns a dict result
                if isinstance(res, dict):
                    results.append(res)
                    if res.get("status") == "error":
                        # If set-task-status failed, mark the task as ❌ (Error)
                        # so PLAN.md reflects what actually happened
                        if cmd_name == "set-task-status" and not hit_error:
                            content = _mark_failed_task_error(content, ns)
                        hit_error = True
                else:
                    # Fallback for legacy handlers that don't return dicts
                    results.append(_result("success", cmd_name, ""))
            except PlanError as e:
                results.append(_result("error", cmd_name, str(e)))
                # If set-task-status failed, mark the task as ❌ (Error)
                if cmd_name == "set-task-status" and not hit_error:
                    content = _mark_failed_task_error(content, ns)
                hit_error = True
            except Exception as e:
                results.append(_result("error", cmd_name, f"unexpected error: {e}"))
                hit_error = True
            finally:
                globals()["_safe_edit"] = original_safe_edit
                globals()["read_plan"] = original_read_plan
                globals()["read_plan_raw"] = original_read_plan_raw

        # Always write PLAN.md — successful mutations are preserved.
        # On error, the failed task is marked ❌ and remaining steps skipped.
        content = _touch_updated(path, content)
        content = validate_status_set(content)

        # Atomic write
        final_content = _add_checksum(content)
        write_plan_atomic(path, final_content)

    finally:
        _release_lock(fd, path)

    # Determine overall status and count results
    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = sum(1 for r in results if r["status"] == "error")
    skipped_count = sum(1 for r in results if r["status"] == "skipped")

    if hit_error:
        overall_status = "error"
        msg = (f"Batch applied {success_count}/{len(operations)} operations to {path} "
                f"({error_count} error(s), {skipped_count} skipped)")
    elif any(r["status"] == "warning" for r in results):
        overall_status = "warning"
        msg = f"Batch complete: {len(operations)} operations applied to {path}"
    else:
        overall_status = "success"
        msg = f"Batch complete: {len(operations)} operations applied to {path}"

    return _result(overall_status, "batch", msg, path=path, results=results)


# ---------------------------------------------------------------------------
# Commands — create
# ---------------------------------------------------------------------------

def cmd_create(args: argparse.Namespace) -> dict:
    """Create a new PLAN.md with header."""
    path = args.path
    title = validate_title(args.title, "plan title")
    depends = getattr(args, "depends", []) or []

    if Path(path).exists():
        raise PlanError(f"{path} already exists")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    deps_str = "NONE"
    if depends:
        deps_str = " , ".join(depends)

    content = f"""# {STATUS_TODO} Plan ➖ {title}
- Depends On: {deps_str}
- Created: {now}
- Updated: {now}
- Current Phase: NONE
- Current Task: NONE
"""
    # Check for dependency cycles before writing
    if depends:
        check_dependency_cycle(path, depends)

    # Atomically write the new file (no lock needed — file doesn't exist yet)
    final = _add_checksum(content)
    write_plan_atomic(path, final)
    return _result("success", "create", f"Created {path}", path=path)


# ---------------------------------------------------------------------------
# Commands — get (header reads)
# ---------------------------------------------------------------------------

def cmd_get_plan_title(args: argparse.Namespace) -> dict:
    content = _safe_read(args.path)
    lines = content.splitlines()
    for line in lines:
        m = _TITLE_RE.match(line.strip())
        if m:
            return _result("success", "get-plan-title", m.group(2).strip(), value=m.group(2).strip())
    raise PlanError("no plan title found")


def cmd_get_plan_depends_on(args: argparse.Namespace) -> dict:
    content = _safe_read(args.path)
    header = _parse_header("", content.splitlines())
    val = header.get("depends_on", "NONE")
    return _result("success", "get-plan-depends-on", val, value=val)


def cmd_get_plan_created(args: argparse.Namespace) -> dict:
    content = _safe_read(args.path)
    header = _parse_header("", content.splitlines())
    val = header.get("created", "")
    return _result("success", "get-plan-created", val, value=val)


def cmd_get_plan_updated(args: argparse.Namespace) -> dict:
    content = _safe_read(args.path)
    header = _parse_header("", content.splitlines())
    val = header.get("updated", "")
    return _result("success", "get-plan-updated", val, value=val)


def cmd_get_plan_current_phase(args: argparse.Namespace) -> dict:
    content = _safe_read(args.path)
    header = _parse_header("", content.splitlines())
    val = header.get("current_phase", "NONE")
    return _result("success", "get-plan-current-phase", val, value=val)


def cmd_get_plan_current_task(args: argparse.Namespace) -> dict:
    content = _safe_read(args.path)
    header = _parse_header("", content.splitlines())
    val = header.get("current_task", "NONE")
    return _result("success", "get-plan-current-task", val, value=val)


# ---------------------------------------------------------------------------
# Commands — set (header writes)
# ---------------------------------------------------------------------------

def _touch_updated(path: str, content: str) -> str:
    """Update the Updated timestamp in content."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = content.splitlines()
    return "\n".join(_update_header_field(lines, "Updated", now))


def cmd_set_plan_title(args: argparse.Namespace) -> dict:
    def _transform(content: str) -> str:
        lines = content.splitlines()
        new_title = args.title
        for i, line in enumerate(lines):
            m = _TITLE_RE.match(line.strip())
            if m:
                current_emoji = m.group(1) or STATUS_TODO
                lines[i] = format_plan_title(current_emoji, new_title)
                break
        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        content = validate_status_set(content)
        return content

    _safe_edit(args.path, _transform)
    return _result("success", "set-plan-title", f"Set plan title to: {args.title}")


def cmd_set_plan_depends_on(args: argparse.Namespace) -> dict:
    deps = getattr(args, "deps", []) or []
    deps_str = "NONE" if not deps else " , ".join(deps)

    # Check for cycles before writing
    if deps:
        check_dependency_cycle(args.path, deps)

    def _transform(content: str) -> str:
        lines = content.splitlines()
        lines = _update_header_field(lines, "Depends On", deps_str)
        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        return content

    _safe_edit(args.path, _transform)
    return _result("success", "set-plan-depends-on", f"Set depends on to: {deps_str}")


def cmd_set_plan_created(args: argparse.Namespace) -> dict:
    val = args.value
    if val in ("--now", "__NOW__"):
        val = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _transform(content: str) -> str:
        lines = content.splitlines()
        lines = _update_header_field(lines, "Created", val)
        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        return content

    _safe_edit(args.path, _transform)
    return _result("success", "set-plan-created", f"Set created to: {val}")


def cmd_set_plan_updated(args: argparse.Namespace) -> dict:
    val = args.value
    if val in ("--now", "__NOW__"):
        val = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _transform(content: str) -> str:
        lines = content.splitlines()
        lines = _update_header_field(lines, "Updated", val)
        content = "\n".join(lines)
        return content

    _safe_edit(args.path, _transform)
    return _result("success", "set-plan-updated", f"Set updated to: {val}")


def cmd_set_plan_current_phase(args: argparse.Namespace) -> dict:
    phase_ref = args.phase_ref  # e.g. "Phase 2" or "Phase 2 - Description..."
    target = parse_phase_arg(phase_ref)

    def _transform(content: str) -> str:
        lines = content.splitlines()

        # Find the phase and copy its emoji + full heading
        target_text = None
        for line in lines:
            m = parse_phase_heading(line)
            if m:
                emoji, num, title = m
                if num == target:
                    target_text = f"{emoji} Phase {num}"
                    break

        if target_text is None:
            raise PlanError(f"{phase_ref} not found")

        lines = _update_header_field(lines, "Current Phase", target_text)
        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        return content

    # Resolve target_text before locking for the result message
    existing = read_plan(args.path)
    target_text = None
    for line in existing.splitlines():
        m = parse_phase_heading(line)
        if m and m[1] == target:
            target_text = f"{m[0]} Phase {m[1]}"
            break
    if target_text is None:
        raise PlanError(f"{phase_ref} not found")

    _safe_edit(args.path, _transform)
    return _result("success", "set-plan-current-phase", f"Set current phase to: {target_text}")


def cmd_set_plan_current_task(args: argparse.Namespace) -> dict:
    task_ref = args.task_ref  # e.g. "Task 2.3" or "Task 2.3 - Description..."
    target_phase, target_task = parse_task_arg(task_ref)

    def _transform(content: str) -> str:
        lines = content.splitlines()

        # Find the task and copy its emoji + full reference
        target_text = None
        for line in lines:
            t = parse_task_line(line)
            if t and t[1] == target_phase and t[2] == target_task:
                target_text = f"{t[0]} Task {target_phase}.{target_task}"
                break

        if target_text is None:
            raise PlanError(f"{task_ref} not found")

        lines = _update_header_field(lines, "Current Task", target_text)
        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        return content

    # Resolve target_text before locking for the result message
    existing = read_plan(args.path)
    target_text = None
    for line in existing.splitlines():
        t = parse_task_line(line)
        if t and t[1] == target_phase and t[2] == target_task:
            target_text = f"{t[0]} Task {target_phase}.{target_task}"
            break
    if target_text is None:
        raise PlanError(f"{task_ref} not found")

    _safe_edit(args.path, _transform)
    return _result("success", "set-plan-current-task", f"Set current task to: {target_text}")


# ---------------------------------------------------------------------------
# Commands — status reads
# ---------------------------------------------------------------------------

def cmd_get_plan_status(args: argparse.Namespace) -> dict:
    content = _safe_read(args.path)
    lines = content.splitlines()
    for line in lines:
        m = _TITLE_RE.match(line.strip())
        if m:
            val = m.group(1) or STATUS_TODO
            return _result("success", "get-plan-status", val, value=val)
    return _result("success", "get-plan-status", STATUS_TODO, value=STATUS_TODO)


def cmd_get_phase_status(args: argparse.Namespace) -> dict:
    content = _safe_read(args.path)
    phase_ref = args.phase_ref  # e.g. "Phase 2" or "Phase 2 - Description..."
    lines = content.splitlines()
    target = parse_phase_arg(phase_ref)

    for line in lines:
        p = parse_phase_heading(line)
        if p and p[1] == target:
            return _result("success", "get-phase-status", p[0], value=p[0])
    raise PlanError(f"{phase_ref} not found")


def cmd_get_task_status(args: argparse.Namespace) -> dict:
    content = _safe_read(args.path)
    task_ref = args.task_ref  # e.g. "Task 2.3" or "Task 2.3 - Description..."
    lines = content.splitlines()
    target_phase, target_task = parse_task_arg(task_ref)

    for line in lines:
        t = parse_task_line(line)
        if t and t[1] == target_phase and t[2] == target_task:
            return _result("success", "get-task-status", t[0], value=t[0])
    raise PlanError(f"{task_ref} not found")


# ---------------------------------------------------------------------------
# Commands — status writes
# ---------------------------------------------------------------------------

def cmd_set_all_statuses(args: argparse.Namespace) -> dict:
    """Set plan, all phases, and all tasks to the same status."""
    new_status = args.status

    if new_status not in ALL_STATUSES:
        raise PlanError(f"invalid status {new_status!r}")

    def _transform(content: str) -> str:
        lines = content.splitlines()

        # Update plan title
        for i, line in enumerate(lines):
            m = _TITLE_RE.match(line.strip())
            if m:
                title_text = m.group(2).strip()
                lines[i] = format_plan_title(new_status, title_text)
                break

        # Update all phase headings
        for i, line in enumerate(lines):
            p = parse_phase_heading(line)
            if p:
                lines[i] = format_phase_heading(new_status, p[1], p[2])

        # Update all tasks
        for i, line in enumerate(lines):
            t = parse_task_line(line)
            if t:
                lines[i] = format_task_line(new_status, t[1], t[2], t[3], t[4])

        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        return content

    _safe_edit(args.path, _transform)
    return _result("success", "set-all-statuses", f"Set all statuses to: {new_status}")


def cmd_set_plan_status(args: argparse.Namespace) -> dict:
    """Set plan status (emoji in title).

    Uses plan-specific transitions that allow ❓→❌:
    during scope clarification a critical blocker may be discovered
    that makes the plan unactionable.
    """
    new_status = args.status

    if new_status not in ALL_STATUSES:
        raise PlanError(f"invalid status {new_status!r}")

    def _transform(content: str) -> str:
        lines = content.splitlines()
        current_emoji = STATUS_TODO
        for i, line in enumerate(lines):
            m = _TITLE_RE.match(line.strip())
            if m:
                current_emoji = m.group(1) or STATUS_TODO
                title_text = m.group(2).strip()

                # Validate plan-level transition
                allowed = PLAN_TRANSITIONS.get(current_emoji, set())
                if new_status != current_emoji and new_status not in allowed:
                    raise PlanError(
                        f"invalid transition {current_emoji} -> {new_status} for plan",
                    )

                lines[i] = format_plan_title(new_status, title_text)
                break

        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        return content

    _safe_edit(args.path, _transform)
    return _result("success", "set-plan-status", f"Set plan status to: {new_status}")


def cmd_set_phase_status(args: argparse.Namespace) -> dict:
    """Set phase status (emoji in heading)."""
    phase_ref = args.phase_ref  # e.g. "Phase 2" or "Phase 2 - Description..."
    new_status = args.status

    if new_status not in ALL_STATUSES:
        raise PlanError(f"invalid status {new_status!r}")

    target = parse_phase_arg(phase_ref)

    def _transform(content: str) -> str:
        lines = content.splitlines()
        for i, line in enumerate(lines):
            p = parse_phase_heading(line)
            if p and p[1] == target:
                # Validate transition
                if not validate_transition(p[0], new_status):
                    raise PlanError(
                        f"invalid transition {p[0]} -> {new_status} for {phase_ref}",
                    )
                lines[i] = format_phase_heading(new_status, p[1], p[2])
                break
        else:
            raise PlanError(f"{phase_ref} not found")

        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        return content

    _safe_edit(args.path, _transform)
    return _result("success", "set-phase-status", f"Set {phase_ref} status to: {new_status}")


def cmd_set_task_status(args: argparse.Namespace) -> dict:
    """Set task status (emoji in task line)."""
    task_ref = args.task_ref  # e.g. "Task 2.3" or "Task 2.3 - Description..."
    new_status = args.status

    if new_status not in ALL_STATUSES:
        raise PlanError(f"invalid status {new_status!r}")

    target_phase, target_task = parse_task_arg(task_ref)

    def _transform(content: str) -> str:
        lines = content.splitlines()
        for i, line in enumerate(lines):
            t = parse_task_line(line)
            if t and t[1] == target_phase and t[2] == target_task:
                # Validate transition
                if not validate_transition(t[0], new_status):
                    raise PlanError(
                        f"invalid transition {t[0]} -> {new_status} for {task_ref}",
                    )
                # Check dependency satisfaction before transitioning to ⚙️ (Doing)
                if new_status == STATUS_DOING:
                    if not check_task_deps_satisfied(content, target_phase, target_task):
                        raise PlanError(
                            f"cannot start {task_ref} — dependencies not satisfied (all deps must be {STATUS_DONE})",
                        )
                lines[i] = format_task_line(new_status, t[1], t[2], t[3], t[4])
                break
        else:
            raise PlanError(f"{task_ref} not found")

        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        # Re-derive phase and plan statuses
        content = validate_status_set(content)
        return content

    _safe_edit(args.path, _transform)
    return _result("success", "set-task-status", f"Set {task_ref} status to: {new_status}")


# ---------------------------------------------------------------------------
# Commands — Phase CRUD
# ---------------------------------------------------------------------------

def cmd_add_phase(args: argparse.Namespace) -> dict:
    """Add a new phase, inserted in sorted numeric position.

    Accepts two forms:
      1. Separate args: add-phase PLAN.md "Phase 2" "Planning & Requirements"
      2. Legacy combined: add-phase PLAN.md "Phase 2 ➖ Planning & Requirements"
         (when phase_title is None, phase_ref carries the full combined string)
    """
    phase_ref = args.phase_ref
    phase_title_arg = args.phase_title

    # Determine explicit_num and title from arguments
    # None (missing arg) → legacy form; empty string → new form (rejected by validate_title)
    if phase_title_arg is not None:
        # New form: separate ID + title
        explicit_num = parse_phase_arg(phase_ref) if "Phase" in phase_ref else 0
        raw_title = phase_title_arg
    else:
        # Legacy form: combined string in phase_ref (e.g. "Phase 2 ➖ Desc")
        explicit_num, raw_title = parse_phase_add_arg(phase_ref)

    title = validate_title(raw_title, "phase title")

    def _transform(content: str) -> str:
        lines = content.splitlines()
        phases = extract_phases(content)

        nonlocal explicit_num
        if explicit_num > 0:
            phase_num = explicit_num
        else:
            phase_num = len(phases) + 1

        # Build new phase section (leading blank + heading + trailing blank)
        new_phase_lines = [
            "",
            format_phase_heading(STATUS_TODO, phase_num, title),
            "",
        ]

        # Find insertion point, collapse adjacent blank lines into one separator
        insert_idx = _sorted_phase_insert_index(lines, phase_num)
        # Strip trailing blanks before insertion (replaced by our leading blank)
        while insert_idx > 0 and lines[insert_idx - 1].strip() == "":
            insert_idx -= 1
        # Strip leading blanks from what follows (replaced by our trailing blank)
        end_idx = insert_idx
        while end_idx < len(lines) and lines[end_idx].strip() == "":
            end_idx += 1
        lines = lines[:insert_idx] + new_phase_lines + lines[end_idx:]

        content = "\n".join(lines) + "\n"
        content = _touch_updated(args.path, content)
        return content

    # For explicit numbers, we know phase_num ahead of time.
    # For auto-numbering, read current phase count to report accurately.
    if explicit_num > 0:
        phase_num = explicit_num
    else:
        existing = read_plan(args.path)
        phase_num = len(extract_phases(existing)) + 1

    _safe_edit(args.path, _transform)
    return _result("success", "add-phase",
                    f"Added Phase {phase_num} ({title}) with status {STATUS_TODO}",
                    phase_id=f"Phase {phase_num}")


def cmd_update_phase(args: argparse.Namespace) -> dict:
    """Update phase description/title.

    Accepts two forms:
      1. Separate args: update-phase PLAN.md "Phase 2" "New description"
      2. Legacy combined: update-phase PLAN.md "Phase 2 ➖ New description"
         (when phase_title is None, phase_ref carries the full combined string)
    """
    phase_ref = args.phase_ref
    phase_title_arg = args.phase_title

    # Empty string (from batch mode) treated as None → legacy form
    if phase_title_arg:
        # New form: separate ID + title
        target = parse_phase_arg(phase_ref)
        new_description = validate_title(phase_title_arg, "phase title")
    else:
        # Legacy form: combined string in phase_ref (e.g. "Phase 2 ➖ New desc")
        target = parse_phase_arg(phase_ref)
        new_description = phase_ref.split(" ➖ ", 1)[-1].strip() if " ➖ " in phase_ref else None
        if new_description is not None:
            new_description = validate_title(new_description, "phase title")

    def _transform(content: str) -> str:
        lines = content.splitlines()

        # Verify phase exists
        found = False
        for line in lines:
            p = parse_phase_heading(line)
            if p and p[1] == target:
                found = True
                break

        if not found:
            raise PlanError(f"Phase {target} not found")

        # Replace the phase heading line's title
        for i, line in enumerate(lines):
            p = parse_phase_heading(line)
            if p and p[1] == target:
                current_emoji = p[0]
                title_to_use = new_description if new_description else p[2]
                lines[i] = format_phase_heading(current_emoji, target, title_to_use)
                break

        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        content = validate_status_set(content)
        return content

    _safe_edit(args.path, _transform)
    return _result("success", "update-phase",
                    f"Updated Phase {target} description to: {new_description if new_description else 'unchanged'}")


def cmd_remove_phase(args: argparse.Namespace) -> dict:
    """Remove a phase and all its tasks."""
    phase_ref = args.phase_ref  # e.g. "Phase 2" or "Phase 2 - Description..."

    target = parse_phase_arg(phase_ref)

    def _transform(content: str) -> str:
        lines = content.splitlines()
        phase_ranges = extract_phases_lines("\n".join(lines))

        # Find the phase range to remove
        remove_start = None
        remove_end = None
        for start, end in phase_ranges:
            p = parse_phase_heading(lines[start])
            if p and p[1] == target:
                remove_start = start
                remove_end = end + 1  # exclusive
                break

        if remove_start is None:
            raise PlanError(f"{phase_ref} not found")

        # Remove lines for this phase (including trailing blank line if any)
        # Also remove one leading blank line if present
        if remove_start > 0 and lines[remove_start - 1].strip() == "":
            remove_start -= 1

        new_lines = lines[:remove_start] + lines[remove_end:]

        content = "\n".join(new_lines)
        content = _touch_updated(args.path, content)
        content = validate_status_set(content)
        return content

    _safe_edit(args.path, _transform)
    return _result("success", "remove-phase", f"Removed {phase_ref}")


# ---------------------------------------------------------------------------
# Commands — Task CRUD
# ---------------------------------------------------------------------------

def cmd_add_task(args: argparse.Namespace) -> dict:
    """Add a new task to an existing phase, inserted in sorted numeric position.

    If the phase_ref includes a description ("Phase N ➖ Title") and the phase
    doesn't exist, it is created first with that title.

    Accepts two forms:
      1. Separate args: add-task PLAN.md "Phase 2" "Task 2.4" "Do thing"
         or: add-task PLAN.md "Phase 2" "Do thing"  (auto-number task)
      2. Legacy combined: add-task PLAN.md "Phase 2" "Task 2.4 ➖ Do thing"
         (when task_title is None, task_ref carries the full combined string)
    """
    phase_ref = args.phase_ref  # e.g. "Phase 2" or "Phase 2 ➖ Description..."
    task_ref_arg = args.task_ref
    task_title_arg = args.task_title

    target_phase = parse_phase_arg(phase_ref)

    # None (missing arg) → legacy form; empty string → new form (rejected by validate_title)
    if task_title_arg is not None:
        # New form: separate ID + title
        explicit_p, explicit_t = parse_task_arg(task_ref_arg) if "Task" in task_ref_arg else (0, 0)
        raw_title = task_title_arg
        # Strip any ⚓ anchor suffix — deps must be added via add-task-dependency
        clean_title, _ = parse_task_deps(raw_title)
        clean_title = validate_title(clean_title, "task title")
        deps = []
    else:
        # Legacy form: combined string in task_ref (e.g. "Task 2.4 ➖ Do thing")
        explicit_p, explicit_t, raw_title = parse_task_add_arg(task_ref_arg)
        clean_title, deps = parse_task_deps(raw_title)
        clean_title = validate_title(clean_title, "task title")

    if explicit_p > 0 and explicit_t > 0:
        task_phase = explicit_p
        task_num = explicit_t
    else:
        task_phase = target_phase
        # Pre-read to determine task number for the result message
        existing = read_plan(args.path)
        phases = extract_phases(existing)
        max_task = 0
        for emoji, num, t_title, tasks in phases:
            if num == target_phase:
                for t in tasks:
                    if t[2] > max_task:
                        max_task = t[2]
        task_num = max_task + 1

    task_title_str = f"Task {task_phase}.{task_num} {clean_title}"

    # Extract phase title from phase_ref if it includes a description
    phase_title_from_ref = None
    if " ➖ " in phase_ref:
        phase_title_from_ref = phase_ref.split(" ➖ ", 1)[1].strip()

    def _transform(content: str) -> str:
        lines = content.splitlines()
        phases = extract_phases(content)

        # Check if phase exists; if not and phase_ref has a title, create it
        phase_exists = any(p[1] == target_phase for p in phases)
        if not phase_exists:
            if phase_title_from_ref:
                # Create the phase inline
                phase_heading = format_phase_heading(STATUS_TODO, target_phase, phase_title_from_ref)
                insert_idx = _sorted_phase_insert_index(lines, target_phase)
                # Strip trailing blanks before insertion
                while insert_idx > 0 and lines[insert_idx - 1].strip() == "":
                    insert_idx -= 1
                new_phase_lines = ["", phase_heading, ""]
                lines = lines[:insert_idx] + new_phase_lines + lines[insert_idx:]
                phases = extract_phases("\n".join(lines))
            else:
                raise PlanError(f"Phase {target_phase} not found")

        # Re-resolve task_num inside transform (content may differ from pre-read)
        if explicit_p > 0 and explicit_t > 0:
            tp = explicit_p
            tn = explicit_t
        else:
            tp = target_phase
            max_task = 0
            for emoji, num, t_title, tasks in phases:
                if num == target_phase:
                    for t in tasks:
                        if t[2] > max_task:
                            max_task = t[2]
            tn = max_task + 1

        # Check for duplicate task ID before inserting
        for emoji, num, t_title, tasks in phases:
            if num == target_phase:
                for t in tasks:
                    if t[2] == tn:
                        raise PlanError(
                            f"Task {target_phase}.{tn} already exists in Phase {target_phase}",
                        )

        # Insert at sorted position within the phase
        insert_idx, err = _sorted_task_insert_index(lines, target_phase, tn)
        if insert_idx is None:
            raise PlanError(err)

        task_line = format_task_line(STATUS_TODO, tp, tn, clean_title, deps)
        lines.insert(insert_idx, task_line)

        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        content = validate_status_set(content)
        return content

    _safe_edit(args.path, _transform)
    return _result("success", "add-task",
                    f"Added {task_title_str} to {phase_ref} with status {STATUS_TODO}",
                    task_id=f"Task {task_phase}.{task_num}")


def cmd_update_task(args: argparse.Namespace) -> dict:
    """Update task description (preserves existing dependencies).

    Accepts two forms:
      1. Separate args: update-task PLAN.md "Phase 2" "Task 2.4" "New description"
      2. Legacy combined: update-task PLAN.md "Phase 2" "Task 2.4 ➖ New description"
         (when task_title is None, task_ref carries the full combined string)
    """
    phase_ref = args.phase_ref  # e.g. "Phase 2" or "Phase 2 - Description..."
    task_ref_arg = args.task_ref
    task_title_arg = args.task_title

    # Empty string (from batch mode) treated as None → legacy form
    if task_title_arg:
        # New form: separate ID + title
        target_phase, target_task = parse_task_arg(task_ref_arg)
        new_description = validate_title(task_title_arg, "task title")
    else:
        # Legacy form: combined string in task_ref (e.g. "Task 2.4 ➖ New desc")
        target_phase, target_task = parse_task_arg(task_ref_arg)
        new_description = task_ref_arg.split(" ➖ ", 1)[-1].strip() if " ➖ " in task_ref_arg else None
        if new_description is not None:
            new_description = validate_title(new_description, "task title")

    def _transform(content: str) -> str:
        lines = content.splitlines()
        for i, line in enumerate(lines):
            t = parse_task_line(line)
            if t and t[1] == target_phase and t[2] == target_task:
                # Build new task line with updated title, preserving deps
                current_emoji = t[0]
                existing_deps = t[4]
                title_to_use = new_description if new_description else t[3]
                lines[i] = format_task_line(current_emoji, target_phase, target_task, title_to_use, existing_deps)
                break
        else:
            task_id = f"Task {target_phase}.{target_task}"
            raise PlanError(f"{task_id} not found in {phase_ref}")

        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        content = validate_status_set(content)
        return content

    task_id = f"Task {target_phase}.{target_task}"
    _safe_edit(args.path, _transform)
    return _result("success", "update-task",
                    f"Updated {task_id} description to: {new_description if new_description else 'unchanged'}")


def cmd_remove_task(args: argparse.Namespace) -> dict:
    """Remove a task from a phase."""
    phase_ref = args.phase_ref  # e.g. "Phase 2" or "Phase 2 - Description..."
    task_ref = args.task_ref  # e.g. "Task 2.4" or "Task 2.4 - Description..."

    target_phase, target_task = parse_task_arg(task_ref)

    def _transform(content: str) -> str:
        lines = content.splitlines()
        remove_start = None
        remove_end = None

        for i, line in enumerate(lines):
            t = parse_task_line(line)
            if t and t[1] == target_phase and t[2] == target_task:
                remove_start = i
                # Skip sub-bullets
                remove_end = i + 1
                j = i + 1
                while j < len(lines) and lines[j].startswith("  - "):
                    remove_end = j + 1
                    j += 1
                break

        if remove_start is None:
            raise PlanError(f"{task_ref} not found in {phase_ref}")

        new_lines = lines[:remove_start] + lines[remove_end:]

        content = "\n".join(new_lines)
        content = _touch_updated(args.path, content)
        content = validate_status_set(content)
        return content

    _safe_edit(args.path, _transform)
    return _result("success", "remove-task", f"Removed {task_ref}")


# ---------------------------------------------------------------------------
# Helpers — task dependency cycle detection
# ---------------------------------------------------------------------------

def _build_task_dep_graph(phases) -> dict[tuple[int, int], list[tuple[int, int]]]:
    """Build a task dependency graph from extracted phases.

    Returns dict mapping (phase, task) -> [(dep_phase, dep_task), ...].
    """
    graph: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for _, phase_num, _, tasks in phases:
        for t in tasks:
            # t = (emoji, phase, task, clean_title, deps)
            key = (t[1], t[2])
            dep_targets = []
            for dep_ref in t[4]:
                dp, dt = _resolve_dep_ref(dep_ref, t[1])
                if dp is not None:
                    dep_targets.append((dp, dt))
            graph[key] = dep_targets
    return graph


def _check_task_dep_cycle(graph: dict[tuple[int, int], list[tuple[int, int]]], new_dep_from: tuple[int, int], new_dep_to: tuple[int, int]) -> None:
    """Check if adding an edge from new_dep_from -> new_dep_to would create a cycle.

    A cycle exists if new_dep_to (or any of its transitive dependencies)
    can reach back to new_dep_from.

    Raises PlanError if cycle detected.
    """
    # BFS/DFS from new_dep_to through existing edges, see if we reach new_dep_from
    visited = set()
    stack = [new_dep_to]

    while stack:
        current = stack.pop()
        if current == new_dep_from:
            from_p, from_t = new_dep_from
            to_p, to_t = new_dep_to
            raise PlanError(
                f"adding dependency Task {from_p}.{from_t} -> Task {to_p}.{to_t} "
                f"would create a dependency cycle",
            )
        if current in visited:
            continue
        visited.add(current)
        for dep_target in graph.get(current, []):
            stack.append(dep_target)


# ---------------------------------------------------------------------------
# Commands — add-task-dependency / remove-task-dependency
# ---------------------------------------------------------------------------

def cmd_add_task_dependency(args: argparse.Namespace) -> dict:
    """Add a dependency to an existing task.

    Takes: phase_ref, task_ref (the task to modify), dep_task_ref (the dependency).
    Appends dep_task_ref to the ⚓ anchor of task_ref.

    State logic: if the target task's status is ☐ after modification, plan and
    phase statuses remain derived as ☐ (via validate_status_set). Otherwise,
    validate_status_set derives the correct status from actual task states.
    """
    phase_ref = args.phase_ref
    task_ref = args.task_ref
    dep_task_ref = args.dep_task_ref

    target_phase, target_task = parse_task_arg(task_ref)

    # Validate that dep_task_ref is a valid task reference
    dep_phase, dep_task = parse_task_arg(dep_task_ref)

    # Build the canonical dep ref string for comparison
    # If dep is in same phase as target, use "Task X.Y" form
    # If different phase, use "Phase X - Task X.Y" form
    if dep_phase == target_phase:
        canonical_dep = f"Task {dep_phase}.{dep_task}"
    else:
        canonical_dep = f"Phase {dep_phase} - Task {dep_phase}.{dep_task}"

    def _transform(content: str) -> str:
        lines = content.splitlines()
        phases = extract_phases(content)

        # Verify target task exists
        target_found = False
        for _, phase_num, _, tasks in phases:
            for t in tasks:
                if t[1] == target_phase and t[2] == target_task:
                    target_found = True
                    break
        if not target_found:
            raise PlanError(f"{task_ref} not found in {phase_ref}")

        # Verify dependency task exists
        dep_found = False
        for _, phase_num, _, tasks in phases:
            for t in tasks:
                if t[1] == dep_phase and t[2] == dep_task:
                    dep_found = True
                    break
        if not dep_found:
            raise PlanError(f"dependency {dep_task_ref} not found")

        # Build current dependency graph for cycle detection (before adding new edge)
        graph = _build_task_dep_graph(phases)

        # Check for cycles: adding edge from (target_phase, target_task) -> (dep_phase, dep_task)
        # means target depends on dep. A cycle exists if dep (or its transitive deps) can reach target.
        _check_task_dep_cycle(graph, (target_phase, target_task), (dep_phase, dep_task))

        # Now update the task line
        for i, line in enumerate(lines):
            t = parse_task_line(line)
            if t and t[1] == target_phase and t[2] == target_task:
                current_deps = list(t[4])  # existing deps

                # Check for duplicate (compare canonical forms)
                if canonical_dep in current_deps:
                    raise PlanError(
                        f"{task_ref} already depends on {dep_task_ref}",
                    )

                # Also check self-dependency
                if target_phase == dep_phase and target_task == dep_task:
                    raise PlanError("task cannot depend on itself")

                current_deps.append(canonical_dep)
                lines[i] = format_task_line(t[0], t[1], t[2], t[3], current_deps)
                break

        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        content = validate_status_set(content)
        return content

    _safe_edit(args.path, _transform)
    return _result("success", "add-task-dependency", f"Added dependency: {task_ref} -> {dep_task_ref}")


def cmd_remove_task_dependency(args: argparse.Namespace) -> dict:
    """Remove a dependency from an existing task.

    Takes: phase_ref, task_ref (the task to modify), dep_task_ref (the dependency to remove).
    Removes dep_task_ref from the ⚓ anchor of task_ref.

    State logic: if the target task's status is ☐ after modification, plan and
    phase statuses remain derived as ☐ (via validate_status_set). Otherwise,
    validate_status_set derives the correct status from actual task states.
    """
    phase_ref = args.phase_ref
    task_ref = args.task_ref
    dep_task_ref = args.dep_task_ref

    target_phase, target_task = parse_task_arg(task_ref)
    dep_phase, dep_task = parse_task_arg(dep_task_ref)

    # Build the canonical dep ref string for comparison
    if dep_phase == target_phase:
        canonical_dep = f"Task {dep_phase}.{dep_task}"
    else:
        canonical_dep = f"Phase {dep_phase} - Task {dep_phase}.{dep_task}"

    def _transform(content: str) -> str:
        lines = content.splitlines()

        # Verify target task exists
        phases = extract_phases(content)
        target_found = False
        for _, phase_num, _, tasks in phases:
            for t in tasks:
                if t[1] == target_phase and t[2] == target_task:
                    target_found = True
                    break
        if not target_found:
            raise PlanError(f"{task_ref} not found in {phase_ref}")

        # Find and update the task line
        removed = False
        for i, line in enumerate(lines):
            t = parse_task_line(line)
            if t and t[1] == target_phase and t[2] == target_task:
                current_deps = list(t[4])

                # Check if dependency actually exists
                # Compare against canonical form and also raw forms (in case of format mismatch)
                found_dep = False
                for raw_dep in current_deps:
                    rd_phase, rd_task = _resolve_dep_ref(raw_dep, target_phase)
                    if rd_phase == dep_phase and rd_task == dep_task:
                        found_dep = True
                        break

                if not found_dep:
                    raise PlanError(
                        f"{task_ref} does not depend on {dep_task_ref}",
                    )

                # Remove matching deps (could have both "Task X.Y" and "Phase X - Task X.Y" forms)
                new_deps = [
                    d for d in current_deps
                    if _resolve_dep_ref(d, target_phase) != (dep_phase, dep_task)
                ]

                lines[i] = format_task_line(t[0], t[1], t[2], t[3], new_deps)
                removed = True
                break

        if not removed:
            raise PlanError(f"{task_ref} not found in {phase_ref}")

        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        content = validate_status_set(content)
        return content

    _safe_edit(args.path, _transform)
    return _result("success", "remove-task-dependency", f"Removed dependency: {task_ref} -> {dep_task_ref}")


# ---------------------------------------------------------------------------
# Commands — sort
# ---------------------------------------------------------------------------

def cmd_check(args: argparse.Namespace) -> dict:
    """Check PLAN.md for consistency issues.

    Validates structure, status derivation, numbering, and dependencies.
    With --fix, auto-fixes recoverable issues (emoji derivation, numbering, ordering).
    """
    fix = getattr(args, "fix", False)
    exit_code, messages = check_plan(args.path, fix=fix)

    # Separate warnings from errors
    warnings = [m for m in messages if "empty-phase" in m]
    errors = [m for m in messages if "empty-phase" not in m]

    if exit_code == 0:
        # No errors — but still report warnings if any
        if warnings:
            return _result("warning", "check",
                            f"OK: {args.path} passed all checks (with warnings)",
                            path=args.path, issues=warnings)
        return _result("success", "check",
                        f"OK: {args.path} passed all checks",
                        path=args.path, issues=[])
    else:
        # Has errors — include warnings too
        all_issues = errors + warnings
        status = "warning" if not errors and warnings else "error"
        return _result(status, "check",
                        "; ".join(all_issues),
                        path=args.path, issues=all_issues)


def cmd_sort(args: argparse.Namespace) -> dict:
    """Sort phases by number and tasks within each phase by number."""
    def _transform(content: str) -> str:
        lines = content.splitlines()

        # Find header end (first ## Phase line)
        header_end = 0
        for i, line in enumerate(lines):
            if parse_phase_heading(line) is not None:
                header_end = i
                break
        else:
            # No phases found — nothing to sort
            content = "\n".join(lines)
            content = _touch_updated(args.path, content)
            return content

        header_lines = lines[:header_end]
        # Strip trailing blank lines from header (separator added during reconstruction)
        while header_lines and header_lines[-1].strip() == "":
            header_lines.pop()
        phase_block = lines[header_end:]

        # Find the last line that belongs to any phase section.
        # A line is phase content if it's a phase heading, a task line,
        # or an indented sub-bullet (starts with "  - ").
        last_content_idx = -1
        for i, line in enumerate(phase_block):
            if parse_phase_heading(line) is not None:
                last_content_idx = i
            elif parse_task_line(line) is not None:
                last_content_idx = i
            elif line.startswith("  - "):
                last_content_idx = i
        # Include trailing blank lines up to the next non-content line
        actual_end = last_content_idx + 1
        while actual_end < len(phase_block) and phase_block[actual_end].strip() == "":
            actual_end += 1

        # Extract phase sections from the trimmed block
        sections: list[tuple[int, list[str]]] = []
        i = 0
        while i < actual_end:
            p = parse_phase_heading(phase_block[i])
            if p is None:
                i += 1
                continue

            start = i

            # Find end of this section (next phase heading or actual_end)
            j = i + 1
            while j < actual_end and parse_phase_heading(phase_block[j]) is None:
                j += 1

            # Sort tasks within this section by task number
            section_lines = phase_block[start:j]
            sorted_section = _sort_tasks_in_section(section_lines)
            sections.append((p[1], sorted_section))
            i = j

        # Sort phases by number and reconstruct
        sections.sort(key=lambda s: s[0])
        sorted_phase_lines = []
        for idx, (_, section) in enumerate(sections):
            # Blank separator before each phase heading (always)
            sorted_phase_lines.append("")
            sorted_phase_lines.extend(section)

        new_lines = header_lines + sorted_phase_lines
        content = "\n".join(new_lines) + "\n"
        content = _touch_updated(args.path, content)
        content = validate_status_set(content)
        return content

    _safe_edit(args.path, _transform)
    return _result("success", "sort", "Sorted phases and tasks")


def _sort_tasks_in_section(section_lines: list[str]) -> list[str]:
    """Sort tasks within a phase section by task number, preserving sub-bullets."""
    if not section_lines:
        return section_lines

    # Find the phase heading line
    heading_idx = None
    for i, line in enumerate(section_lines):
        if parse_phase_heading(line) is not None:
            heading_idx = i
            break

    if heading_idx is None:
        return section_lines

    heading = [section_lines[heading_idx]]
    rest = section_lines[heading_idx + 1:]

    # Collect task blocks (task line + sub-bullets)
    task_blocks: list[tuple[int, list[str]]] = []
    i = 0
    while i < len(rest):
        t = parse_task_line(rest[i])
        if t is not None:
            block = [rest[i]]
            j = i + 1
            while j < len(rest) and rest[j].startswith("  - "):
                block.append(rest[j])
                j += 1
            task_blocks.append((t[2], block))
            i = j
        else:
            # Skip blank lines and other non-task content (formatting artifacts)
            i += 1

    # Sort task blocks by task number
    task_blocks.sort(key=lambda b: b[0])

    # Reconstruct: heading + blank separator + sorted tasks
    result = list(heading)
    result.append("")
    for _, block in task_blocks:
        result.extend(block)
    return result


# ---------------------------------------------------------------------------
# Commands — get-plan (structured output)
# ---------------------------------------------------------------------------


_STATUS_LABEL = {
    STATUS_TODO: "todo",
    STATUS_QUESTION: "question",
    STATUS_DOING: "doing",
    STATUS_ERROR: "error",
    STATUS_DONE: "done",
}


def parse_plan_data(
    plan_path: str | None = None,
    content: str | None = None,
    view: str = "list",
) -> list[dict] | dict:
    """Extract structured plan data from PLAN.md as native Python objects.

    Accepts either a file path (*plan_path*) or raw markdown text (*content*),
    but not both.  Returns parsed plan data as plain Python dicts — no
    serialisation to JSON/YAML strings.

    Args:
        plan_path: Path to a PLAN.md file on disk.  Read with shared lock
            and checksum verification when provided.
        content: Raw PLAN.md markdown text.  Used directly when provided.
        view: Output shape — ``"list"`` for a flat array of plan/phase/task
            items (default), or ``"tree"`` for a nested hierarchy.

    Returns:
        A ``list[dict]`` when *view* is ``"list"``, or a ``dict`` with a
        top-level ``"plan"`` key when *view* is ``"tree"``.

    Raises:
        ValueError: If neither or both *plan_path* and *content* are given,
            or if *view* is not ``"list"`` or ``"tree"``.

    Examples::

        # From a file
        data = parse_plan_data(plan_path="PLAN.md")

        # From raw text
        data = parse_plan_data(content=raw_text, view="tree")
    """
    if plan_path is None and content is None:
        raise ValueError("Either plan_path or content must be provided")
    if plan_path is not None and content is not None:
        raise ValueError("Provide either plan_path or content, not both")

    if view not in ("list", "tree"):
        raise ValueError(f"view must be 'list' or 'tree', got '{view}'")

    # Resolve raw content
    if plan_path is not None:
        content = _safe_read(plan_path)
    plan_id = plan_path or "PLAN.md"

    data = _build_plan_data(content)

    if view == "list":
        return _to_list_data(data, plan_id)
    else:
        return _to_tree_data(data, plan_id)


def _build_plan_data(content: str) -> dict:
    """Extract structured plan data from PLAN.md content.

    Returns a dict with plan header, phases, and tasks.
    """
    lines = content.splitlines()

    # Parse plan title
    plan_emoji = STATUS_TODO
    plan_title = ""
    for line in lines:
        m = _TITLE_RE.match(line.strip())
        if m:
            plan_emoji = m.group(1) or STATUS_TODO
            plan_title = m.group(2).strip()
            break

    # Parse header fields
    header = _parse_header("", lines)

    # Parse phases and tasks
    phases_data = []
    for emoji, num, title, tasks in extract_phases(content):
        task_data = []
        for t in tasks:
            # t = (emoji, phase, task, clean_title, deps)
            task_data.append({
                "id": f"Task {t[1]}.{t[2]}",
                "status": _STATUS_LABEL.get(t[0], t[0]),
                "title": t[3],
                "depends_on": t[4],
            })
        phases_data.append({
            "id": f"Phase {num}",
            "status": _STATUS_LABEL.get(emoji, emoji),
            "title": title,
            "tasks": task_data,
        })

    return {
        "title": plan_title,
        "status": _STATUS_LABEL.get(plan_emoji, plan_emoji),
        "depends_on": [d.strip() for d in header.get("depends_on", "").split(",") if d.strip() and d.strip() != "NONE"],
        "created": header.get("created", ""),
        "updated": header.get("updated", ""),
        "current_phase": header.get("current_phase", "NONE"),
        "current_task": header.get("current_task", "NONE"),
        "phases": phases_data,
    }


def _to_list_data(data: dict, plan_id: str) -> list[dict]:
    """Convert _build_plan_data dict to a flat list of native Python dicts.

    Same structure as --list output but returns Python objects instead of
    serialised JSON/YAML strings.
    """
    items = [{
        "type": "plan",
        "id": plan_id,
        "title": data["title"],
        "status": data["status"],
        "created": data["created"],
        "updated": data["updated"],
        "depends_on": list(data["depends_on"]),
    }]
    for phase in data["phases"]:
        items.append({
            "type": "phase",
            "id": phase["id"],
            "title": phase["title"],
            "status": phase["status"],
        })
        for task in phase["tasks"]:
            items.append({
                "type": "task",
                "phase": phase["id"],
                "id": task["id"],
                "title": task["title"],
                "status": task["status"],
                "depends_on": list(task["depends_on"]),
            })
    return items


def _to_tree_data(data: dict, plan_id: str) -> dict:
    """Convert _build_plan_data dict to a nested tree of native Python dicts.

    Same structure as --tree output but returns Python objects instead of
    serialised JSON/YAML strings.
    """
    phases = []
    for phase in data["phases"]:
        tasks = [{
            "id": task["id"],
            "status": task["status"],
            "title": task["title"],
            "depends_on": list(task["depends_on"]),
        } for task in phase["tasks"]]
        phases.append({
            "id": phase["id"],
            "status": phase["status"],
            "title": phase["title"],
            "tasks": tasks,
        })
    return {
        "plan": {
            "id": plan_id,
            "title": data["title"],
            "status": data["status"],
            "depends_on": list(data["depends_on"]),
            "created": data["created"],
            "updated": data["updated"],
            "phases": phases,
        },
    }


def _format_list_json(data: dict, plan_id: str) -> str:
    """Flat list format as JSON — plan, phases, and tasks in a single array."""
    items = [{
        "type": "plan",
        "id": plan_id,
        "title": data["title"],
        "status": data["status"],
        "created": data["created"],
        "updated": data["updated"],
        "depends_on": data["depends_on"],
    }]
    for phase in data["phases"]:
        items.append({
            "type": "phase",
            "id": phase["id"],
            "title": phase["title"],
            "status": phase["status"],
        })
        for task in phase["tasks"]:
            items.append({
                "type": "task",
                "phase": phase["id"],
                "id": task["id"],
                "title": task["title"],
                "status": task["status"],
                "depends_on": task["depends_on"],
            })
    return _json_mod.dumps(items, indent=2, ensure_ascii=False)


def _format_list_yaml(data: dict, plan_id: str) -> str:
    """Flat list format as YAML — plan, phases, and tasks in a single sequence."""
    lines = []
    lines.append("- type: plan")
    lines.append(f"  id: {plan_id}")
    lines.append(f"  title: {_yaml_scalar(data['title'])}")
    lines.append(f"  status: {data['status']}")
    lines.append(f"  created: {data['created']}")
    lines.append(f"  updated: {data['updated']}")
    depends = data["depends_on"]
    if depends:
        lines.append("  depends_on:")
        for d in depends:
            lines.append(f"    - {d}")
    else:
        lines.append("  depends_on: []")
    for phase in data["phases"]:
        lines.append("- type: phase")
        lines.append(f"  id: {phase['id']}")
        lines.append(f"  title: {phase['title']}")
        lines.append(f"  status: {phase['status']}")
        for task in phase["tasks"]:
            lines.append("- type: task")
            lines.append(f"  phase: {phase['id']}")
            lines.append(f"  id: {task['id']}")
            lines.append(f"  title: {_yaml_scalar(task['title'])}")
            lines.append(f"  status: {task['status']}")
            deps = task["depends_on"]
            if deps:
                lines.append("  depends_on:")
                for dep in deps:
                    lines.append(f"    - {dep}")
            else:
                lines.append("  depends_on: []")
    return "\n".join(lines) + "\n"


def _format_tree_json(data: dict, plan_id: str) -> str:
    """Tree format as JSON — nested phases with tasks."""
    tree = {
        "plan": {
            "id": plan_id,
            "title": data["title"],
            "status": data["status"],
            "depends_on": data["depends_on"],
            "created": data["created"],
            "updated": data["updated"],
            "phases": [],
        },
    }
    for phase in data["phases"]:
        phase_node = {
            "id": phase["id"],
            "status": phase["status"],
            "title": phase["title"],
            "tasks": [],
        }
        for task in phase["tasks"]:
            phase_node["tasks"].append({
                "id": task["id"],
                "status": task["status"],
                "title": task["title"],
                "depends_on": task["depends_on"],
            })
        tree["plan"]["phases"].append(phase_node)
    return _json_mod.dumps(tree, indent=2, ensure_ascii=False)


def _format_tree_yaml(data: dict, plan_id: str) -> str:
    """Tree format as YAML — nested phases with tasks."""
    lines = []
    lines.append("plan:")
    lines.append(f"  id: {plan_id}")
    lines.append(f"  title: {_yaml_scalar(data['title'])}")
    lines.append(f"  status: {data['status']}")
    depends = data["depends_on"]
    if depends:
        lines.append("  depends_on:")
        for d in depends:
            lines.append(f"    - {d}")
    else:
        lines.append("  depends_on: []")
    lines.append(f"  created: {data['created']}")
    lines.append(f"  updated: {data['updated']}")
    lines.append("  phases:")
    for phase in data["phases"]:
        lines.append(f"    - id: {phase['id']}")
        lines.append(f"      status: {phase['status']}")
        lines.append(f"      title: {phase['title']}")
        if phase["tasks"]:
            lines.append("      tasks:")
            for task in phase["tasks"]:
                lines.append(f"        - id: {task['id']}")
                lines.append(f"          status: {task['status']}")
                lines.append(f"          title: {_yaml_scalar(task['title'])}")
                deps = task["depends_on"]
                if deps:
                    lines.append("          depends_on:")
                    for dep in deps:
                        lines.append(f"            - {dep}")
                else:
                    lines.append("          depends_on: []")
        else:
            lines.append("      tasks: []")
    return "\n".join(lines) + "\n"


def _yaml_scalar(value: str) -> str:
    """Quote a YAML scalar if it needs quoting."""
    if not value:
        return '""'
    # Quote if contains special chars or looks like a number/bool
    needs_quote = False
    if any(c in value for c in ':{}[]&*?|->!%@`,#'):
        needs_quote = True
    if value.lower() in ('true', 'false', 'null', 'yes', 'no'):
        needs_quote = True
    try:
        float(value)
        needs_quote = True
    except ValueError:
        pass
    if needs_quote or '"' in value or '\n' in value:
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    return value


def cmd_get_plan(args: argparse.Namespace) -> dict:
    """Output structured plan data in list or tree format, json or yaml."""
    content = _safe_read(args.path)
    data = _build_plan_data(content)
    plan_id = args.path

    view = "tree" if args.tree else "list"
    fmt = "yaml" if args.yaml else "json"

    if view == "list":
        if fmt == "json":
            output = _format_list_json(data, plan_id)
        else:
            output = _format_list_yaml(data, plan_id)
    else:
        # tree
        if fmt == "json":
            output = _format_tree_json(data, plan_id)
        else:
            output = _format_tree_yaml(data, plan_id)

    return _result("success", "get-plan", "",
                    view=view, format=fmt, data=_json_mod.loads(output) if fmt == "json" else output)


# ---------------------------------------------------------------------------
# CLI — Argument Parser
# ---------------------------------------------------------------------------

def _add_path(sub, name: str, **kwargs) -> argparse.ArgumentParser:
    """Add a subparser with a positional 'path' argument prepended."""
    p = sub.add_parser(name, **kwargs)
    p.add_argument("path", help="Path to PLAN.md file")
    return p


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="plan.py",
        description="Deterministic PLAN.md manager — all reads/writes via script.",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # --- create ---
    p_create = sub.add_parser("create", help="Create a new PLAN.md")
    p_create.add_argument("path", help="Path to PLAN.md file")
    p_create.add_argument("title", help="Plan title")
    p_create.add_argument("depends", nargs="*", default=[], help="Dependency PLAN.md paths")

    # --- batch ---
    p_batch = sub.add_parser("batch", help="Execute multiple operations under one lock (reads commands from stdin or --input FILE)")
    p_batch.add_argument("path", help="Path to PLAN.md file")
    p_batch.add_argument("--input", help="Read commands from a file instead of stdin (.txt/.md → line mode, .json → JSON mode)")
    p_batch.add_argument("--json", action="store_true", help='Force JSON parse mode (default: auto-detect from file extension or stdin)')

    # --- get (header reads) ---
    _add_path(sub, "get-plan-title", help="Get plan title")
    _add_path(sub, "get-plan-depends-on", help="Get dependencies")
    _add_path(sub, "get-plan-created", help="Get created timestamp")
    _add_path(sub, "get-plan-updated", help="Get updated timestamp")
    _add_path(sub, "get-plan-current-phase", help="Get current phase")
    _add_path(sub, "get-plan-current-task", help="Get current task")

    # --- set (header writes) ---
    p_set_title = _add_path(sub, "set-plan-title", help="Set plan title")
    p_set_title.add_argument("title", help="New plan title")

    p_set_deps = _add_path(sub, "set-plan-depends-on", help="Set dependencies")
    p_set_deps.add_argument("deps", nargs="*", default=[], help="Dependency PLAN.md paths or NONE")

    p_set_created = _add_path(sub, "set-plan-created", help="Set created timestamp")
    p_set_created.add_argument("value", nargs="?", default="--now", help="ISO 8601 timestamp or --now (default: --now)")

    p_set_updated = _add_path(sub, "set-plan-updated", help="Set updated timestamp")
    p_set_updated.add_argument("value", nargs="?", default="--now", help="ISO 8601 timestamp or --now (default: --now)")

    p_set_cp = _add_path(sub, "set-plan-current-phase", help="Set current phase")
    p_set_cp.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')

    p_set_ct = _add_path(sub, "set-plan-current-task", help="Set current task")
    p_set_ct.add_argument("task_ref", help='Task reference, e.g. "Task 2.3"')

    # --- status reads ---
    _add_path(sub, "get-plan-status", help="Get plan status emoji")

    p_gps = _add_path(sub, "get-phase-status", help="Get phase status emoji")
    p_gps.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')

    p_gts = _add_path(sub, "get-task-status", help="Get task status emoji")
    p_gts.add_argument("task_ref", help='Task reference, e.g. "Task 2.3"')

    # --- status writes ---
    p_sas = _add_path(sub, "set-all-statuses", help="Set all statuses to same value")
    p_sas.add_argument("status", help="Status emoji")

    p_sps = _add_path(sub, "set-plan-status", help="Set plan status")
    p_sps.add_argument("status", help="Status emoji")

    p_sphs = _add_path(sub, "set-phase-status", help="Set phase status")
    p_sphs.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')
    p_sphs.add_argument("status", help="Status emoji")

    p_sts = _add_path(sub, "set-task-status", help="Set task status")
    p_sts.add_argument("task_ref", help='Task reference, e.g. "Task 2.3"')
    p_sts.add_argument("status", help="Status emoji")

    # --- phase CRUD ---
    p_add_phase = _add_path(sub, "add-phase", help="Add a new phase")
    p_add_phase.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2" or just "Planning"')
    p_add_phase.add_argument("phase_title", nargs="?", default=None, help='Phase title (optional, auto-derived from phase_ref if omitted)')

    p_upd_phase = _add_path(sub, "update-phase", help="Update phase title/description")
    p_upd_phase.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')
    p_upd_phase.add_argument("phase_title", nargs="?", default=None, help='New phase title (optional)')

    p_rm_phase = _add_path(sub, "remove-phase", help="Remove a phase and its tasks")
    p_rm_phase.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')

    # --- task CRUD ---
    p_add_task = _add_path(sub, "add-task", help="Add a new task")
    p_add_task.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')
    p_add_task.add_argument("task_ref", help='Task reference, e.g. "Task 2.4" or just "Do thing"')
    p_add_task.add_argument("task_title", nargs="?", default=None, help='Task title (optional, auto-derived from task_ref if omitted)')

    p_upd_task = _add_path(sub, "update-task", help="Update task description")
    p_upd_task.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')
    p_upd_task.add_argument("task_ref", help='Task reference, e.g. "Task 2.4"')
    p_upd_task.add_argument("task_title", nargs="?", default=None, help='New task title (optional)')


    p_rm_task = _add_path(sub, "remove-task", help="Remove a task")
    p_rm_task.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')
    p_rm_task.add_argument("task_ref", help='Task reference, e.g. "Task 2.4"')

    # --- get-plan (structured output) ---
    p_get_plan = _add_path(sub, "get-plan", help="Get structured plan data")
    view_group = p_get_plan.add_mutually_exclusive_group()
    view_group.add_argument("--list", action="store_true", help="Flat list view (default)")
    view_group.add_argument("--tree", action="store_true", help="Tree (nested) view")
    fmt_group = p_get_plan.add_mutually_exclusive_group()
    fmt_group.add_argument("--json", action="store_true", help="JSON output (default)")
    fmt_group.add_argument("--yaml", action="store_true", help="YAML output")

    # --- task dependency management ---
    p_add_dep = _add_path(sub, "add-task-dependency", help="Add a dependency to a task")
    p_add_dep.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')
    p_add_dep.add_argument("task_ref", help='Task reference, e.g. "Task 2.4"')
    p_add_dep.add_argument("dep_task_ref", help='Dependency task reference, e.g. "Task 2.1"')

    p_rm_dep = _add_path(sub, "remove-task-dependency", help="Remove a dependency from a task")
    p_rm_dep.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')
    p_rm_dep.add_argument("task_ref", help='Task reference, e.g. "Task 2.4"')
    p_rm_dep.add_argument("dep_task_ref", help='Dependency task reference, e.g. "Task 2.1"')

    # --- sort ---
    _add_path(sub, "sort", help="Sort phases and tasks by number")

    # --- check ---
    p_check = _add_path(sub, "check", help="Check PLAN.md consistency (with optional --fix)")
    p_check.add_argument("--fix", action="store_true", help="Auto-fix recoverable issues")

    return parser


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

COMMAND_MAP = {
    "batch": cmd_batch,
    "create": cmd_create,
    "get-plan": cmd_get_plan,
    "get-plan-title": cmd_get_plan_title,
    "get-plan-depends-on": cmd_get_plan_depends_on,
    "get-plan-created": cmd_get_plan_created,
    "get-plan-updated": cmd_get_plan_updated,
    "get-plan-current-phase": cmd_get_plan_current_phase,
    "get-plan-current-task": cmd_get_plan_current_task,
    "set-plan-title": cmd_set_plan_title,
    "set-plan-depends-on": cmd_set_plan_depends_on,
    "set-plan-created": cmd_set_plan_created,
    "set-plan-updated": cmd_set_plan_updated,
    "set-plan-current-phase": cmd_set_plan_current_phase,
    "set-plan-current-task": cmd_set_plan_current_task,
    "get-plan-status": cmd_get_plan_status,
    "get-phase-status": cmd_get_phase_status,
    "get-task-status": cmd_get_task_status,
    "set-all-statuses": cmd_set_all_statuses,
    "set-plan-status": cmd_set_plan_status,
    "set-phase-status": cmd_set_phase_status,
    "set-task-status": cmd_set_task_status,
    "add-phase": cmd_add_phase,
    "update-phase": cmd_update_phase,
    "remove-phase": cmd_remove_phase,
    "add-task": cmd_add_task,
    "update-task": cmd_update_task,
    "remove-task": cmd_remove_task,
    "add-task-dependency": cmd_add_task_dependency,
    "remove-task-dependency": cmd_remove_task_dependency,
    "sort": cmd_sort,
    "check": cmd_check,
}


def _preprocess_args(argv: list[str]) -> list[str]:
    """Replace --now with a safe token before argparse sees it."""
    return ["__NOW__" if a == "--now" else a for a in argv]


def main() -> None:
    parser = build_parser()
    args = parser.parse_args(_preprocess_args(sys.argv[1:]))

    handler = COMMAND_MAP.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    # Run command and get JSON result
    result = _run_command(handler, args)

    # Print JSON output
    _print_json_result(result)

    # Exit with appropriate code
    if result["status"] in ("error",):
        sys.exit(1)
    elif result["status"] == "skipped":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
