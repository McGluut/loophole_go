# Architecture

## Purpose

Loophole is a small interactive application for adversarially pressure-testing a draft rule system.

Its output is not just a rewritten code document. It is a sequence of cases, revisions, escalations, and operator judgments that can be inspected afterward.

## Normative Layers

Loophole has multiple layers of authority. They should not be collapsed into “the model decided.”

1. Human moral principles
2. Human clarifications added during escalations
3. Current legal code draft
4. Resolved case history
5. Judge and legislator outputs
6. HTML and markdown reporting artifacts

The top layers constrain the lower ones.

## Control Flow

### 1. Initial draft

- `Legislator.draft_initial()` turns principles into a first code draft.

### 2. Adversarial search

- `LoopholeFinder.find()` proposes legal-but-wrong scenarios.
- `OverreachFinder.find()` proposes illegal-but-acceptable scenarios.

### 3. Judgment

- `Judge.evaluate()` decides whether a case looks locally resolvable.
- if resolvable, the legislator writes a revised code draft
- the revised code is validated against resolved cases before acceptance
- if unresolved or regressive, the case escalates to the operator

### 4. Persistence

- `SessionManager.save()` writes machine-readable and human-readable artifacts after each completed case

### 5. Reporting

- `generate_html()` renders a session timeline from the saved state

## Key Components

### CLI / orchestration

- [`loophole/main.py`](../loophole/main.py)

Owns:

- command routing
- session lifecycle
- round loop
- escalation prompts

### Domain models

- [`loophole/models.py`](../loophole/models.py)

Owns:

- `SessionState`
- `Case`
- `LegalCode`

### Agent wrappers

- [`loophole/agents/`](../loophole/agents)

Own:

- prompt construction
- response parsing
- role-specific contracts

### Provider boundary

- [`loophole/llm.py`](../loophole/llm.py)

Owns:

- Anthropic client creation
- text-block extraction
- dependency failure at the live runtime boundary

### Persistence and reporting

- [`loophole/session.py`](../loophole/session.py)
- [`loophole/visualize.py`](../loophole/visualize.py)

## Known Non-Separations

The repo is intentionally small, but some boundaries are still tighter than ideal:

- CLI orchestration and application policy still live in the same file
- the judge proposes resolution semantics, but the legislator generates the actual accepted code
- precedent is carried as prompt context and validator checks, not as a formal rule engine
- session path handling is clearer than before but still oriented toward repo-root operation

## Review Notes

When reviewing changes, evaluate them by layer:

- Does this change affect human authority or only model behavior?
- Does it alter precedent handling or only output formatting?
- Does it improve truthfulness of claims, or only polish?
- Does it create a clearer contestability path when the system is wrong?
