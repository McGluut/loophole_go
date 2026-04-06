# Loophole

Loophole is a human-in-the-loop adversarial drafting tool for turning moral principles into a draft legal-style code, attacking that code with counterexamples, and revising it round by round.

It is designed to help surface pressure on a rule set. It is not a moral theorem prover, a formal verifier, or an autonomous policy engine.

## What Loophole Does

Loophole runs a four-role loop:

1. A **Legislator** drafts a legal code from your stated principles.
2. A **Loophole Finder** looks for scenarios that appear legal under that code but violate the intended principles.
3. An **Overreach Finder** looks for the opposite: scenarios the code prohibits even though a human may still judge them acceptable.
4. A **Judge** decides whether a case looks locally resolvable or should be escalated back to the operator.

Every round produces explicit artifacts:

- the current legal code
- a case log
- serialized session state
- an HTML report

## What Loophole Does Not Do

Loophole does not provide:

- formal consistency proofs
- exhaustive loophole coverage
- guaranteed preservation of moral intent
- autonomous high-stakes decision making
- evidence that an escalation reflects a deep moral contradiction rather than drafting ambiguity, validator conservatism, or model error

If a round finds no failures, that means only that this round of model-mediated search did not produce parseable cases that survived the loop. It does not establish completeness.

## Authority Order

Loophole has a simple authority chain:

1. **Human principles**
2. **Human clarifications and escalated resolutions**
3. **Current legal code**
4. **Resolved case history**
5. **Model judgments and rewrites**

The human remains the highest authority layer throughout.

The system attempts to preserve resolved precedent through prompt context and validator checks. That is a meaningful constraint, but it is not a formal guarantee.

## Session Lifecycle

`new`:
- collects a domain and principles
- drafts an initial code
- enters the adversarial loop

Each loop round:
- runs both adversarial finders
- evaluates every case through the judge
- auto-applies only revisions that survive validation against resolved cases
- escalates unresolved or regression-inducing cases to the operator
- saves session artifacts after each completed case

`resume`:
- reloads a saved session and continues the loop

`visualize`:
- renders an HTML report for a saved session

## Outputs

By default, each session writes:

- `state.json`
- `current_code.md`
- `case_log.md`
- `report.html`

See [docs/operator-guide.md](docs/operator-guide.md) for current path behavior and the `session_dir` caveat.

## Setup

### Requirements

- Python 3.12+
- an Anthropic API key for live runs

### Install

Using `uv`:

```bash
git clone https://github.com/McGluut/loophole_go
cd loophole_go
uv sync
```

Using plain Python tooling:

```bash
git clone https://github.com/McGluut/loophole_go
cd loophole_go
python -m pip install anthropic pydantic rich typer pyyaml
```

### Set your API key

Bash:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

PowerShell:

```powershell
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

## Usage

### Start a new session

Installed console script:

```bash
loophole new --domain privacy --principles examples/privacy_principles.txt
```

Module form:

```bash
python -m loophole.main new --domain privacy --principles examples/privacy_principles.txt
```

Interactive menu:

```bash
python -m loophole.main
```

### Resume a session

```bash
loophole resume
```

or

```bash
python -m loophole.main resume
```

### Generate a report

```bash
loophole visualize
```

or

```bash
python -m loophole.main visualize
```

## Configuration

The default configuration lives in [config.yaml](config.yaml):

```yaml
model:
  default: "claude-sonnet-4-20250514"
  max_tokens: 4096

temperatures:
  legislator: 0.4
  loophole_finder: 0.9
  overreach_finder: 0.9
  judge: 0.3

loop:
  max_rounds: 10
  cases_per_agent: 3

session_dir: "sessions"
```

Current operational caveat:

- this repo is still best run from the repository root
- `session_dir` is used for session storage and report output, but some operator assumptions remain root-oriented

## Development

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

The current tests focus on:

- protocol contract failures
- session persistence
- report generation
- human-escalation rollback behavior

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/TRUST_MODEL.md](docs/TRUST_MODEL.md)
- [docs/LIMITATIONS.md](docs/LIMITATIONS.md)
- [docs/operator-guide.md](docs/operator-guide.md)
- [docs/SESSION_REVIEW_TEMPLATE.md](docs/SESSION_REVIEW_TEMPLATE.md)

## Why This Repo Exists

Most rule systems look stronger than they are until someone attacks their wording. Loophole is useful when you want a structured way to pressure-test a draft norm system, keep the human in charge, and leave behind auditable artifacts rather than a single polished answer.

That is the ambition.

The current repo should be read as an experimental application that helps surface candidate gaps, not as a settled engine for moral or legal judgment.
