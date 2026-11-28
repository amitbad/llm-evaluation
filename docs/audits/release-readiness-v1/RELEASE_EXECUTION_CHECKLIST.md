# V1.0 release execution checklist

**Owner-run only. Current status · NO-GO.** Browser acceptance, human teaching review and the beginner pilot are pending. The workbook route still returns 404 and public M18-T01 still shows the outline. This checklist prepares commands for a scheduled release after sign-off.

## Freeze the candidate and stage the package

The verified serving snapshot is commit `a260e3a76af9e14033013187a6c402857be16d18`. Its public files are identical to the earlier tested `3cd4ddb` snapshot. This is an identified candidate awaiting human approval. The final acceptance commit adds reports and a test. If it is the deployment target, pin its full SHA and confirm public-file parity before sign-off.

From a clean review checkout of the intended candidate, in Bash:

```bash
set -euo pipefail
tested=a260e3a76af9e14033013187a6c402857be16d18
candidate=$(git rev-parse HEAD)
reference=$(mktemp -d)
stage=$(mktemp -d)
git archive "$tested" | tar -xf - -C "$reference"
(cd "$reference" && python3 scripts/validate_static_site.py --stage "$reference.public")
python3 docs/generate_master_curriculum.py --check
python3 scripts/validate_static_site.py --stage "$stage"
diff -qr "$reference.public" "$stage"
printf 'Candidate %s\nStaged files %s\n' "$candidate" "$stage"
```

The stage contains 85 files. Pages and assets retain their `docs/` paths and the workbook retains its repository-relative path. Record the stage, candidate SHA, actual manual results and approval. Production serves `/var/www/llm-evaluation/docs` directly using the existing private workflow. The temporary stage is verification evidence.

For desktop acceptance, start a loopback preview of the allowlisted stage and manually open `http://127.0.0.1:8000/docs/`. Use an approved private preview with the same staged bytes for physical mobile devices.

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory "$stage"
```

## Workbook evidence and proposed correction

- **Existing URL:** `/phase-3-what-you-are-evaluating/rag-evaluation/rag_test_cases.xlsx`.
- **Expected destination:** `/var/www/llm-evaluation/phase-3-what-you-are-evaluating/rag-evaluation/rag_test_cases.xlsx`.
- The homepage download resolves to that exact URL. Local validation, staging and XLSX integrity all pass. The workbook SHA-256 is `24e5b7d4ead7536c7d8cfd79834355b6ddca4af67b17cbd120899372ac4a320c`. A new public GET during acceptance preparation returned HTTP 404, consistent with the [readiness assessment](DEPLOYMENT_VERIFICATION.md).
- The workbook is outside the document root, so normal static lookup from `docs/` cannot reach it. The effective production mapping failure is confirmed. Whether the live cause is an absent or wrong mapping, a missing or unreadable VPS file, or a stale response still needs origin inspection. The local site already uses the correct route and artifact. No local URL or static-file relocation is needed.

Inspect the Academy HTTPS vhost and file first using the private runbook. If a mapping is absent or wrong, add or correct this exact location inside the existing `llmacademy.testneural.in` HTTPS server block. If a correct location exists, check its destination, worker access and origin response before editing it. Keep the rest of the allowlist and other vhosts intact. [NGINX location and alias directives](https://nginx.org/en/docs/http/ngx_http_core_module.html#alias)

```nginx
location = /phase-3-what-you-are-evaluating/rag-evaluation/rag_test_cases.xlsx {
    alias /var/www/llm-evaluation/phase-3-what-you-are-evaluating/rag-evaluation/rag_test_cases.xlsx;
    types { application/vnd.openxmlformats-officedocument.spreadsheetml.sheet xlsx; }
}
```

The checked-in test exercises the homepage URL, the staged XLSX bytes, and this exact proposed route and destination. It cannot verify the private vhost. [Workbook regression tests](../../../scripts/test_release_workbook.py)

## Back up and deploy on the VPS

Follow the [production boundaries](../../../PROJECT_CONTEXT.md#deployment-and-development-boundaries) and [static hosting guidance](../../DEPLOYMENT.md). Use the Academy deploy account and its isolated read-only GitHub configuration. The owner supplies the approved SHA and identifies the actual vhost file from the private runbook. Run each block in the same Bash session. Stop if the deployment script, vhost, path or expected revision differs.

```bash
set -euo pipefail
app=/var/www/llm-evaluation
workbook=phase-3-what-you-are-evaluating/rag-evaluation/rag_test_cases.xlsx
read -r -p 'Approved full candidate SHA: ' candidate
read -r -p 'Confirmed Academy HTTPS vhost source file: ' vhost
test -n "$candidate"
vhost=$(sudo readlink -f -- "$vhost")
sudo test -f "$vhost"
test -r /var/www/llm-evaluation.deploy.sh
test -z "$(git -C "$app" status --porcelain)"
prior=$(git -C "$app" rev-parse HEAD)
test "$(git -C "$app" ls-remote --exit-code origin refs/heads/main | cut -f1)" = "$candidate"
backup=$(sudo mktemp -d /var/backups/llm-academy-v1.XXXXXX)
sudo cp -p -- "$vhost" "$backup/academy-vhost.conf"
printf '%s\n' "$prior" "$candidate" | sudo tee "$backup/revisions.txt" >/dev/null
backup_paths=(docs)
if git -C "$app" cat-file -e "$prior:$workbook"; then
  backup_paths+=("$workbook")
