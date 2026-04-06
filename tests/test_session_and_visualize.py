from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from loophole.models import Case, CaseStatus, CaseType, LegalCode, SessionState
from loophole.session import SessionManager
from loophole.visualize import generate_html


class SessionAndVisualizeTests(unittest.TestCase):
    def test_session_round_trip_persists_state_and_supporting_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            initial_code = LegalCode(version=1, text="Article 1")
            state = manager.create_session("session_a", "privacy", "Protect privacy.", initial_code)
            state.cases.append(
                Case(
                    id=1,
                    round=1,
                    case_type=CaseType.LOOPHOLE,
                    scenario="scenario",
                    explanation="explanation",
                    status=CaseStatus.AUTO_RESOLVED,
                    resolution="resolution",
                    resolved_by="judge",
                )
            )
            manager.save(state)

            loaded = manager.load("session_a")
            session_dir = Path(tmpdir) / "session_a"

            self.assertEqual(loaded.current_code.text, "Article 1")
            self.assertTrue((session_dir / "state.json").exists())
            self.assertTrue((session_dir / "current_code.md").exists())
            self.assertTrue((session_dir / "case_log.md").exists())

    def test_generate_html_writes_requested_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state = SessionState(
                session_id="session_b",
                domain="privacy",
                moral_principles="Protect privacy.",
                current_code=LegalCode(version=2, text="Article 2"),
                code_history=[
                    LegalCode(version=1, text="Article 1"),
                    LegalCode(version=2, text="Article 2"),
                ],
                cases=[
                    Case(
                        id=1,
                        round=1,
                        case_type=CaseType.LOOPHOLE,
                        scenario="scenario",
                        explanation="explanation",
                        status=CaseStatus.AUTO_RESOLVED,
                        resolution="resolution",
                        resolved_by="judge",
                    )
                ],
                current_round=1,
            )

            output_path = Path(tmpdir) / "custom-report.html"
            written = generate_html(state, output_path=str(output_path))

            self.assertEqual(Path(written), output_path)
            self.assertTrue(output_path.exists())
            self.assertIn("Final Legal Code", output_path.read_text())

    def test_generate_html_uses_session_dir_style_default_when_provided(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state = SessionState(
                session_id="session_c",
                domain="privacy",
                moral_principles="Protect privacy.",
                current_code=LegalCode(version=1, text="Article 1"),
            )

            output_path = Path(tmpdir) / "custom_sessions" / "session_c" / "report.html"
            written = generate_html(state, output_path=str(output_path))

            self.assertEqual(Path(written), output_path)
            self.assertTrue(output_path.exists())

    def test_generate_html_includes_held_open_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state = SessionState(
                session_id="session_d",
                domain="privacy",
                moral_principles="Protect privacy.",
                current_code=LegalCode(version=1, text="Article 1"),
                code_history=[LegalCode(version=1, text="Article 1")],
                cases=[
                    Case(
                        id=1,
                        round=1,
                        case_type=CaseType.LOOPHOLE,
                        scenario="scenario",
                        explanation="explanation",
                        status=CaseStatus.HOLD_OPEN,
                        resolution="Need later human review.",
                        resolved_by="user",
                    )
                ],
                current_round=1,
            )

            output_path = Path(tmpdir) / "held-open-report.html"
            written = generate_html(state, output_path=str(output_path))

            self.assertEqual(Path(written), output_path)
            self.assertIn("Held open", output_path.read_text())
