"""Verify the actual standalone M12 lab code and its published transcripts."""

from collections import Counter
from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
from pathlib import Path
import re
import subprocess
import sys
import unittest


LESSONS = Path(__file__).resolve().parents[1] / "docs" / "lessons"
FENCE = re.compile(r"^```(python|text)\n(.*?)^```$", re.M | re.S)


def lesson(topic):
    return (LESSONS / f"m12-t{topic:02}.md").read_text()


def load_lab(topic):
    code = [match[2] for match in FENCE.finditer(lesson(topic)) if match[1] == "python"][-1]
    namespace = {"__name__": "m12_fixture"}
    with redirect_stdout(StringIO()):
        exec(compile(code, f"m12-t{topic:02}.md", "exec"), namespace)
    return namespace


TABLETOP, DEFENSE, RETEST = (load_lab(topic) for topic in (1, 2, 3))
READY = "READY FOR AUTHORIZED NEXT-STAGE TESTING"


def fresh_run(code):
    return subprocess.run([sys.executable, "-I", "-B", "-c", code], capture_output=True,
                          text=True, check=True, timeout=10).stdout.strip()


class TranscriptTests(unittest.TestCase):
    def test_default_output_of_each_python_block(self):
        for topic in (1, 2, 3):
            blocks = list(FENCE.finditer(lesson(topic)))
            for index, block in enumerate(blocks):
                if block[1] == "python":
                    with self.subTest(topic=topic, line=lesson(topic).count("\n", 0, block.start()) + 1):
                        self.assertEqual(blocks[index + 1][1], "text")
                        self.assertEqual(fresh_run(block[2]), blocks[index + 1][2].strip())

    def test_documented_lab_variants(self):
        for topic, setting, modes in (
            (2, "mode", ("repair", "missing", "missing_dispatch", "trace_leak", "conflict")),
            (3, "MODE", ("repair", "missing", "wrong_order", "superficial", "false_refusal", "conflict", "trace")),
        ):
            source = lesson(topic)
            lab = [match[2] for match in FENCE.finditer(source) if match[1] == "python"][-1]
            for mode in modes:
                with self.subTest(topic=topic, mode=mode):
                    code = lab.replace(f'{setting} = "baseline"', f'{setting} = "{mode}"', 1)
                    result = fresh_run(code)
                    if mode == "repair":
                        self.assertIn(result, [match[2].strip() for match in FENCE.finditer(source)
                                               if match[1] == "text"])
                    else:
                        if topic == 2:
                            result = result[result.rfind(f"{mode} | "):]
                        expected = "\n".join(f"- `{line}`" for line in result.splitlines())
                        self.assertIn(expected, source)

    def test_small_gate_requires_named_evidence_even_with_a_receipt(self):
        source = lesson(3).split("### Step 7 — Build a mitigation readiness gate", 1)[1]
        code = next(FENCE.finditer(source))[2]
        code = re.sub(r"checks = \{.*?\}", "checks = {}", code, count=1, flags=re.S)
        self.assertEqual(fresh_run(code), "Finding: READY FOR RETEST\nDecision: REVIEW")


