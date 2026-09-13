# Apex Command Center

Unified CLI across all APEX repos. One command center to rule them all.

## Usage

```bash
# Show status of all repos
python3 apex.py status

# Run tests across repos
python3 apex.py test
python3 apex.py test apex-core

# Search across all repos
python3 apex.py search "def merge"

# Health check all repos
python3 apex.py health

# List all engines
python3 apex.py engines

# Show statistics
python3 apex.py stats
```

## Python API

```python
from apex import CommandCenter

center = CommandCenter()

# Get status
statuses = center.status()
for s in statuses:
    print(f"{s.name}: {s.health}")

# Run tests
results = center.test("apex-core")
for r in results:
    print(f"{r.repo}: {r.passed} passed")

# Search
results = center.search("merge")
for r in results:
    print(f"[{r.repo}] {r.file}:{r.line}")

# Health check
health = center.health()
for name, checks in health.items():
    print(f"[{checks['grade']}] {name}")
```

## Data Models

- `RepoStatus` — status of a repository
- `TestResult` — result of running tests
- `SearchResult` — a search result

## Registered Repos

| Repo | Category | Engines |
|------|----------|---------|
| apex-core | foundation | config, shadowdrive, firewall |
| hyper-pipeline | pipelines | architect, forge, runner, skill, mcp, test, doc, deploy, rename, auditor, types |
| engineering-mastery | skills | skill_tree, learning_path, hierarchy_validator |
| apex-runtime | runtime | state, ci, connector, search, monitor, recovery, docs, skills, mcp |
| apex-merge | git | merge_engine |
| pipeline-architect | pipelines | architect |
| pipeline-forge | pipelines | forge |
| mega-pipeline-production | quality | audit, combo_skills |

## Testing

```bash
pytest tests/ -v
```

## License

MIT

### Machine–Mesh Protocol Manifest

<!-- glacier-eq-protocol:start -->
```yaml
{
  "schema": "glacier-eq.readme.machine-mesh/v1",
  "repository": {
    "id": "GlacierEQ/apex-command-center",
    "url": "https://github.com/GlacierEQ/apex-command-center",
    "readme_contract": "estate-machine-v1",
    "default_branch": "main"
  },
  "machine": {
    "repository_kind": "migration-residue",
    "public_api": "inspect-declared-entrypoints",
    "protocol_files": [],
    "entrypoints": [
      {
        "kind": "test-area",
        "path": "tests",
        "policy": "run-before-reliance"
      }
    ]
  },
  "presentation": {
    "architecture": [
      "recruiter",
      "master",
      "machine",
      "mesh"
    ],
    "authority": {
      "capability": "stone-psysoc-x",
      "repository": "GlacierEQ/AKOS",
      "manifest": "stones/psysoc-x/stone.json",
      "engine": "infinity_stones/psysoc_x.py"
    },
    "truth_invariant": "presentation-may-change-sequence-density-tone-and-style; facts-evidence-uncertainty-provenance-dignity-and-reader-agency-may-not"
  },
  "license": {
    "class": "NO_ROOT_LICENSE_DETECTED",
    "status": "ORIGINALITY_AND_PROVENANCE_REVIEW_REQUIRED",
    "controlling_path": null,
    "policy": "GlacierEQ/job-app-helix/LICENSE_POLICY.json",
    "may_relicense_automatically": false,
    "upstream_rights_must_be_preserved": false
  },
  "mesh": {
    "primary_home": null,
    "branch": "migration-residue",
    "subcategory": "unresolved-primary-home",
    "routing": [
      {
        "relation": "estate-map",
        "target": "GlacierEQ/monolith",
        "url": "https://github.com/GlacierEQ/monolith"
      }
    ],
    "boundaries": [
      "routing-does-not-transfer-source-code-evidence-deployment-or-lifecycle-authority",
      "generated-contract-is-a-source-index-not-a-runtime-or-provider-receipt",
      "implementation-and-provider-state-require-independent-evidence",
      "presentation-calibration-cannot-promote-claim-or-evidence-state",
      "license-automation-cannot-relicense-unresolved-upstream-or-third-party-rights"
    ]
  },
  "provenance": {
    "generated_by": "GlacierEQ/job-app-helix",
    "generator_contract": "estate-machine-v1",
    "classification_source": null,
    "classification_evidence_path": null,
    "classification_evidence_blob_sha": null,
    "classification_status": null,
    "contract_digest": "d80a71e6d338f307759e71cf6f4e116a3435fef615a049b0cd13587750bc8b52"
  }
}
```
<!-- glacier-eq-protocol:end -->
