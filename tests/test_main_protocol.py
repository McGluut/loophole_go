from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest import mock

import typer

import loophole.main as main_module
from loophole.errors import ProtocolError, ProviderAuthError
from loophole.main import _assign_case_ids, _hold_open_case, _try_user_resolution
from loophole.models import Case, CaseStatus, CaseType, LegalCode, SessionState


def make_state() -> SessionState:
    return SessionState(
        session_id="session",
        domain="privacy",
        moral_principles="Protect privacy.",
        current_code=LegalCode(version=1, text="Article 1"),
    )


class DummyLegislator:
    def __init__(self, revised_text: str) -> None:
        self.revised_text = revised_text

    def revise(self, state: SessionState, case: Case) -> LegalCode:
        return LegalCode(version=state.current_code.version + 1, text=self.revised_text)


class DummyJudge:
    def __init__(self, passes: bool, details: str = "details") -> None:
        self.passes = passes
        self.details = details

    def validate(self, state: SessionState, proposed_code: str) -> SimpleNamespace:
        return SimpleNamespace(passes=self.passes, details=self.details)


class BrokenLegislator:
    def revise(self, state: SessionState, case: Case) -> LegalCode:
        raise ProtocolError("missing legal code block")

    def draft_initial(self, state: SessionState) -> LegalCode:
        raise ProtocolError("missing legal code block")


class AuthFailingLegislator:
    def draft_initial(self, state: SessionState) -> LegalCode:
        raise ProviderAuthError(
            "Provider authentication failed. Check LOOPHOLE_API_KEY or ANTHROPIC_API_KEY and try again."
        )


class MainProtocolTests(unittest.TestCase):
    def test_assign_case_ids_rewrites_batch_sequentially(self) -> None:
        state = make_state()
        cases = [
            Case(id=99, round=1, case_type=CaseType.LOOPHOLE, scenario="a", explanation="b"),
            Case(id=99, round=1, case_type=CaseType.OVERREACH, scenario="c", explanation="d"),
        ]

        assigned = _assign_case_ids(state, cases)

        self.assertEqual([case.id for case in assigned], [1, 2])

    def test_try_user_resolution_accepts_revision_when_validation_passes(self) -> None:
        state = make_state()
        prior = Case(
            id=1,
            round=1,
            case_type=CaseType.LOOPHOLE,
            scenario="prior",
            explanation="prior",
            status=CaseStatus.AUTO_RESOLVED,
            resolution="prior resolution",
            resolved_by="judge",
        )
        current = Case(
            id=2,
            round=1,
            case_type=CaseType.OVERREACH,
            scenario="current",
            explanation="current",
            status=CaseStatus.ESCALATED,
        )
        state.cases.extend([prior, current])

        accepted, details = _try_user_resolution(
            state,
            current,
            "Allow emergency exception.",
            DummyLegislator("Article 1 revised"),
            DummyJudge(True),
        )

        self.assertTrue(accepted)
        self.assertIn("v2", details)
        self.assertEqual(state.current_code.text, "Article 1 revised")
        self.assertEqual(current.status, CaseStatus.USER_RESOLVED)
        self.assertEqual(state.user_clarifications[-1], "[Case #2] Allow emergency exception.")

    def test_try_user_resolution_rolls_back_failed_revision(self) -> None:
        state = make_state()
        prior = Case(
            id=1,
            round=1,
            case_type=CaseType.LOOPHOLE,
            scenario="prior",
            explanation="prior",
            status=CaseStatus.AUTO_RESOLVED,
            resolution="prior resolution",
            resolved_by="judge",
        )
        current = Case(
            id=2,
            round=1,
            case_type=CaseType.OVERREACH,
            scenario="current",
            explanation="current",
            status=CaseStatus.ESCALATED,
        )
        state.cases.extend([prior, current])

        accepted, details = _try_user_resolution(
            state,
            current,
            "Break the previous rule.",
            DummyLegislator("Article 1 conflicting"),
            DummyJudge(False, "Conflicts with Case #1."),
        )

        self.assertFalse(accepted)
        self.assertEqual(details, "Conflicts with Case #1.")
        self.assertEqual(state.current_code.text, "Article 1")
        self.assertEqual(len(state.code_history), 0)
        self.assertEqual(current.status, CaseStatus.ESCALATED)
        self.assertEqual(state.user_clarifications, [])

    def test_escalate_turns_protocol_error_into_clean_exit(self) -> None:
        state = make_state()
        current = Case(
            id=2,
            round=1,
            case_type=CaseType.OVERREACH,
            scenario="current",
            explanation="current",
            status=CaseStatus.ESCALATED,
        )

        with mock.patch.object(main_module, "_get_multiline_input", return_value="decision"):
            with mock.patch.object(main_module.Prompt, "ask", return_value="resolve now"):
                with self.assertRaises(typer.Exit):
                    main_module._escalate(
                        state,
                        current,
                        "conflict",
                        BrokenLegislator(),
                        DummyJudge(True),
                    )

    def test_escalate_records_pressure_metadata_on_case(self) -> None:
        state = make_state()
        current = Case(
            id=2,
            round=1,
            case_type=CaseType.OVERREACH,
            scenario="current",
            explanation="current",
            status=CaseStatus.ESCALATED,
        )

        with mock.patch.object(main_module, "_get_multiline_input", return_value="decision"):
            with mock.patch.object(main_module.Prompt, "ask", return_value="resolve now"):
                with mock.patch.object(
                    main_module,
                    "_try_user_resolution",
                    return_value=(True, "Code updated -> v2"),
                ):
                    main_module._escalate(
                        state,
                        current,
                        "conflict",
                        DummyLegislator("Article 1 revised"),
                        DummyJudge(True),
                        pressure_kind="principle_tension",
                        pressure_reason="The case forces a choice between two stated commitments.",
                    )

        self.assertEqual(current.pressure_kind, "principle_tension")
        self.assertEqual(
            current.pressure_reason,
            "The case forces a choice between two stated commitments.",
        )

    def test_hold_open_case_marks_case_without_revising_code(self) -> None:
        current = Case(
            id=2,
            round=1,
            case_type=CaseType.OVERREACH,
            scenario="current",
            explanation="current",
            status=CaseStatus.ESCALATED,
        )

        _hold_open_case(current, "Need a second pass on the principles.")

        self.assertEqual(current.status, CaseStatus.HOLD_OPEN)
        self.assertEqual(current.resolution, "Need a second pass on the principles.")
        self.assertEqual(current.resolved_by, "user")

    def test_new_turns_initial_draft_protocol_error_into_clean_exit(self) -> None:
        with mock.patch.object(main_module, "_load_config", return_value={"session_dir": "sessions"}):
            with mock.patch.object(
                main_module,
                "_build_agents",
                return_value={"legislator": BrokenLegislator()},
            ):
                with mock.patch.object(main_module, "_get_multiline_input", return_value="Protect privacy."):
                    with self.assertRaises(typer.Exit):
                        main_module.new(domain="privacy", principles_file=None)

    def test_new_turns_initial_draft_auth_error_into_clean_exit(self) -> None:
        with mock.patch.object(main_module, "_load_config", return_value={"session_dir": "sessions"}):
            with mock.patch.object(
                main_module,
                "_build_agents",
                return_value={"legislator": AuthFailingLegislator()},
            ):
                with mock.patch.object(main_module, "_get_multiline_input", return_value="Protect privacy."):
                    with self.assertRaises(typer.Exit):
                        main_module.new(domain="privacy", principles_file=None)
