"""Validate generated academy pages and prepare an allowlisted static release."""

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGE_DIR = ROOT / "docs"
PUBLIC_ASSETS = (
    "academy.css", "academy.js", "branding/academy-logo-banner.png",
    "branding/academy-logo-banner.svg", "branding/academy-icon.svg",
    "branding/icon-48.png", "branding/favicon.ico", "branding/icon-32.png",
    "branding/icon-180.png",
)
EXERCISES = (
    "phase-1-first-experiments/results/full_results.html",
    "phase-3-what-you-are-evaluating/rag-evaluation/rag_test_cases.xlsx",
)
VIRTUAL_ROUTES = re.compile(r"roadmap-(?:[a-g]|full)$")


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.dependencies = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.add(attributes["id"])
        if tag == "a" and "href" in attributes:
            self.links.append(attributes["href"])
        if tag == "link" and "href" in attributes and attributes.get("rel") != "canonical":
            self.dependencies.append(attributes["href"])
        if tag in {"script", "img", "iframe", "source"} and "src" in attributes:
            self.dependencies.append(attributes["src"])


def public_files():
    pages = ["index.html", "home.html", "master-curriculum.html", "concepts.html"] + [
        path.name for path in sorted(PAGE_DIR.glob("test*.html")) if re.fullmatch(r"test\d+\.html", path.name)
    ]
    return sorted(
        [Path("docs") / name for name in pages]
        + [Path("docs/assets") / name for name in PUBLIC_ASSETS]
        + [Path(name) for name in EXERCISES]
    )


def validate():
    subprocess.run([sys.executable, str(PAGE_DIR / "generate_master_curriculum.py"), "--check"], check=True)
    files = public_files()
    pages = {}
    for relative in files:
        path = ROOT / relative
        if not path.is_file() or not path.stat().st_size or path.resolve() != path:
            raise ValueError(f"Missing, empty or symlinked public file: {relative}")
        if path.suffix == ".html":
            page = Page()
            page.feed(path.read_text(encoding="utf-8"))
            pages[relative] = page

    for relative, page in pages.items():
        for link, embedded in [(link, False) for link in page.links] + [(link, True) for link in page.dependencies]:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                if embedded and url.scheme != "data":
                    raise ValueError(f"Remote dependency in {relative}: {link}")
                continue
            local = unquote(url.path)
            destination = (ROOT / relative.parent / local).resolve().relative_to(ROOT) if local else relative
            if destination not in files:
                raise ValueError(f"Unpublished link in {relative}: {link}")
            fragment = unquote(url.fragment)
            if fragment and destination in pages and fragment not in pages[destination].ids:
                if destination != Path("docs/master-curriculum.html") or not VIRTUAL_ROUTES.fullmatch(fragment):
                    raise ValueError(f"Missing link target in {relative}: {link}")
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, help="Copy validated files into a new or empty release directory")
    args = parser.parse_args()
    try:
        files = validate()
        if args.stage:
            stage = args.stage.resolve()
            if stage == ROOT or ROOT in stage.parents or stage in ROOT.parents:
                raise ValueError("Stage outside the source repository")
            stage.mkdir(parents=True, exist_ok=True)
            if any(stage.iterdir()):
                raise ValueError("Release staging directory is not empty")
            for relative in files:
                destination = stage / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, destination)
        print(f"Academy static site validated ({len(files)} public files).")
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Static site validation failed: {error}\n")


if __name__ == "__main__":
    main()
