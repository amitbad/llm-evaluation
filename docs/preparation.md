## Prepare for your first terminal replay

Use this optional packet before a lesson asks you to save a script or read a captured request. You will work in a new temporary directory with fictional data and a Python 3.11+ interpreter. These commands use a POSIX shell such as macOS Terminal, Linux Bash, or a Linux shell in WSL. The core beginner lessons still work in the online editor.

### P01 — Make a scratch directory

The shell remembers a current working directory. Running `pwd` prints it. The first two commands make a new empty directory and move your shell into it. Keep this window open for the rest of the packet.

```bash
PREP_DIR="$(mktemp -d)"
cd "$PREP_DIR"
pwd
python3 --version
```

Your directory name will vary. Check that `pwd` shows the new directory. If your shell can't find `python3`, install an appropriate Python interpreter before continuing. A filename such as `cases.jsonl` is relative to the directory printed by `pwd`.

### P04 and P05 — Save two small input files

Copy this block into your scratch shell. `cat` writes the text between the opening line and the closing marker to the named file. Keep each JSONL object on its own line. The JSON capture records a request method and path, response status and body. It is a saved file. Reading it sends no HTTP request.

```bash
cat > cases.jsonl <<'CASES'
{"id":"correct","expected":"30 days"}
{"id":"wrong","expected":"30 days"}
{"id":"unavailable","expected":"30 days"}
CASES
cat > captures.json <<'CAPTURES'
{
  "correct": {"request": {"method": "GET", "path": "/fixture/refund"}, "response": {"status": 200, "body": "30 days"}},
  "wrong": {"request": {"method": "GET", "path": "/fixture/refund"}, "response": {"status": 200, "body": "90 days"}},
  "unavailable": {"request": {"method": "GET", "path": "/fixture/refund"}, "response": {"status": 503, "body": null}}
}
CAPTURES
```

A JSON object maps field names to values. In JSONL, each line is a separate object. In `captures.json`, the `status` belongs to the saved HTTP response. The `body` shows what the service returned when a response was available. A real request may include headers such as Content-Type. Keep credentials out of saved training records.

### P02 and P03 — Run a supplied script

Copy the Python block into a plain-text file named `check_capture.py` in the scratch directory. `Path.read_text()` reads a file. `json.loads()` decodes its contents. A loop reads one JSONL line at a time. The function `evaluate` checks transport first, then compares any successful response with the independent expected value. An `assert` checks that the three known fixtures cover all three outcomes.

```python
import json
from pathlib import Path
import sys


def evaluate(response, expected):
    if response["status"] != 200:
        return "REQUEST_ERROR"
    return "PASS" if response["body"] == expected else "FAIL"


case_file = Path(sys.argv[1])
if not case_file.is_file():
    raise SystemExit(f"Missing input: {case_file}. Check pwd and the file name.")
captures = json.loads(Path("captures.json").read_text(encoding="utf-8"))
outcomes = set()
for line in case_file.read_text(encoding="utf-8").splitlines():
    case = json.loads(line)
    capture = captures[case["id"]]
    request, response = capture["request"], capture["response"]
    decision = evaluate(response, case["expected"])
    outcomes.add(decision)
    print(case["id"], request["method"], request["path"], response["status"], decision)
assert outcomes == {"PASS", "FAIL", "REQUEST_ERROR"}
```

Run the supplied script with the misspelling first. The argument after the script is the case-file name Python looks for.

```bash
python3 check_capture.py case.jsonl
```

```text
Missing input: case.jsonl. Check pwd and the file name.
```

Run `pwd` and `ls`, then use the plural name shown in the listing.

```bash
python3 check_capture.py cases.jsonl
```

```text
correct GET /fixture/refund 200 PASS
wrong GET /fixture/refund 200 FAIL
unavailable GET /fixture/refund 503 REQUEST_ERROR
```

The wrong case received a successful HTTP response with an incorrect answer. The unavailable case has no answer to grade. Explain which case goes to the quality owner and which goes to the service owner. For a JSONL check, duplicate a line in a scratch copy and remove its closing brace. Predict which statement reads the invalid line and why this is different from a decoded object missing a required field.

After you can repair the path and explain the three results, move to the [offline trace replay](#m14-t01). That lab uses the same principles with a saved trace and a repository-relative file.
