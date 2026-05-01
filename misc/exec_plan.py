#!/usr/bin/env python3
"""Execute PLAN.md tasks one at a time using pi until all are done.

The script is a dumb harness — it just loops the prompt and checks for
the [[PLAN DONE]] sentinel. All plan reading, task selection, execution,
and status updates are handled by the workflow skill inside pi.
"""

import sys
import time
import argparse
from pathlib import Path
from subprocess import PIPE, Popen, TimeoutExpired

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# PLAN_MD = Path(__file__).parent / "PLAN.md"  # ./PLAN.md from repo root
PLAN_MD = Path(__file__).parent.parent / "PLAN.md"  # ./PLAN.md from repo root

PROVIDERS = ["llama.cpp s0", "llama.cpp s1", "llama.cpp s2", "llama.cpp s3"]
MODEL = "Qwen/Qwen3.6-27B"
TIMEOUT = 3600
MAX_ITERS = 100

RETRY_INITIAL_DELAY = 5
RETRY_MAX_DELAY = 900
RETRY_BACKOFF_FACTOR = 2

PROMPT = """\
/skill:workflow from local @PLAN.md execute next task.
just one task.
you are allowed to use `write-skill` (write-skill assume complex skill) and `tzip` (`tzip on`) skills.
if plan is fully successfully completed, just return `[[PLAN DONE]]`."""


# ---------------------------------------------------------------------------
# Pi subprocess with exponential backoff retry
# ---------------------------------------------------------------------------

def run_pi(provider: str, model: str, prompt: str, iteration: int) -> str:
    """Call pi subprocess with exponential backoff retry. Returns stdout."""
    delay = RETRY_INITIAL_DELAY
    attempt = 0

    while True:
        attempt += 1
        print(f"[iter {iteration}] Attempt {attempt} (provider: {provider})", flush=True)

        t0 = time.time()
        try:
            proc = Popen(
                ["pi", "--provider", provider, "--model", model, "-p", prompt],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
            )
            stdout, stderr = proc.communicate(timeout=TIMEOUT)
            elapsed = time.time() - t0

            if proc.returncode == 0 and (stdout or "").strip():
                print(f"[iter {iteration}] SUCCESS (attempt {attempt}, {elapsed:.0f}s)", flush=True)
                return stdout.strip()

            err_preview = (stderr or "")[:200]
            print(
                f"[iter {iteration}] FAILED attempt {attempt} "
                f"(rc={proc.returncode}, {elapsed:.0f}s)\n"
                f"      stderr: {err_preview}",
                flush=True,
            )
        except TimeoutExpired:
            proc.kill()
            elapsed = time.time() - t0
            print(f"[iter {iteration}] TIMEOUT on attempt {attempt} after {elapsed:.0f}s", flush=True)
        except Exception as exc:
            elapsed = time.time() - t0
            print(f"[iter {iteration}] ERROR on attempt {attempt}: {exc}", flush=True)

        print(f"[iter {iteration}] Sleeping {delay:.0f}s before retry...", flush=True)
        time.sleep(delay)
        delay *= RETRY_BACKOFF_FACTOR
        if delay > RETRY_MAX_DELAY:
            delay = RETRY_INITIAL_DELAY


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Execute PLAN.md until done using pi"
    )
    parser.add_argument(
        "--provider", default=None,
        help="Provider name (overrides rotation)"
    )
    parser.add_argument(
        "--model", default=MODEL,
        help=f"Model pattern (default: {MODEL})"
    )
    parser.add_argument(
        "--timeout", type=int, default=TIMEOUT,
        help=f"Timeout per pi call in seconds (default: {TIMEOUT})"
    )
    parser.add_argument(
        "--max-iters", type=int, default=MAX_ITERS,
        help=f"Max iterations (default: {MAX_ITERS})"
    )
    args = parser.parse_args()

    # Early check — fail if PLAN.md missing
    if not PLAN_MD.exists():
        print(
            f"FATAL: {PLAN_MD} does not exist. Nothing to execute.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"{'=' * 60}")
    print(f"Plan Executor — pi sequential")
    print(f"Plan     : {PLAN_MD}")
    print(f"Model    : {args.model}")
    print(f"Timeout  : {args.timeout}s per call")
    print(f"Max iters: {args.max_iters}")
    if args.provider:
        print(f"Provider : {args.provider} (fixed)")
    else:
        print(f"Providers: {', '.join(PROVIDERS)} (rotating)")
    print(f"{'=' * 60}\n")

    for iteration in range(args.max_iters):
        # Rotate provider or use fixed
        if args.provider:
            provider = args.provider
        else:
            provider = PROVIDERS[iteration % len(PROVIDERS)]

        stdout = run_pi(provider, args.model, PROMPT, iteration)

        # Check for completion sentinel
        if "[[PLAN DONE]]" in stdout:
            print(f"\n{'=' * 60}")
            print(f"PLAN COMPLETE after {iteration + 1} iteration(s)!")
            print(f"{'=' * 60}")
            sys.exit(0)

        print(f"\n--- Iteration {iteration + 1} done, moving to next ---\n", flush=True)

    # Max iterations reached
    print(
        f"\nFATAL: Hit max iterations ({args.max_iters}) without [[PLAN DONE]].",
        file=sys.stderr,
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
