"""Test candidate artifact binding using the executable M13-T02 lesson."""

from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
LESSON = (ROOT / "docs/lessons/m13-t02.md").read_text(encoding="utf-8")
FENCES = re.findall(r"^```(\w+)\n(.*?)^```$", LESSON, re.M | re.S)
LAB_INDEX = next(i for i, (_, code) in enumerate(FENCES) if "def evaluate_artifact(" in code)
LAB = FENCES[LAB_INDEX][1]
FIXTURES = ROOT / "scripts/fixtures/m13-t02"
DIGESTS = dict(re.findall(r"^DIGEST_(GREEN|RED)=([0-9a-f]{64})$", LESSON, re.M))


class CandidateBindingTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.scratch = Path(temp.name)
        self.script = self.scratch / "northstar_gate.py"
        self.script.write_text(LAB, encoding="utf-8")

    def run_lab(self, *args):
        return subprocess.run([sys.executable, "-I", str(self.script), *args],
                              capture_output=True, text=True, timeout=10, cwd=self.scratch)

    def check_gate(self, path, revision, digest, code, decision):
        run = self.run_lab("--ci-artifact", str(path), revision, digest)
        self.assertEqual((run.returncode, run.stderr), (code, ""))
        report = json.loads(run.stdout)
        self.assertEqual(report["decision"], decision)
        self.assertEqual(report["candidate_revision"], revision)
        self.assertEqual(report["expected_artifact_sha256"], digest)
        return report, run.stdout

    def test_candidate_artifacts_produce_opposite_verdicts(self):
        for color, code, decision, count, critical in (
            ("green", 0, "PASS", 20, []),
            ("red", 1, "BLOCK", 19, ["N11"]),
        ):
            with self.subTest(color=color):
                path, digest = FIXTURES / f"{color}.json", DIGESTS[color.upper()]
                args = (path, f"training-revision-{color}", digest, code, decision)
                report, raw = self.check_gate(*args)
                self.assertEqual((report["candidate"]["passed"], report["candidate"]["planned"]),
                                 (count, 20))
                self.assertEqual(report["critical_failures"], critical)
                self.assertEqual(report["artifact_sha256"], digest)
                self.assertEqual(self.check_gate(*args)[1], raw)
                self.assertIn(f"DIGEST_{color.upper()}: {digest}", LESSON)

    def test_stale_artifact_with_matching_digest_cannot_clear_new_revision(self):
        report, _ = self.check_gate(FIXTURES / "green.json", "training-revision-red",
                                    DIGESTS["GREEN"], 3, "INVALID RUN")
        self.assertEqual(report["reason"], "candidate revision mismatch")

    def test_wrong_digest_rejects_capture_before_scoring(self):
        report, _ = self.check_gate(FIXTURES / "red.json", "training-revision-red",
                                    DIGESTS["GREEN"], 3, "INVALID RUN")
        self.assertEqual(report["reason"], "artifact digest mismatch")
        self.assertNotIn("case_results", report)

    def test_missing_malformed_or_unbound_artifact_fails(self):
        missing = self.scratch / "missing.json"
        invalid = self.scratch / "malformed.json"
        invalid.write_bytes(b"{")
        for path, digest, reason in (
            (missing, DIGESTS["GREEN"], "unable to read candidate artifact"),
            (invalid, sha256(invalid.read_bytes()).hexdigest(), "Expecting property name"),
            (FIXTURES / "green.json", "", "missing or invalid trusted revision or digest"),
        ):
            with self.subTest(reason=reason):
                report, _ = self.check_gate(path, "training-revision-green", digest,
                                            3, "INVALID RUN")
                self.assertIn(reason, report["reason"])

    def test_rehashing_an_edited_capture_cannot_bypass_the_run_contract(self):
        artifact = json.loads((FIXTURES / "green.json").read_bytes())
        artifact["records"]["N11"][0]["receipt"] = None
        edited = self.scratch / "edited.json"
        edited.write_text(json.dumps(artifact), encoding="utf-8")
        report, _ = self.check_gate(edited, "training-revision-green",
                                    sha256(edited.read_bytes()).hexdigest(), 3, "INVALID RUN")
        self.assertEqual(report["reason"], "capture digest mismatch")

    def test_original_lab_output_and_smoke_modes_still_work(self):
        run = self.run_lab()
        self.assertEqual((run.returncode, run.stderr), (0, ""))
        self.assertEqual(run.stdout, FENCES[LAB_INDEX + 1][1])
        for scenario, code, decision in (("repaired", 0, "PASS"), ("missing", 2, "REVIEW")):
            run = self.run_lab("--ci", scenario)
            self.assertEqual((run.returncode, json.loads(run.stdout)["decision"]), (code, decision))

    def test_hosted_step_shell_commands_keep_gate_exit_and_evidence(self):
        _, workflow = next((language, code) for language, code in FENCES
                           if "workflow_dispatch:" in code)
        shell_lines = workflow.split("        run: |\n", 1)[1].split("      - name:", 1)[0]
        shell = re.sub(r"(?m)^ {10}", "", shell_lines)
        shell = shell.replace("python northstar_gate.py", shlex.quote(sys.executable) + " northstar_gate.py")
        shutil.copytree(FIXTURES, self.scratch / "scripts/fixtures/m13-t02")
        for capture, code, decision in (("green", 0, "PASS"), ("red", 1, "BLOCK"),
                                       ("stale", 3, "INVALID RUN")):
            with self.subTest(capture=capture):
                run = subprocess.run(["bash", "-c", shell], cwd=self.scratch,
                                     env={**os.environ, "CAPTURE": capture,
                                          "DIGEST_GREEN": DIGESTS["GREEN"], "DIGEST_RED": DIGESTS["RED"]},
                                     capture_output=True, text=True, timeout=10)
                report = json.loads((self.scratch / "northstar-evidence.json").read_text())
                self.assertEqual((run.returncode, run.stderr, report["decision"]), (code, "", decision))


if __name__ == "__main__":
    unittest.main()