fi
git -C "$app" archive "$prior" -- "${backup_paths[@]}" | sudo tee "$backup/prior-static-source.tar" >/dev/null
sudo nginx -t
printf 'Backup %s\nPrior %s\nCandidate %s\n' "$backup" "$prior" "$candidate"
```

Record the backup path. Run the existing script as the Academy deploy account with the private runbook's environment. Its documented workflow validates a temporary checkout and fast-forwards the production checkout. Coordinate a release window and keep main stable while it runs. Confirm the deployed SHA before proceeding.

```bash
bash /var/www/llm-evaluation.deploy.sh
test "$(git -C "$app" rev-parse HEAD)" = "$candidate"
test -r "$app/$workbook"
(cd "$app" && python3 docs/generate_master_curriculum.py --check)
```

If the workbook mapping needs the proposed edit, make that isolated edit now. Check configuration and reload only for an approved change.

```bash
sudoedit "$vhost"
sudo nginx -t
sudo systemctl reload nginx
```

Verify the origin whether or not a configuration edit was needed. Use the origin listener address confirmed in the private runbook if it differs from loopback.

```bash
curl -fsS --resolve llmacademy.testneural.in:443:127.0.0.1 \
  "https://llmacademy.testneural.in/$workbook" | cmp - "$app/$workbook"
```

The direct checkout update is non-atomic. If these checks fail after the script starts, suspend release and follow rollback below.

## Public probes and F-001 closure

Check origin bytes first if the public response is stale. Inspect `Age`, `ETag`, `Last-Modified`, and `CF-Cache-Status` when present. Where a proxy cache is active and confirmed stale, purge only the affected Academy URLs using the approved cache procedure. Include the canonical workbook if its 404 was cached. Verify with a fresh browser profile and fresh GETs to the canonical URLs. [Cloudflare URL purge](https://developers.cloudflare.com/cache/how-to/purge-cache/purge-by-single-file/)

From the approved checkout:

```bash
set -euo pipefail
base=https://llmacademy.testneural.in
probe=$(mktemp -d)
workbook=phase-3-what-you-are-evaluating/rag-evaluation/rag_test_cases.xlsx
for file in master-curriculum.html lesson-m18-t01.html concepts.html assets/academy.css assets/lesson-reader.js; do
  curl -fsS --proto '=https' -D "$probe/${file##*/}.headers" "$base/$file" -o "$probe/${file##*/}"
  cmp "docs/$file" "$probe/${file##*/}"