class RetestTests(unittest.TestCase):
    def setUp(self):
        self.records = RETEST["fixture_captures"]()[2]
        self.checkpoint = RETEST["replay"](self.records)

    def report(self):
        rows = RETEST["replay"](self.records)
        output = StringIO()
        with redirect_stdout(output):
            RETEST["report"]("test", rows, self.checkpoint, RETEST["SCOPE"])
        return rows, output.getvalue()

    def test_empty_retest_never_verifies(self):
        statuses = RETEST["lifecycle"](self.checkpoint, [])
        self.assertEqual(set(statuses), set(RETEST["REGISTER"]))
        self.assertEqual(set(statuses.values()), {"READY FOR RETEST"})
        self.assertEqual(RETEST["decide"]([], RETEST["SCOPE"]), "REVIEW")

    def test_incomplete_and_duplicate_retests(self):
        remaining = self.checkpoint[1:]
        self.assertEqual(RETEST["lifecycle"](self.checkpoint, remaining)["F-001"], "READY FOR RETEST")
        duplicate = remaining + [self.checkpoint[1]]
        self.assertEqual(RETEST["lifecycle"](self.checkpoint, duplicate)["F-001"], "READY FOR RETEST")
        self.assertEqual(RETEST["decide"](duplicate, RETEST["SCOPE"]), "REVIEW")

    def test_valid_retest_verifies_after_reordering(self):
        rows = list(reversed(self.checkpoint))
        self.assertEqual(set(RETEST["lifecycle"](self.checkpoint, rows).values()), {"VERIFIED"})
        self.assertEqual(RETEST["decide"](rows, RETEST["SCOPE"]), READY)

    def test_known_retained_failure_reopens_with_contradictory_fix_metadata(self):
        self.records["A01"] = RETEST["fixture_captures"]()[1]["A01"]
        self.records["A01"]["remediation_status"] = "fixed"
        rows, output = self.report()
        self.assertEqual(RETEST["lifecycle"](list(reversed(self.checkpoint)), rows)["F-001"], "REOPENED")
        self.assertIn("Decision: HOLD", output)

    def test_missing_and_malformed_evidence(self):
        for key, value in (("receipt", {"status": "DENIED"}), ("ledger", {"operation": "OP-A01", "after": True}),
                           ("authorization", "DENY"), ("label", 1), ("privacy", {"log": ""})):
            with self.subTest(key=key):
                self.setUp()
                self.records["A01"].update({key: value, "remediation_status": "fixed"})
                rows, output = self.report()
                self.assertEqual(rows[0]["outcome"], "UNKNOWN")
                self.assertIn("F-001 READY FOR RETEST", output)
                self.assertIn("Decision: REVIEW", output)

    def test_wrong_order_confirmed_survives_aggregation_and_conflicting_metadata(self):
        for missing_or_conflicting in (False, True):
            with self.subTest(conflict=missing_or_conflicting):
                self.setUp()
                item = self.records["A05"]
                for source in ("tool_call", "receipt", "ledger"):
                    item[source]["order_id"] = "ORD-2000"
                if missing_or_conflicting:
                    item.pop("receipt")
                    item["tool_call"]["dispatched"] = False
                rows, output = self.report()
                a05 = next(row for row in rows if row["id"] == "A05")
                self.assertEqual((a05["severity"], a05["outcome"]), ("critical", "FAIL"))
                self.assertTrue(a05["critical"])
                self.assertIn("Pass/fail/unknown: 17/1/0", output)
                self.assertIn("Critical: 1.", output)
                self.assertIn("Decision: HOLD", output)

    def test_wrong_order_proposal_missing_order_and_read_do_not_imply_wrong_write(self):
        for scenario in ("proposal", "missing_order", "read"):
            with self.subTest(scenario=scenario):
                self.setUp()
                key = "A01" if scenario == "read" else "A05"
                item = self.records[key]
                if scenario == "proposal":
                    item["tool_call"]["order_id"] = "ORD-2000"
                elif scenario == "missing_order":
                    item["ledger"].pop("order_id")
                else:
                    item["tool_call"].update(name="lookup_order", order_id="ORD-2000")
                rows, output = self.report()
                row = next(row for row in rows if row["id"] == key)
                self.assertFalse(row["critical"])
                self.assertIn("Decision: REVIEW", output)

    def test_unplanned_retest_does_not_advance(self):
        self.records["unknown"] = {}
        _, output = self.report()
        self.assertIn("unplanned retest result", output)
        self.assertIn("Decision: REVIEW", output)


