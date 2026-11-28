"""Regression tests for the Batch 2 lessons and preparation workflow."""

import dis
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import CodeType
import unittest


ROOT = Path(__file__).resolve().parents[1]
FENCE = re.compile(r"^```(bash|python|text)\n(.*?)^```$", re.M | re.S)


def blocks(path):
    return [match.groups() for match in FENCE.finditer((ROOT / path).read_text())]


def python_run(code, *args, cwd=ROOT):
    return subprocess.run([sys.executable, "-I", "-B", "-c", code, *args], cwd=cwd,
                          capture_output=True, text=True, timeout=10)


def referenced_globals(code):
    names = {step.argval for step in dis.get_instructions(code) if step.opname == "LOAD_GLOBAL"}
    for nested in code.co_consts:
        if isinstance(nested, CodeType):
            names.update(referenced_globals(nested))
    return names


JUDGE_BLOCKS = blocks("docs/lessons/m18-t01.md")
JUDGE_CODE = next(code for language, code in reversed(JUDGE_BLOCKS) if language == "python")


class JudgeIndependenceTests(unittest.TestCase):
    def setUp(self):
        self.lab = {"__name__": "judge_fixture"}
        exec(compile(JUDGE_CODE, "m18-t01.md", "exec"), self.lab)

    def assess(self, snapshot, labels, calibration_judge="repaired"):
        lab = self.lab
        stats = lab["calibration"](lab["calibration_rows"](calibration_judge), lab["THRESHOLD"], calibration_judge)
        return lab["assess"](lab["REQUESTS"], snapshot, labels, lab["CRITICAL_CASES"], stats)

    def test_scoring_changes_with_reference_without_changing_capture(self):
        predict = self.lab["prediction_snapshot"]
        baseline = predict("repaired")
        labels = self.lab["REFERENCES"]
        original = self.assess(baseline, labels)
        self.lab["REFERENCES"] = {**labels, "A01": "BLOCK"}
        regenerated = predict("repaired")
        changed = self.assess(regenerated, self.lab["REFERENCES"])
        self.assertEqual(regenerated, baseline)
        self.assertEqual((original["correct"], changed["correct"], changed["scored"]), (12, 11, 12))
        self.assertEqual(changed["metrics"]["matrix"], [[4, 0], [1, 7]])
        self.assertEqual(changed["cases"][0]["raw"], original["cases"][0]["raw"])
        self.assertEqual(changed["cases"][0]["verdict"], "PASS")

    def test_prediction_path_and_its_helpers_work_without_any_reference_globals(self):
        predict = self.lab["prediction_snapshot"]
        before = {version: predict(version) for version in self.lab["FROZEN_VERDICTS"]}
        for name in ("REFERENCES", "CRITICAL_CASES", "EVIDENCE", "CALIBRATION_CORRECT"):
            del self.lab[name]
        for version, snapshot in before.items():
            regenerated = predict(version)
            self.assertEqual(regenerated, snapshot)
            payload = json.dumps({"judge": version, "raw": regenerated["raw"]}, sort_keys=True)
            self.assertEqual(regenerated["sha256"], hashlib.sha256(payload.encode()).hexdigest())
        for function in ("prediction_snapshot", "capture"):
            globals_used = referenced_globals(self.lab[function].__code__)
            self.assertTrue(globals_used <= {"zip", "CASE_ORDER", "FROZEN_VERDICTS", "capture",
                                             "json", "sha256", "dict", "DIMENSIONS"}, globals_used)

    def test_missing_references_affect_coverage_and_stale_calibration_routes_review(self):
        snapshot = self.lab["prediction_snapshot"]("repaired")
        empty = self.assess(snapshot, {})
        self.assertEqual((empty["scored"], empty["planned"], empty["decision"]), (0, 12, "REVIEW"))
        self.assertEqual(len([row for row in empty["cases"] if row["verdict"] in ("PASS", "BLOCK")]), 12)
        stale = self.assess(snapshot, self.lab["REFERENCES"], "v2")
        self.assertEqual((stale["scored"], stale["calibration_matches"], stale["decision"]),
                         (12, False, "REVIEW"))

    def test_all_judge_transcripts_and_json_are_deterministic(self):
        for index, (language, code) in enumerate(JUDGE_BLOCKS):
            if language == "python":
                with self.subTest(block=index):
                    run = python_run(code)
                    self.assertEqual(run.returncode, 0, run.stderr)
                    self.assertEqual(run.stdout, JUDGE_BLOCKS[index + 1][1])
        export = JUDGE_CODE.replace("EXPORT_JSON = False", "EXPORT_JSON = True", 1)
        first, second = python_run(export), python_run(export)
        self.assertEqual((first.returncode, second.returncode), (0, 0))
        self.assertEqual(first.stdout, second.stdout)


