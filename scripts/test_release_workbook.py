"""Regression checks for the one workbook exposed outside the Academy web root."""

from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from urllib.parse import urljoin
from zipfile import ZipFile

from validate_static_site import ROOT, public_files


WORKBOOK = Path("phase-3-what-you-are-evaluating/rag-evaluation/rag_test_cases.xlsx")
ROUTE = "/" + WORKBOOK.as_posix()
HOST = "https://llmacademy.testneural.in"
RELEASE = ROOT / "docs/audits/release-readiness-v1/RELEASE_EXECUTION_CHECKLIST.md"


class Downloads(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a" and "download" in attributes:
            self.links.append(attributes["href"])


class WorkbookRouteTests(unittest.TestCase):
    def test_homepage_download_resolves_to_the_exact_public_route(self):
        homepage = Downloads()
        homepage.feed((ROOT / "docs/index.html").read_text(encoding="utf-8"))
        for entry in ("/", "/index.html"):
            with self.subTest(entry=entry):
                links = [urljoin(HOST + entry, target) for target in homepage.links]
                self.assertEqual(links.count(HOST + ROUTE), 1)

    def test_release_stage_preserves_the_allowlisted_workbook_bytes(self):
        self.assertEqual([path for path in public_files() if path.suffix == ".xlsx"], [WORKBOOK])
        with TemporaryDirectory() as temporary:
            stage = Path(temporary)
            run = subprocess.run(
                [sys.executable, str(ROOT / "scripts/validate_static_site.py"), "--stage", str(stage)],
                cwd=ROOT, capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            copy = stage / WORKBOOK
            self.assertEqual(copy.read_bytes(), (ROOT / WORKBOOK).read_bytes())
            self.assertFalse((stage / "docs" / WORKBOOK).exists())
            with ZipFile(copy) as archive:
                self.assertIsNone(archive.testzip())
                self.assertIn("xl/workbook.xml", archive.namelist())

    def test_runbook_maps_only_the_exact_route_to_the_checkout_artifact(self):
        proposal = RELEASE.read_text(encoding="utf-8").split("`" * 3 + "nginx\n", 1)[1]
        proposal = proposal.split("`" * 3, 1)[0]
        lines = [line.strip() for line in proposal.splitlines()]
        self.assertEqual([line for line in lines if line.startswith("location ")],
                         [f"location = {ROUTE} {{"])
        self.assertEqual([line for line in lines if line.startswith("alias ")],
                         [f"alias /var/www/llm-evaluation{ROUTE};"])


if __name__ == "__main__":
    unittest.main()
