#!/usr/bin/env python3
"""
Apex Command Center — Unified CLI Across All Repos

One command center to rule them all. Provides a single interface to
monitor, test, search, and manage the entire APEX estate.

Usage:
    python3 apex.py status          # Show status of all repos
    python3 apex.py test [repo]     # Run tests across repos
    python3 apex.py search "query"  # Search across all repos
    python3 apex.py engines         # List all engines
    python3 apex.py stats           # Show statistics
    python3 apex.py health          # Health check all repos
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


VERSION = "2.0.0"
HOME = Path.home()


# ─── Repo Registry ───────────────────────────────────────────────────────────

REPOS: Dict[str, Dict[str, Any]] = {
    "apex-core": {
        "path": str(HOME / "APEX_SYSTEM/INFRASTRUCTURE/apex-core"),
        "description": "Config, tests, security, firewall",
        "engines": ["config", "shadowdrive", "firewall"],
        "test_cmd": "python3 -m pytest tests/ -q --tb=line",
        "category": "foundation",
    },
    "hyper-pipeline": {
        "path": "/tmp/hyper-pipeline",
        "description": "13 pipeline engines",
        "engines": ["architect", "forge", "runner", "skill", "mcp", "test", "doc", "deploy", "rename", "auditor", "types"],
        "test_cmd": "python3 -m pytest tests/ -q --tb=line",
        "category": "pipelines",
    },
    "engineering-mastery": {
        "path": "/tmp/engineering-mastery",
        "description": "8 skill domains, 56 skills",
        "engines": ["skill_tree", "learning_path", "hierarchy_validator"],
        "test_cmd": "python3 -m pytest tests/ -q --tb=line",
        "category": "skills",
    },
    "apex-runtime": {
        "path": "/tmp/apex-runtime",
        "description": "8 runtime engines + MCP server",
        "engines": ["state", "ci", "connector", "search", "monitor", "recovery", "docs", "skills", "mcp"],
        "test_cmd": "python3 -m pytest tests/ -q --tb=line",
        "category": "runtime",
    },
    "apex-merge": {
        "path": "/tmp/apex-merge",
        "description": "Hyper-powerful branch merge",
        "engines": ["merge_engine"],
        "test_cmd": "python3 -m pytest tests/ -q --tb=line",
        "category": "git",
    },
    "pipeline-architect": {
        "path": "/tmp/pipeline-architect",
        "description": "Pipeline builder",
        "engines": ["architect"],
        "test_cmd": "python3 -m pytest test_architect.py -q --tb=line",
        "category": "pipelines",
    },
    "pipeline-forge": {
        "path": "/tmp/pipeline-forge",
        "description": "Template composer",
        "engines": ["forge"],
        "test_cmd": "python3 -m pytest test_forge.py -q --tb=line --timeout=10",
        "category": "pipelines",
    },
    "mega-pipeline-production": {
        "path": "/tmp/mega-pipeline-production",
        "description": "Production audit + combo skills",
        "engines": ["audit", "combo_skills"],
        "test_cmd": "python3 -m pytest tests/ -q --tb=line",
        "category": "quality",
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
    engine_count: int = 0
    category: str = ""

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
            "engine_count": self.engine_count,
            "category": self.category,
        }


@dataclass
class TestResult:
    """Result of running tests on a repo."""
    repo: str
    status: str
    passed: int = 0
    failed: int = 0
    duration_ms: float = 0.0
    output: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repo": self.repo,
            "status": self.status,
            "passed": self.passed,
            "failed": self.failed,
            "duration_ms": self.duration_ms,
            "output": self.output,
        }


@dataclass
class SearchResult:
    """A search result."""
    repo: str
    file: str
    result_type: str
    line: int = 0
    context: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repo": self.repo,
            "file": self.file,
            "type": self.result_type,
            "line": self.line,
            "context": self.context,
        }


# ─── Command Center ──────────────────────────────────────────────────────────

class CommandCenter:
    """Unified command center for all repos."""

    def __init__(self, repos: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        self.repos = repos or REPOS

    def status(self) -> List[RepoStatus]:
        """Get status of all repos."""
        statuses: List[RepoStatus] = []

        for name, config in self.repos.items():
            path = Path(config["path"])
            exists = path.exists()
            clean = True
            last_commit = ""
            engine_count = len(config.get("engines", []))
            category = config.get("category", "")

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
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass

            health = "healthy" if exists and clean else "warning"
            if not exists:
                health = "missing"

            statuses.append(RepoStatus(
                name=name,
                path=str(path),
                exists=exists,
                clean=clean,
                tests_passed=0,
                tests_failed=0,
                last_commit=last_commit,
                health=health,
                engine_count=engine_count,
                category=category,
            ))

        return statuses

    def test(self, repo_name: Optional[str] = None) -> List[TestResult]:
        """Run tests for a repo or all repos."""
        results: List[TestResult] = []

        if repo_name:
            if repo_name not in self.repos:
                return [TestResult(repo=repo_name, status="error", output="Repo not found")]
            repos = {repo_name: self.repos[repo_name]}
        else:
            repos = self.repos

        for name, config in repos.items():
            path = Path(config["path"])
            if not path.exists():
                results.append(TestResult(repo=name, status="skipped", output="Not found"))
                continue

            start = time.time()
            try:
                result = subprocess.run(
                    config["test_cmd"],
                    shell=True,
                    cwd=path,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                duration = (time.time() - start) * 1000
                output = result.stdout + result.stderr
                passed = output.count("passed")
                failed = output.count("failed") + output.count("error")

                results.append(TestResult(
                    repo=name,
                    status="passed" if result.returncode == 0 else "failed",
                    passed=passed,
                    failed=failed,
                    duration_ms=duration,
                    output=output[-300:] if len(output) > 300 else output,
                ))
            except subprocess.TimeoutExpired:
                results.append(TestResult(repo=name, status="timeout", output="Exceeded 120s"))
            except Exception as e:
                results.append(TestResult(repo=name, status="error", output=str(e)))

        return results

    def search(self, query: str) -> List[SearchResult]:
        """Search across all repos."""
        results: List[SearchResult] = []
        query_lower = query.lower()

        for name, config in self.repos.items():
            path = Path(config["path"])
            if not path.exists():
                continue

            for py_file in path.glob("**/*.py"):
                if any(part.startswith(".") or part == "__pycache__" for part in py_file.parts):
                    continue
                try:
                    content = py_file.read_text(encoding="utf-8", errors="ignore")
                    for i, line in enumerate(content.split("\n"), 1):
                        if query_lower in line.lower():
                            results.append(SearchResult(
                                repo=name,
                                file=str(py_file.relative_to(path)),
                                result_type="code",
                                line=i,
                                context=line.strip()[:100],
                            ))
                except (OSError, UnicodeDecodeError):
                    pass

        return results

    def get_engines(self) -> Dict[str, List[str]]:
        """Get all engines across repos."""
        return {name: config.get("engines", []) for name, config in self.repos.items()}

    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics."""
        total_engines = sum(len(c.get("engines", [])) for c in self.repos.values())
        categories: Dict[str, int] = {}
        for config in self.repos.values():
            cat = config.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "repos": len(self.repos),
            "engines": total_engines,
            "categories": categories,
            "repos_list": list(self.repos.keys()),
        }

    def health(self) -> Dict[str, Dict[str, Any]]:
        """Health check all repos."""
        health: Dict[str, Dict[str, Any]] = {}

        for name, config in self.repos.items():
            path = Path(config["path"])
            checks = {
                "exists": path.exists(),
                "has_readme": (path / "README.md").exists() if path.exists() else False,
                "has_tests": any(path.glob("test_*.py")) if path.exists() else False,
                "has_src": any(path.glob("**/*.py")) if path.exists() else False,
            }
            checks["score"] = sum(checks.values())
            checks["grade"] = "A" if checks["score"] >= 4 else "B" if checks["score"] >= 3 else "C"
            health[name] = checks

        return health


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description=f"Apex Command Center v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    sub = parser.add_subparsers(dest="command", help="Command to run")

    sub.add_parser("status", help="Show status of all repos")
    sub.add_parser("health", help="Health check all repos")

    test = sub.add_parser("test", help="Run tests")
    test.add_argument("repo", nargs="?", help="Repo name (optional)")

    search = sub.add_parser("search", help="Search across repos")
    search.add_argument("query", help="Search query")

    sub.add_parser("engines", help="List all engines")
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
            icon = "✓" if s.health == "healthy" else "⚠" if s.health == "warning" else "✗"
            print(f"  {icon} {s.name}: {s.health} | {s.engine_count} engines | {s.category}")
            if s.last_commit:
                print(f"    Last: {s.last_commit}")
        print(f"\nTotal: {len(statuses)} repos")

    elif args.command == "health":
        health = center.health()
        print("\n=== HEALTH CHECK ===\n")
        for name, checks in health.items():
            print(f"  [{checks['grade']}] {name}")
            print(f"    Exists: {'✓' if checks['exists'] else '✗'}")
            print(f"    README: {'✓' if checks['has_readme'] else '✗'}")
            print(f"    Tests:  {'✓' if checks['has_tests'] else '✗'}")
            print(f"    Source: {'✓' if checks['has_src'] else '✗'}")
        print()

    elif args.command == "test":
        results = center.test(args.repo)
        print("\n=== TEST RESULTS ===\n")
        for r in results:
            icon = "✓" if r.status == "passed" else "✗"
            print(f"  {icon} {r.repo}: {r.status}")
            if r.passed or r.failed:
                print(f"    Passed: {r.passed}, Failed: {r.failed}")
                print(f"    Duration: {r.duration_ms:.0f}ms")
        print()

    elif args.command == "search":
        results = center.search(args.query)
        print(f"\n=== SEARCH: {args.query} ===\n")
        for r in results:
            print(f"  [{r.repo}] {r.file}:{r.line}")
            print(f"    {r.context}")
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
        print(f"  Categories: {stats['categories']}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
