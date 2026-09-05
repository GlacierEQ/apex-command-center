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