class DefenseTransferTests(unittest.TestCase):
    def test_history_control_changes_only_with_trusted_provenance(self):
        lesson = (ROOT / "docs/lessons/m12-t02.md").read_text().split("### Run a retained-history control", 1)[1]
        example = list(FENCE.finditer(lesson))
        code, expected = example[0][2], example[1][2]
        replay = python_run(code)
        self.assertEqual(replay.returncode, 0, replay.stderr)
        self.assertEqual(replay.stdout, expected)
        revised = python_run(code.replace('"  VERIFIED  "', '"VeRiFiEd"'))
        self.assertEqual(revised.returncode, 0, revised.stderr)
        self.assertEqual(revised.stdout, expected)
        missing = python_run(code.replace('{"e3": "verification-record"}', '{}'))
        self.assertEqual(missing.returncode, 0, missing.stderr)
        self.assertIn("held-out-legitimate: REVIEW expected=ALLOW", missing.stdout.split("provenance check: on")[1])


class PreparationTests(unittest.TestCase):
    def test_prepare_run_and_recover_from_relative_path_error(self):
        samples = blocks("docs/preparation.md")
        fixtures = next(code for lang, code in samples if lang == "bash" and code.startswith("cat >"))
        checker = next(code for lang, code in samples if lang == "python")
        expected = [code.strip() for lang, code in samples if lang == "text"]
        with TemporaryDirectory() as workspace:
            temp = Path(workspace)
            subprocess.run(["sh", "-c", fixtures], cwd=temp, check=True, timeout=10)
            script = temp / "check_capture.py"
            script.write_text(checker)
            outcomes = []
            for case_name in ("case.jsonl", "cases.jsonl"):
                results = subprocess.run([sys.executable, "-I", "-B", str(script), case_name],
                                         cwd=temp, text=True, capture_output=True, timeout=10)
                outcomes.append((results.returncode, (results.stdout or results.stderr).strip()))
            self.assertEqual(outcomes, [(1, expected[0]), (0, expected[1])])

    def test_trace_replay_requires_no_export_service(self):
        page = (ROOT / "docs/lessons/m14-t01.md").read_text()
        self.assertLess(page.index("### Replay and diagnose without a service"), page.index("python -m pip install"))
        _, code = next((language, code) for language, code in blocks("docs/lessons/m14-t01.md") if language == "python")
        for mode, outcome, expected_steps in (
            ("replay", "FAIL_MISSING_REQUIRED_SEARCH", ["lookup_account_status"]),
            ("repair", "PASS_SEARCH_AND_SAFE_ESCALATION", ["lookup_account_status", "search_docs"]),
        ):
            with self.subTest(mode=mode):
                result = python_run(code, "--mode", mode, "--no-export")
                self.assertEqual(result.returncode, 0, result.stderr)
                observation = json.loads(result.stdout)
                self.assertIsNone(observation["trace_id"])
                self.assertEqual((observation["outcome"], observation["path"]), (outcome, expected_steps))
        failure = python_run(code, "--mode", "repair", "--no-export", "--inject-lookup-error")
        self.assertEqual((failure.returncode, failure.stdout), (1, ""))
        self.assertEqual(failure.stderr.strip(), "Lab stopped: Account lookup failed. Finalization stopped.")
        with TemporaryDirectory() as elsewhere:
            wrong_dir = python_run(code, "--mode", "replay", "--no-export", cwd=elsewhere)
            self.assertEqual(wrong_dir.returncode, 1)
            self.assertIn("Check dependencies and repository inputs", wrong_dir.stderr)

    def test_concepts_distinguishes_a_valid_score_from_missing_evidence(self):
        page = (ROOT / "docs/concepts.html").read_text()
        archive = page.split('id="metric-calibration"', 1)[1].split("</main>", 1)[0]
        for phrase in ("timeout-affected values", "do not\n        isolate calibration",
                       "measured score", "execution error", "unscorable", "false refusal", "not applicable"):
            self.assertIn(phrase, archive)
        self.assertIn('href="master-curriculum.html#m09-t02"', archive)
        self.assertIn('href="master-curriculum.html#m11-t01"', archive)


if __name__ == "__main__":
    unittest.main()
