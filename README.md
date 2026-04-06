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
- a live API key for the configured provider

### Quickstart for most users

```bash
git clone https://github.com/McGluut/loophole_go
cd loophole_go
uv sync
```

Set your key:

```powershell
$env:LOOPHOLE_API_KEY="sk-ant-..."
```

Run the app:

```bash
uv run loophole
```

If you prefer the module form:

```bash
uv run python -m loophole.main
```

### Install details

Using `uv`:

```bash
git clone https://github.com/McGluut/loophole_go
cd loophole_go
uv sync
```

Using plain Python tooling without `uv`:

```bash
git clone https://github.com/McGluut/loophole_go
cd loophole_go
python -m pip install -e .
```

### Set your API key

Preferred generic variable:

Bash:

```bash
export LOOPHOLE_API_KEY="sk-ant-..."
```

PowerShell:

```powershell
$env:LOOPHOLE_API_KEY="sk-ant-..."
```

Backward-compatible provider variable:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Live runs in this repo still use the Anthropic SDK today. The generic `LOOPHOLE_API_KEY` name is provided so local setup does not have to depend on a provider-specific environment variable.

If you cloned the repo and are running from source, do not assume plain `python -m loophole.main` will pick up the `uv` environment. After `uv sync`, prefer `uv run loophole` or `uv run python -m loophole.main`.

## Usage

### Start a new session

Installed console script:

```bash
uv run loophole new --domain privacy --principles examples/privacy_principles.txt
```

Module form:

```bash
uv run python -m loophole.main new --domain privacy --principles examples/privacy_principles.txt
```

Interactive menu:

```bash
uv run loophole
```

### Resume a session

```bash
uv run loophole resume
```

or

```bash
uv run python -m loophole.main resume
```

### Generate a report

```bash
uv run loophole visualize
```

or

```bash
uv run python -m loophole.main visualize
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
