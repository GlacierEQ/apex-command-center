#!/usr/bin/env python3
"""
Apex Command Center — Unified CLI Across All Repos
One command center to rule them all.

Usage:
    python3 apex.py status          # Show status of all repos
    python3 apex.py test [repo]     # Run tests across repos
    python3 apex.py search "query"  # Search across all repos
    python3 apex.py monitor         # Health check all repos
    python3 apex.py skill list      # List all skills
    python3 apex.py pipeline list   # List all pipelines
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


VERSION = "1.0.0"
HOME = Path.home()

# ─── Repo Registry ───────────────────────────────────────────────────────────

REPOS = {
    "apex-core": {
        "path": str(HOME / "APEX_SYSTEM/INFRASTRUCTURE/apex-core"),
        "description": "Config, tests, security",
        "engines": ["config", "tests", "security"],
        "test_cmd": "python3 -m pytest tests/ -q --tb=line",
    },
    "hyper-pipeline": {
        "path": "/tmp/hyper-pipeline",
        "description": "9 pipeline engines",
        "engines": ["architect", "forge", "runner", "skill", "mcp", "test", "doc", "deploy", "rename"],
        "test_cmd": "python3 -m pytest tests/ -q --tb=line",
    },
    "engineering-mastery": {
        "path": "/tmp/engineering-mastery",
        "description": "Skill trees, learning paths",
        "engines": ["skill_tree", "learning_path", "progress"],
        "test_cmd": "python3 -m pytest tests/ -q --tb=line",
    },
    "apex-runtime": {
        "path": "/tmp/apex-runtime",
        "description": "8 runtime engines",
        "engines": ["state", "ci", "connector", "search", "monitor", "recovery", "docs", "skills"],
        "test_cmd": "python3 -m pytest tests/ -q --tb=line",
    },
    "pipeline-architect": {
        "path": "/tmp/pipeline-architect",
        "description": "Pipeline builder",
        "engines": ["architect"],
        "test_cmd": "python3 -m pytest test_architect.py -q --tb=line",
    },
    "pipeline-forge": {
        "path": "/tmp/pipeline-forge",
        "description": "Template composer",
        "engines": ["forge"],
        "test_cmd": "python3 -m pytest test_forge.py -q --tb=line --timeout=10",
    },
    "mega-pipeline-production": {
        "path": "/tmp/mega-pipeline-production",
        "description": "Production audit",
        "engines": ["audit", "compliance", "telemetry", "gpu", "f35", "ew", "swarm"],
        "test_cmd": "python3 -m pytest test_utils.py test_pipeline.py test_integration.py test_production.py -q --tb=line",
    },
}


# ─── Data Models ─────────────────────────────────────────────────────────────

@dataclass
class RepoStatus:
    """Status of a repository."""
    name: str
    path: str
    exists: bool
    clean: bool
    tests_passed: int
    tests_failed: int
    last_commit: str = ""
    health: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "exists": self.exists,
            "clean": self.clean,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "last_commit": self.last_commit,
            "health": self.health,
        }


# ─── Command Center ──────────────────────────────────────────────────────────

class CommandCenter:
    """Unified command center for all repos."""

    def __init__(self) -> None:
        self.repos = REPOS

    def status(self) -> List[RepoStatus]:
        """Get status of all repos."""
        statuses = []
        for name, config in self.repos.items():
            path = Path(config["path"])
            exists = path.exists()

            clean = True
            last_commit = ""
            if exists:
                try:
                    result = subprocess.run(
                        ["git", "status", "--porcelain"],
                        cwd=path,
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    clean = not result.stdout.strip()

                    result = subprocess.run(
                        ["git", "log", "-1", "--format=%s"],
                        cwd=path,
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    last_commit = result.stdout.strip()
                except Exception:
                    pass

            statuses.append(RepoStatus(
                name=name,
                path=str(path),
                exists=exists,
                clean=clean,
                tests_passed=0,
                tests_failed=0,
                last_commit=last_commit,
                health="healthy" if exists and clean else "warning",
            ))

        return statuses

    def test(self, repo_name: Optional[str] = None) -> Dict[str, Any]:
        """Run tests for a repo or all repos."""
        results = {}

        if repo_name:
            repos = {repo_name: self.repos[repo_name]} if repo_name in self.repos else {}
        else:
            repos = self.repos

        for name, config in repos.items():
            path = Path(config["path"])
            if not path.exists():
                results[name] = {"status": "skipped", "reason": "not found"}
                continue

            try:
                result = subprocess.run(
                    config["test_cmd"],
                    shell=True,
                    cwd=path,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                output = result.stdout + result.stderr
                passed = output.count("passed")
                failed = output.count("failed") + output.count("error")

                results[name] = {
                    "status": "passed" if result.returncode == 0 else "failed",
                    "passed": passed,
                    "failed": failed,
                    "output": output[-200:] if len(output) > 200 else output,
                }
            except subprocess.TimeoutExpired:
                results[name] = {"status": "timeout", "reason": "exceeded 120s"}
            except Exception as e:
                results[name] = {"status": "error", "reason": str(e)}

        return results

    def search(self, query: str) -> List[Dict[str, str]]:
        """Search across all repos."""
        results = []
        query_lower = query.lower()

        for name, config in self.repos.items():
            path = Path(config["path"])
            if not path.exists():
                continue

            # Search Python files
            for py_file in path.glob("**/*.py"):
                if any(part.startswith(".") or part == "__pycache__" for part in py_file.parts):
                    continue
                try:
                    content = py_file.read_text(encoding="utf-8", errors="ignore")
                    if query_lower in content.lower():
                        results.append({
                            "repo": name,
                            "file": str(py_file.relative_to(path)),
                            "type": "code",
                        })
                except Exception:
                    pass

            # Search markdown files
            for md_file in path.glob("**/*.md"):
                if any(part.startswith(".") for part in md_file.parts):
                    continue
                try:
                    content = md_file.read_text(encoding="utf-8", errors="ignore")
                    if query_lower in content.lower():
                        results.append({
                            "repo": name,
                            "file": str(md_file.relative_to(path)),
                            "type": "docs",
                        })
                except Exception:
                    pass

        return results

    def get_engines(self) -> Dict[str, List[str]]:
        """Get all engines across repos."""
        engines = {}
        for name, config in self.repos.items():
            engines[name] = config["engines"]
        return engines

    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics."""
        total_repos = len(self.repos)
        total_engines = sum(len(c["engines"]) for c in self.repos.values())

        return {
            "repos": total_repos,
            "engines": total_engines,
            "repos_list": list(self.repos.keys()),
        }


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description=f"Apex Command Center v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    sub = parser.add_subparsers(dest="command", help="Command to run")

    # Status
    sub.add_parser("status", help="Show status of all repos")

    # Test
    test = sub.add_parser("test", help="Run tests")
    test.add_argument("repo", nargs="?", help="Repo name (optional)")

    # Search
    search = sub.add_parser("search", help="Search across repos")
    search.add_argument("query", help="Search query")

    # Engines
    sub.add_parser("engines", help="List all engines")

    # Stats
    sub.add_parser("stats", help="Show statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    center = CommandCenter()

    if args.command == "status":
        statuses = center.status()
        print("\n=== APEX STATUS ===\n")
        for s in statuses:
            icon = "✓" if s.exists and s.clean else "⚠"
            print(f"  {icon} {s.name}: {'exists' if s.exists else 'missing'} | {'clean' if s.clean else 'modified'}")
            if s.last_commit:
                print(f"    Last: {s.last_commit}")
        print(f"\nTotal: {len(statuses)} repos")

    elif args.command == "test":
        results = center.test(args.repo)
        print("\n=== TEST RESULTS ===\n")
        for name, result in results.items():
            icon = "✓" if result["status"] == "passed" else "✗"
            print(f"  {icon} {name}: {result['status']}")
            if "passed" in result:
                print(f"    Passed: {result['passed']}, Failed: {result['failed']}")
        print()

    elif args.command == "search":
        results = center.search(args.query)
        print(f"\n=== SEARCH: {args.query} ===\n")
        for r in results:
            print(f"  [{r['repo']}] {r['file']} ({r['type']})")
        print(f"\nTotal: {len(results)} results")

    elif args.command == "engines":
        engines = center.get_engines()
        print("\n=== ALL ENGINES ===\n")
        for repo, engine_list in engines.items():
            print(f"  {repo}: {', '.join(engine_list)}")
        print()

    elif args.command == "stats":
        stats = center.get_stats()
        print("\n=== STATISTICS ===\n")
        print(f"  Repos: {stats['repos']}")
        print(f"  Engines: {stats['engines']}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
