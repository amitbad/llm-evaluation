# V1.0 deployment verification

**Local staging passed. Public parity failed.** Production release and VPS changes require the owner and the existing private runbook. No deployment, server login, configuration edit, reload or cache purge was performed for this assessment.

## Observed public HTTPS results

The read-only sweep used certificate-verified HTTPS and checked all 85 allowlisted URLs. Eighty responses matched the candidate byte for byte, four served older versions and one returned 404. The homepage at `/` also matched the candidate. All 53 lesson address files returned 200 and matched local bytes. Those files forward into the generated course, so a successful response for the alias does not establish lesson publication.

| URL | HTTP | Observed versus the candidate |
| --- | --- | --- |
| [Curriculum](https://llmacademy.testneural.in/master-curriculum.html) | 200 | Exact bytes of `97f04a1`. Public SHA-256 `9a99e01160d5be438e10f8ef1556a46c87d53ff70743dee23c3621f4a0c4e8e3`. Candidate SHA-256 `49956fcaf9e39bc29f09f7bdb8c78718ef7313443583e28707f72cb767fd0391`. |
| [M18-T01](https://llmacademy.testneural.in/lesson-m18-t01.html) | 200 | The alias matches and points to the public master document. Its M18-T01 material has one outline and zero Python blocks. The candidate material has four Python blocks and no outline. |
| [Concept reference](https://llmacademy.testneural.in/concepts.html) | 200 | Matches the bytes at `97f04a1`, before the Batch 2 concepts correction. |
| [Shared CSS](https://llmacademy.testneural.in/assets/academy.css) and [standalone reader](https://llmacademy.testneural.in/assets/lesson-reader.js) | 200 each | Match the bytes at `97f04a1`. The generated public curriculum also embeds the older reader. |
| [Full results](https://llmacademy.testneural.in/full-results.html) | 200 | Matches the candidate. |
| [Allowlisted RAG workbook](https://llmacademy.testneural.in/phase-3-what-you-are-evaluating/rag-evaluation/rag_test_cases.xlsx) | 404 | Public workbook URL fails. Local file is a valid XLSX in the staged set. Expected SHA-256 `24e5b7d4ead7536c7d8cfd79834355b6ddca4af67b17cbd120899372ac4a320c`. |

Public and local roadmap data are byte-identical. Both contain 18 modules, 53 topic IDs and seven paths. Two nonpublic probes, `/PROJECT_CONTEXT.md` and `/preparation.md`, returned 404. That checks those paths only. The curriculum response reported NGINX, Last-Modified and ETag, with no Cache-Control, Age or CF-Cache-Status header in the recorded response. This comparison establishes what was served, with origin configuration and cache behavior still to verify.

## Preflight for the operator

1. Finish browser and teaching acceptance on the reviewed candidate. Record the intended revision, prior known-good revision, approved static manifest, reviewers and rollback owner. Keep the identified public workbook mapping in scope. A Git push updates the repository. Release requires the separate approved origin operation.
2. Validate the generated files with the repository checks. Stage into a fresh directory outside the checkout using `python3 scripts/validate_static_site.py --stage <empty-directory>`. The candidate produced 85 matching files in two temporary stages. The staging layout is for verification. Production's documented web root remains `/var/www/llm-evaluation/docs`.
3. Use the private VPS runbook and isolated read-only deploy key. Confirm the dedicated HTTPS virtual host, certificate, public URL allowlist and explicit workbook mapping. Keep the workbook mapping narrow. Leave other virtual hosts and services untouched. Record `nginx -t` for any approved NGINX configuration change before reload. Neither the live VPS checkout nor the private runbook was inspected in this assessment.
4. Direct serving from the production checkout makes the documented update non-atomic. Use the existing temporary-checkout validation before fast-forwarding. Plan a release window and immediate verification. Check cache headers and origin revision when served bytes differ. Revalidate only Academy URLs using the approved cache procedure if necessary.

Follow [static deployment guidance](../../DEPLOYMENT.md) and the [project's production boundaries](../../../PROJECT_CONTEXT.md#deployment-and-development-boundaries).

## Read-only post-deployment probes

Run from the approved candidate checkout. The file comparisons make a version mismatch visible even when the URL returns 200.

```bash
base=https://llmacademy.testneural.in
check_dir=$(mktemp -d)
workbook=phase-3-what-you-are-evaluating/rag-evaluation/rag_test_cases.xlsx

curl -fsSL -D "$check_dir/curriculum.headers" \
  "$base/master-curriculum.html" -o "$check_dir/curriculum.html" &&
cmp docs/master-curriculum.html "$check_dir/curriculum.html" &&
curl -fsSL "$base/lesson-m18-t01.html" -o "$check_dir/m18-t01.html" &&
cmp docs/lesson-m18-t01.html "$check_dir/m18-t01.html" &&
curl -fsSL "$base/$workbook" -o "$check_dir/rag.xlsx" &&
cmp "$workbook" "$check_dir/rag.xlsx"
```

Repeat the public file sweep for all allowlisted paths, including the concepts reference, shared CSS and standalone reader. Inspect HTTPS response headers and compare fresh bytes with the approved manifest. Open M18-T01 in both learning modes and after a reload. Check the four blocks, voice loading, routes, exports and workbook download. Verify the analytics loader and owner opt-out using the documented browser and dashboard procedure. Analytics delivery and dashboard telemetry were outside this assessment.

## Rollback criteria

If the authored lesson, workbook, critical navigation or static assets fail after release, pause the V1.0 announcement and have the owner investigate against the manifest. Use the private runbook's reviewed revert to the prior known-good Academy revision or restore only the Academy virtual host when configuration caused the failure. Revalidate NGINX before any approved reload and repeat the HTTPS and browser smoke checks against the recorded rollback revision. Record the failed revision, served hashes, observed cause, rollback result and retest owner.