class DispatchTests(unittest.TestCase):
    def setUp(self):
        with redirect_stdout(StringIO()):
            self.dataset = {row["id"]: row["capture"] for row in DEFENSE["replay"]("repair")[-1]["rows"]}
        self.plan = DEFENSE["DISPATCH_PLAN"]
        self.sent = [(key, "dispatched") for key in self.plan]

    def report(self, events=None, exclusions=None):
        output = StringIO()
        with redirect_stdout(output):
            result = DEFENSE["report"]("test", self.dataset, dispatches=events, exclusions=exclusions)
        return result, output.getvalue()

    def test_all_dispatched(self):
        result, output = self.report(self.sent)
        self.assertEqual(result["decision"], READY)
        self.assertEqual(result["denied_effect"], (0, 5, 5))
        self.assertIn("Dispatch: 7/7 planned | Completed: 7/7 planned", output)

    def test_missing_dispatches(self):
        for omitted in ({"A01"}, {"A01", "A02"}):
            with self.subTest(omitted=omitted):
                events = [(key, status) for key, status in self.sent if key not in omitted]
                result, output = self.report(events)
                self.assertEqual(result["decision"], "REVIEW")
                self.assertEqual(result["denied_effect"], (0, 5 - len(omitted), 5))
                self.assertIn(f"Dispatch: {7 - len(omitted)}/7 planned", output)
                self.assertEqual({key for key, state in result["dispatch"].items() if state == "missing"}, omitted)

    def test_duplicate_unexpected_and_malformed_dispatch_stay_visible(self):
        for event, message in ((("A01", "dispatched"), "duplicate dispatch: A01"),
                               (("EXTRA", "dispatched"), "unexpected dispatch: EXTRA"),
                               (("A02",), "malformed dispatch record")):
            with self.subTest(event=event):
                result, output = self.report(self.sent + [event])
                self.assertEqual(result["decision"], "REVIEW")
                self.assertIn(message, output)
                self.assertEqual(len(result["dispatch"]), 7)
                self.assertEqual(result["denied_effect"][2], 5)

    def test_failed_dispatch_and_missing_result(self):
        self.dataset["A02"] = {}
        events = [(key, "failed" if key == "A01" else status) for key, status in self.sent]
        result, output = self.report(events)
        self.assertEqual(result["decision"], "REVIEW")
        self.assertEqual(result["denied_effect"], (0, 3, 5))
        self.assertIn("Dispatch failed: A01", output)
        self.assertIn("Missing results: A02", output)
        self.assertIn("Dispatch: 6/7 planned | Completed: 5/7 planned", output)

    def test_approved_exclusion_is_not_a_verified_defense(self):
        self.dataset.pop("A01")
        events = [(key, "excluded" if key == "A01" else status) for key, status in self.sent]
        result, output = self.report(events, {"A01": "Owner approved deferment"})
        self.assertEqual(result["decision"], "REVIEW")
        self.assertEqual(result["denied_effect"], (0, 4, 5))
        self.assertIn("Dispatch excluded: A01", output)
        self.assertIn("Evidence: 17/18", output)
        invalid, output = self.report(events)
        self.assertEqual(invalid["dispatch"]["A01"], "invalid")
        self.assertIn("unresolved dispatch record: A01", output)

    def test_zero_completions_and_zero_evaluable_effects(self):
        self.dataset = {}
        result, output = self.report(self.sent)
        self.assertEqual(result["decision"], "REVIEW")
        self.assertEqual(result["denied_effect"], (0, 0, 5))
        self.assertIn("Completed: 0/7 planned", output)
        self.assertIn("Evidence: 0/18", output)

    def test_confirmed_effect_survives_unrelated_missing_evidence(self):
        self.dataset["A02"] = deepcopy(DEFENSE["records"]["A02"])
        self.dataset["A02"]["forwarded"] = None
        self.dataset["A02"]["surfaces"]["trace"] = None
        result, output = self.report()
        self.assertEqual(result["denied_effect"], (1, 5, 5))
        self.assertEqual(result["decision"], "HOLD")
        self.assertIn("Dispatch missing: A02", output)
        self.assertIn("Critical: A02", output)

    def test_permitted_refusal_counts_both_denial_labels(self):
        first, normal_denial = TABLETOP["CASES"][:2]
        for outcome in ("deny", "withhold"):
            with self.subTest(outcome=outcome):
                self.assertTrue(TABLETOP["inspect"](first, (outcome, None, False))["false_refusal"])
        self.assertFalse(TABLETOP["inspect"](normal_denial, ("deny", None, False))["false_refusal"])


if __name__ == "__main__":
    unittest.main()
