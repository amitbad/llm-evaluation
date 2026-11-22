# TestNeural LLM Academy project context

## Purpose and identity

TestNeural LLM Academy is a public learning site for self-study and instructor-led teaching. Its first course, **LLM Evaluation Engineering**, supports both focused study and a complete path from foundations through production. The academy uses the tagline **Learn • Evaluate • Build** and the credit **Developed by: Amit Baderia**. The target domain is [llmacademy.testneural.in](https://llmacademy.testneural.in/).

## Architecture and repository

The academy uses static HTML, CSS, and vanilla JavaScript. A Python standard-library generator builds two checked-in HTML pages. The homepage and published examples use local companion assets. The curriculum HTML embeds its styles, JavaScript, and data for offline use. Links to example pages and workbook downloads still need the companion files. Learners run the Python exercises separately.

| Location | Purpose |
| --- | --- |
| [MASTER_CURRICULUM.md](MASTER_CURRICULUM.md) | Authoritative curriculum, including topic IDs, dependency definitions, path membership, and hour estimates |
| [docs/generate_master_curriculum.py](docs/generate_master_curriculum.py) | Validates curriculum data and generates the homepage and interactive curriculum |
| [docs/index.html](docs/index.html), [docs/home.html](docs/home.html) | Generated homepage and compatibility entry point |
| [docs/master-curriculum.html](docs/master-curriculum.html), [homepage template](docs/templates/academy-home.html) | Standalone curriculum and homepage source template |
| [docs/assets/](docs/assets/) | Shared academy styles, behavior, and approved V1 branding under `branding/` |
| [Learning modes](docs/learning_modes.js), [roadmap](docs/learning_roadmap.js), [progress backups](docs/learning_progress.js) | JavaScript embedded in the generated curriculum |
| [docs/COURSE_AUDIT_REPORT.md](docs/COURSE_AUDIT_REPORT.md), [concepts reference](docs/concepts.html) | Course audit and published reference material |
| `docs/test*.html`, `phase-0-foundations/` through `phase-5-production-eval/` | Published example pages, existing lessons, and experiments |
| [scripts/validate_static_site.py](scripts/validate_static_site.py), [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Public file validation and general static hosting guidance |

Change curriculum definitions in Markdown and presentation in the generator, source templates, or named JavaScript and CSS sources. After editing any of these inputs, regenerate both pages, check synchronization, and validate the public file set before handing off the change.

```bash
python3 docs/generate_master_curriculum.py
python3 docs/generate_master_curriculum.py --check
python3 scripts/validate_static_site.py
```

## Navigation and progress

The homepage puts Quick Learning and Complete Course first. The homepage and curriculum share this primary order.

1. **Quick Learning** contains focused study plans and the Learning Paths comparison with all seven paths, plus the preparation checklist.
2. **Complete Course** shows the full sequence and labels preparation and electives as optional.
3. **Learning Roadmap** shows dependencies and supports SVG, PNG, and standalone HTML downloads.
4. **About the Course** contains course outcomes, hour estimates, and progress controls.
5. **Resources** links to published examples and concepts. Instructor Resources groups Existing Repository Coverage and Teaching Plan.

Both learning modes use the same topic IDs and content. Quick Learning links carry both the path and the topic in the URL fragment, so reload and browser history retain the exact lesson. The guided view temporarily moves the original topic material from Complete Course and restores it when the learner leaves. Required prerequisites appear in the lesson sequence. Complete Course keeps its existing topic links and provides module breadcrumbs.

Continue Learning opens the first unfinished required topic in order. In Quick Learning and About the Course this opens a guided lesson, while Complete Course resumes in its own view. Progress is stored in the current browser's local storage when available. It does not synchronize across devices. The versioned JSON backup transfers completed topic IDs and the optional selected path. Imports require a preview and explicit apply, with merge or replace available. Reset requires confirmation.

## Deployment and development boundaries

The production plan uses a dedicated NGINX virtual host and Let's Encrypt on the Ubuntu VPS. The approved web root is `/var/www/llm-evaluation/docs` with a public URL allowlist. The private runbook specifies a read-only GitHub deploy key and isolated SSH alias `github-llm-academy`. It places the deployment script at `/var/www/llm-evaluation.deploy.sh` and validates a temporary checkout before fast-forwarding production. The vhost files, runbook, and script are maintained outside the public checkout. Production operations require owner approval and are performed by the owner. The public homepage and curriculum served the `aa01ca7` release at `/` and `/master-curriculum.html` during website QA. See the [static hosting guidance](docs/DEPLOYMENT.md) for the release checks.

This supersedes the earlier plan to version production templates here and serve from a separate release symlink. Direct serving from the approved checkout path keeps the root in `docs/`, so checkout updates are not atomic. The production runbook records how to recover with a reviewed revert and how to restore only the academy virtual host.

Develop from local `main`, which tracks clean GitHub `origin/main`. The initial public release was published from `academy-public-release` at `aa01ca7`. The local `archive/pre-clean-main-72c2e33` branch preserves the earlier history, including retired production files. Keep that branch local and outside any public merge or push.

Keep the learning site static and publicly readable without accounts, API keys, a backend, or required remote assets. Preserve stable topic IDs, approved brand assets, and the distinction between published examples and planned lessons. Use non-browser validation for current work. The repository owner performs manual browser checks. Keep curriculum, experiment, and deployment changes within the authorized task scope. Deployment and Git staging, commits, or pushes require owner authorization.

## Required documentation maintenance

- Read this file and [PROGRESS.md](PROGRESS.md) before starting development.
- Update [PROGRESS.md](PROGRESS.md) after every meaningful milestone. Distinguish implementation, automated tests, manual verification, and pending work.
- Update this file whenever architecture, requirements, or major decisions change.
- Update [BUG_TRACKER.md](BUG_TRACKER.md) whenever an issue is discovered, fixed, or reopened.
- Keep the documentation aligned with the implementation. Preserve the decision history and document the reason when a decision is superseded.
