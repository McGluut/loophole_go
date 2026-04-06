from __future__ import annotations

import unittest

from loophole.agents.judge import Judge
from loophole.agents.loophole_finder import _parse_scenarios as parse_loopholes
from loophole.agents.overreach_finder import _parse_scenarios as parse_overreaches
from loophole.errors import ProtocolError
from loophole.models import Case, CaseType, LegalCode, SessionState


def make_state() -> SessionState:
    return SessionState(
        session_id="session",
        domain="privacy",
        moral_principles="Protect privacy.",
        current_code=LegalCode(version=1, text="Article 1"),
    )


class AgentProtocolTests(unittest.TestCase):
    def test_loophole_parser_requires_expected_case_count(self) -> None:
        raw = """
<scenario>
<description>Scenario one</description>
<explanation>Explanation one</explanation>
</scenario>
"""
        with self.assertRaises(ProtocolError):
            parse_loopholes(raw, make_state(), expected_count=2)

    def test_overreach_parser_requires_expected_case_count(self) -> None:
        raw = """
<scenario>
<description>Scenario one</description>
<explanation>Explanation one</explanation>
</scenario>
"""
        with self.assertRaises(ProtocolError):
            parse_overreaches(raw, make_state(), expected_count=2)

    def test_parser_returns_cases_when_contract_is_satisfied(self) -> None:
        raw = """
<scenario>
<description>Scenario one</description>
<explanation>Explanation one</explanation>
</scenario>
<scenario>
<description>Scenario two</description>
<explanation>Explanation two</explanation>
</scenario>
"""
        cases = parse_loopholes(raw, make_state(), expected_count=2)
        self.assertEqual([case.id for case in cases], [1, 2])
        self.assertEqual(cases[0].scenario, "Scenario one")
        self.assertEqual(cases[1].explanation, "Explanation two")

    def test_judge_requires_pressure_classification(self) -> None:
        judge = Judge(llm=None)  # type: ignore[arg-type]
        judge.run = lambda state, **kwargs: """
<reasoning>Conflicting scope.</reasoning>
<verdict>unresolvable</verdict>
<conflict_explanation>Need human judgment.</conflict_explanation>
"""  # type: ignore[method-assign]

        state = make_state()
        case = Case(
            id=1,
            round=1,
            case_type=CaseType.LOOPHOLE,
            scenario="Scenario one",
            explanation="Explanation one",
        )

        with self.assertRaises(ProtocolError):
            judge.evaluate(state, case)
