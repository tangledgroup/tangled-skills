---
name: loop
description: A minimal problem-solving loop with required phases Planning and Build, optional Design (auto-generated from Planning if not provided), and optional phases Test, Release, Improve. Works for any problem — software, business, personal projects, marketing, writing, product creation, research, or anything else. Works for humans, AI agents, or any combination. Use when tackling a new problem that benefits from structured iteration, tracking work through phases, or coordinating human-AI collaboration.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - problem-solving
  - methodology
  - workflow
  - iteration
  - planning
category: methodology
---

# Problem-Solving Loop v0.1.0

## Overview

A very minimal, practical loop for solving **any problem** — software, business, personal projects, marketing, writing, product creation, research, or anything else. Works for humans, AI agents, or any combination.

The loop has two required phases — **Planning** and **Build** — and four optional phases — Design, Test, Release, Improve. The typical flow moves forward through phases. You can loop within any phase as needed before moving on, and Test feeds back to Build when issues are found.

## When to Use

- Starting a new problem and need a structured approach
- Breaking down complex work into manageable phases
- Coordinating work between humans and AI agents
- Tracking progress through defined stages
- Iterating on existing work with clear improvement cycles
- Any situation where a repeatable, minimal process would reduce chaos

## Phase Requirements

| Phase      | Required | Notes |
|------------|----------|-------|
| Planning   | Yes      | Must be defined before any work begins; loop within as needed |
| Design     | No       | Auto-generated from Planning info if not provided; loop within as needed |
| Build      | Yes      | Core work phase; loop within as needed |
| Test       | No       | Optional validation step; loop within as needed |
| Release    | No       | Optional deployment step; loop within as needed |
| Improve    | No       | Optional refinement; loops back to Planning |

## The Phases

### 1. Planning (Understand & Decide) — Required

Clearly understand the problem before acting. This phase is mandatory — no work begins without it.

- Define what needs to be solved
- List the main things needed to solve it
- Decide priorities (what's must-have vs nice-to-have)
- Loop within Planning if the problem isn't clear yet — refine understanding before moving on

**Outcome:** A clear understanding of the problem and ranked priorities.

### 2. Design (Plan the Solution) — Optional

Outline how the solution will work before building. If the user does not provide a Design phase, it is auto-generated based on best practices and the information given in Planning.

- Describe the approach at a high level
- Break it into clear parts or steps
- Choose the simplest approach that works
- Loop within Design if the plan needs refinement before moving on

**Outcome:** A plan with defined parts and a chosen approach.

### 3. Build (Make It) — Required

Do the actual work. Create the main pieces. This is the core phase where work happens.

- Keep it simple and focused
- Implement one piece at a time
- Avoid over-engineering
- Loop within Build as needed — iterate on the implementation until it feels ready

**Outcome:** A working solution, however rough.

### 4. Test (Check If It Works) — Optional

Verify the solution meets its goals. If issues are found, go back to Build.

- Test it thoroughly
- Identify problems or mistakes
- Gather feedback if possible
- Loop within Test to cover edge cases before declaring done
- If something is fundamentally wrong, return to **Build**

**Outcome:** Known issues and confidence in what works.

### 5. Release (Put It Into Use) — Optional

Deploy or apply the solution to its intended context.

- Make it available to users or systems
- Document how to use it
- Communicate what changed
- Loop within Release if deployment needs adjustment (roll back, retry, etc.)

**Outcome:** The solution is live and accessible.

### 6. Improve (Keep Making It Better) — Optional

Refine based on real-world feedback.

- Fix issues that appear in production
- Add small improvements
- Learn from actual use
- Loop within Improve to address multiple rounds of feedback
- Loop back to **Planning** for the next cycle

**Outcome:** A better version, ready for another loop.

## Flow

The typical flow:

1. **Planning** → (required starting point; loop within as needed)
2. **Design** → (skip if not needed; auto-generated from Planning if omitted; loop within as needed)
3. **Build** → (loop within as needed until ready)
4. **Test** → (optional; loop within to cover cases; if fundamentally wrong, go back to Build)
5. **Release** → (optional; loop within if deployment needs adjustment)
6. **Improve** → (optional; loop within for multiple rounds; then back to Planning)

You can loop within any phase as many times as needed before moving forward. There is no fixed number of iterations.

Minimal viable loop: **Planning → Build** (done). Everything else is optional refinement.

## Planning Terms

These terms provide a shared vocabulary for tracking work within the loop.

**Goal** — The big thing you want to achieve.
Example: "Launch a new website."

**Task** — A small piece of work that contributes to a goal.
Example: "Write the homepage content."

**Issue** — Something wrong or blocking progress.
Example: "Payment button not working."

Work items move through three states:

- **To Do** — Work identified but not started.
- **In Progress** — Currently being worked on.
- **Done** — Finished and checked.

## How to Use This Loop

- Start with Planning — it is required.
- Skip Design if the problem is straightforward; it will be generated from Planning context.
- You can loop within any phase as many times as needed before moving forward.
- Build is where the core work happens — loop within it until ready.
- Test feeds back to Build if something is fundamentally wrong.
- Test, Release, and Improve are optional refinements.
- Keep each task small enough to complete in one focused session.
- Works for individuals, teams, AI agents, or any collaboration model.
- There is no "perfect" first pass — the loop exists to iterate toward quality.

## Example: Building a Feature

Here is how the loop applies to a concrete software task.

**Planning:** The goal is to add user search to the dashboard. Must-have: search by name. Nice-to-have: filter by role.

**Design:** Add a search input in the header. Call the existing `/api/users` endpoint with a `q` parameter. Render results in a dropdown.

**Build:** Implement the input field, wire it to the API call, render matching users.

**Test:** Search for known users — results appear. Try empty query — no crash. Try special characters — handled.

**Release:** Deploy to production. Announce the feature to the team.

**Improve:** Users request search by email too. Loop back to Planning with that as the new goal.

## Example: Minimal Loop (Planning → Build Only)

Not every task needs all phases.

**Planning:** Write API documentation for the auth endpoint. Must-have: request/response examples. Nice-to-have: error code reference.

**Build:** Write the docs. Done.

No Design, Test, Release, or Improve needed — the task was straightforward. Next time a related doc is needed, start a new loop from Planning.
