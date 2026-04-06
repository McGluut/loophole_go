# Limitations

## What This Tool Can Support

Loophole can help with:

- adversarial drafting of a policy or rule set
- identifying candidate loopholes and overreach cases
- recording a revision history
- forcing human review when the loop cannot safely continue on its own

## What This Tool Cannot Establish

Loophole cannot establish:

- that a code is complete
- that a code is morally correct
- that “no failures found” means the code is robust in general
- that auto-resolved revisions preserve intent beyond the limits of the current prompts and validator behavior

## Model Dependence

Behavior depends on:

- model choice
- temperature settings
- prompt wording
- prior session state
- the quality of human principles and escalated clarifications

Changing any of those can change the cases, the judgments, and the revisions.

## Known Failure Modes

- malformed model output can break the expected protocol
- the adversarial agents can miss obvious cases
- the judge can be overly conservative or insufficiently conservative
- the legislator can introduce regressions while appearing compliant
- the validator is itself model-mediated rather than formal
- session path assumptions remain oriented toward repo-root operation

## Why “No Failure Found” Is Weak

The loop reports only what this round of search produced.

A clean round can mean:

- the code survived a meaningful attack set
- the attackers failed to produce useful cases
- the output was malformed
- the prompts failed to explore the right area

Treat it as a local result, not a global one.

## Recommended Human Review

Review at least these questions after a serious run:

- Did the escalations expose real principle pressure or just prompt/validator weakness?
- Did the accepted revisions actually narrow ambiguity?
- Did the code become clearer, or just longer?
- Are any accepted cases still contestable on a second reading?
- Does the final code say what you mean, or only what the model could stabilize?
