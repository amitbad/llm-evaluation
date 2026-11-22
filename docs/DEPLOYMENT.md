# Static hosting and release checks

TestNeural LLM Academy is a static site. Serve the academy homepage, curriculum, published lesson examples, and their assets directly from the web server. The learning interface needs no backend, database, or build service.

## Validate a release

From the repository root, run the generator and check for synchronization before committing the generated pages. The validator also checks that local links and embedded assets resolve within the public file set.

```bash
python3 docs/generate_master_curriculum.py
python3 docs/generate_master_curriculum.py --check
python3 scripts/validate_static_site.py
```

For a host that serves a separate release directory, the validator can copy the allowlisted files to an empty directory outside the checkout. Paths are preserved so relative links, including the two published exercise downloads, continue to work.

```bash
python3 scripts/validate_static_site.py --stage /path/to/empty-release-directory
```

## Public file boundary

Expose only the pages, assets, and two exercise downloads accepted by the validator. A web server serving directly from `docs/` needs an explicit URL allowlist and exact mappings for the exercise downloads. Keep site configuration, deployment scripts, SSH keys, certificate material, and internal project files private.

Production uses a dedicated NGINX virtual host and Let's Encrypt. Operators keep the VPS runbook and deployment files outside this repository. Validate NGINX before a reload, verify the academy over HTTPS after a release, and record the release revision for rollback.
