from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from loophole.agents.base import BaseAgent
from loophole.errors import ProtocolError
from loophole.models import Case, SessionState
from loophole.prompts import JUDGE_RESOLVE, JUDGE_SYSTEM, JUDGE_VALIDATE


def _format_resolved_cases(cases: list[Case]) -> str:
    if not cases:
        return "(none yet)"
    parts = []
    for c in cases:
        parts.append(
            f"Case #{c.id} ({c.case_type.value})\n"
            f"  Scenario: {c.scenario}\n"
            f"  Problem: {c.explanation}\n"
            f"  Resolution: {c.resolution}\n"
            f"  Resolved by: {c.resolved_by}"
        )
    return "\n\n".join(parts)


@dataclass
class JudgeResult:
    resolvable: bool
    reasoning: str
    pressure_kind: str
    pressure_reason: str
    proposed_revision: str | None = None
    resolution_summary: str | None = None
    conflict_explanation: str | None = None


@dataclass
class ValidationResult:
    passes: bool
    details: str


class Judge(BaseAgent):
    def _build_system_prompt(self, **kwargs: Any) -> str:
        return JUDGE_SYSTEM

    def _build_user_message(self, state: SessionState, **kwargs: Any) -> str:
        case: Case = kwargs["case"]
        return JUDGE_RESOLVE.format(
            moral_principles=state.moral_principles,
            user_clarifications="\n".join(state.user_clarifications) or "(none)",
            code_version=state.current_code.version,
            legal_code=state.current_code.text,
            case_type=case.case_type.value,
            case_scenario=case.scenario,
            case_explanation=case.explanation,
            resolved_cases_text=_format_resolved_cases(state.resolved_cases),
        )

    def evaluate(self, state: SessionState, case: Case) -> JudgeResult:
        raw = self.run(state, case=case)

        verdict_match = re.search(r"<verdict>\s*(.*?)\s*</verdict>", raw, re.DOTALL)
        verdict = verdict_match.group(1).strip().lower() if verdict_match else "unresolvable"

        reasoning = _extract_tag(raw, "reasoning") or ""
        pressure_kind = _extract_tag(raw, "pressure_kind")
        pressure_reason = _extract_tag(raw, "pressure_reason")
        if not pressure_kind or not pressure_reason:
            raise ProtocolError("Judge response did not include a full pressure classification.")

        if verdict == "resolvable":
            proposed_revision = _extract_tag(raw, "proposed_revision")
            resolution_summary = _extract_tag(raw, "resolution_summary")
            if not proposed_revision or not resolution_summary:
                raise ProtocolError(
                    "Judge marked a case resolvable without providing a full revision and resolution summary."
                )
            return JudgeResult(
                resolvable=True,
                reasoning=reasoning,
                pressure_kind=pressure_kind,
                pressure_reason=pressure_reason,
                proposed_revision=proposed_revision,
                resolution_summary=resolution_summary,
            )
        return JudgeResult(
            resolvable=False,
            reasoning=reasoning,
            pressure_kind=pressure_kind,
            pressure_reason=pressure_reason,
            conflict_explanation=_extract_tag(raw, "conflict_explanation"),
        )

    def validate(self, state: SessionState, proposed_code: str) -> ValidationResult:
        resolved = state.resolved_cases
        if not resolved:
            return ValidationResult(passes=True, details="No prior cases to validate against.")

        user_msg = JUDGE_VALIDATE.format(
            proposed_code=proposed_code,
            resolved_cases_text=_format_resolved_cases(resolved),
        )
        raw = self.llm.call(JUDGE_SYSTEM, user_msg, temperature=self.temperature)

        passes_match = re.search(r"<passes>\s*(.*?)\s*</passes>", raw, re.DOTALL)
        if not passes_match:
            raise ProtocolError("Judge validation response did not include a <passes> tag.")
        passes = passes_match.group(1).strip().lower() == "true"

        details = _extract_tag(raw, "details")
        if not details:
            raise ProtocolError("Judge validation response did not include a <details> tag.")
        return ValidationResult(passes=passes, details=details)


def _extract_tag(text: str, tag: str) -> str | None:
    m = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    return m.group(1).strip() if m else None