done
curl -fsS --proto '=https' -D "$probe/workbook.headers" "$base/$workbook" -o "$probe/workbook.xlsx"
cmp "$workbook" "$probe/workbook.xlsx"
python3 - "$probe/master-curriculum.html" <<'PY'
from pathlib import Path
import sys

for filename in ("docs/master-curriculum.html", sys.argv[1]):
    html = Path(filename).read_text(encoding="utf-8")
    body = html.split('id="material-m18-t01"', 1)[1].split('id="material-m18-t02"', 1)[0]
    assert "Lesson outline.</strong>" not in body, filename
    assert body.count('class="language-python"') == 4, filename
    print(f"{filename} has the complete M18-T01 lesson")
PY
```

During this assessment, the local curriculum SHA-256 was `49956fcaf9e39bc29f09f7bdb8c78718ef7313443583e28707f72cb767fd0391`. It has four M18-T01 Python blocks and no outline. The public curriculum returned 200 with SHA-256 `9a99e01160d5be438e10f8ef1556a46c87d53ff70743dee23c3621f4a0c4e8e3`. The M18-T01 alias returned 200 and matched the local alias, but the public target has the outline and zero blocks. **F-001 remains open.**

After deployment, compare all allowlisted files, open M18-T01 in Quick Learning and Complete Course, and walk the previous and next lessons. Use the homepage workbook button to download and open the expected file. Record HTTP status, response hashes, revision and browser results. Recheck analytics if the owner includes it in production acceptance. Close F-001 only once public content and navigation pass.

## Rollback with Academy-only scope

- If the vhost edit caused the incident, restore the saved Academy config in the same VPS session. Confirm `$backup` and `$vhost` from the release record before copying.

```bash
sudo cp -p -- "$backup/academy-vhost.conf" "$vhost"
sudo nginx -t
sudo systemctl reload nginx
```

- If the static revision caused the incident, prepare a reviewed rollback on a **separate, clean Academy checkout** at the exact deployed candidate. Restore tracked content from the recorded previous SHA and make a forward commit. Land it through the approved owner workflow, then repeat the pinned deployment checks using the rollback commit. If main has advanced, arrange a reviewed revert through the private runbook instead of using this exact-tree procedure.

```bash
set -euo pipefail
read -r -p 'Recorded deployed SHA: ' deployed
read -r -p 'Recorded previous SHA: ' prior
test -z "$(git status --porcelain)"
test "$(git rev-parse HEAD)" = "$deployed"
git switch -c academy-v1-rollback
git restore --source="$prior" --staged --worktree -- .
git diff --cached --exit-code "$prior" --
git diff --cached --stat
python3 docs/generate_master_curriculum.py --check
python3 scripts/validate_static_site.py
git commit -m "Restore prior Academy serving snapshot"
```

Verify the rollback against the recorded previous revision, including HTTPS and workbook behavior. Restoring the prior version can reinstate the original blockers. Keep the release announcement paused and record the actual restored revision and any remaining checks.

## Preparation verification

| Check | Observed result |
| --- | --- |
| `python3 scripts/test_release_workbook.py -v` | 3 passed. The homepage link preserves the exact route, the staged XLSX matches byte for byte and opens as a valid archive, and the proposed mapping targets one file. |
| Generator, static validation and experiment coverage | All passed. The validator checked 85 public files. The pin and stage commands produced byte-identical packages in temporary directories. Experiment coverage found all 15 experiments mapped with zero unresolved paths. |
| `node --test scripts/test*.cjs` | 87 passed, zero failures and skips. |
| Existing audit Python suites | 19 M12, 8 Batch 2 and 7 Batch 3 tests passed. |
| Checklist command review | All nine Bash code blocks passed syntax checking. Only local staging and verification commands ran. Browser checks, VPS commands, the actual NGINX mapping and the rollback procedure await owner execution. |
| Public HTTPS snapshot | Workbook 404. M18-T01 alias 200, but the public lesson body is the outline. Local body comparison passed with four blocks. |
