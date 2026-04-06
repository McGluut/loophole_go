# Operator Guide

## Prerequisites

- Python 3.12+
- project dependencies installed
- `ANTHROPIC_API_KEY` set for live runs

## Run From Repo Root

Current best practice is to run Loophole from the repository root.

Reason:

- `config.yaml` is loaded from the working directory
- session artifacts are clearer and more predictable from the repo root
- some path assumptions remain root-oriented even though `session_dir` is now used for report output

## Recommended Commands

PowerShell:

```powershell
$env:ANTHROPIC_API_KEY="sk-ant-..."
python -m loophole.main new --domain privacy --principles examples/privacy_principles.txt
```

Bash:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python -m loophole.main new --domain privacy --principles examples/privacy_principles.txt
```

## Session Files

Each session directory contains:

- `state.json`
- `current_code.md`
- `case_log.md`
- `report.html`

By default these land under `sessions/<session_id>/`.

## Persistence Timing

Sessions are saved after each completed case during the adversarial loop.

That means:

- you do not lose everything if a later round fails
- you can inspect the current session state between rounds
- prompt-boundary input is not saved independently before a case is completed

## Failure Modes To Expect

- missing dependency errors when live provider packages are not installed
- malformed model outputs
- validation failures when a revision breaks precedent
- escalation loops when human clarifications still conflict with prior accepted cases

## Review Checklist After Each Round

- Did any accepted revision make the code clearer?
- Did any escalation reflect ambiguity rather than deep conflict?
- Did the final code drift away from the original principles?
- Are there cases you would reject even if the loop accepted them?

## Cost And Latency

This is a multi-call LLM workflow.

Operator expectations should include:

- repeated API calls per round
- stochastic outputs
- latency spikes on longer prompts
- higher cost than a single-shot drafting prompt
