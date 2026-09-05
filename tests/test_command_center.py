#!/usr/bin/env python3
"""
Tests for Apex Command Center.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from apex import (
    CommandCenter, RepoStatus, TestResult, SearchResult,
    REPOS, VERSION,
)


class TestRepoStatus:
    def test_create(self):
        status = RepoStatus(
            name="test-repo",
            path="/tmp/test",
            exists=True,
            clean=True,
            tests_passed=10,
            tests_failed=0,
        )
        assert status.name == "test-repo"
        assert status.exists is True

    def test_to_dict(self):
        status = RepoStatus(
            name="test-repo",
            path="/tmp/test",
            exists=True,
            clean=True,
            tests_passed=10,
            tests_failed=0,
        )
        d = status.to_dict()
        assert d["name"] == "test-repo"
        assert d["exists"] is True


class TestTestResult:
    def test_create(self):
        result = TestResult(repo="test", status="passed", passed=10, failed=0)
        assert result.repo == "test"
        assert result.passed == 10

    def test_to_dict(self):
        result = TestResult(repo="test", status="passed", passed=10, failed=0)
        d = result.to_dict()
        assert d["repo"] == "test"
        assert d["passed"] == 10


class TestSearchResult:
    def test_create(self):
        result = SearchResult(repo="test", file="test.py", result_type="code", line=10)
        assert result.repo == "test"
        assert result.line == 10

    def test_to_dict(self):
        result = SearchResult(repo="test", file="test.py", result_type="code", line=10)
        d = result.to_dict()
        assert d["repo"] == "test"
        assert d["line"] == 10


class TestCommandCenter:
    def test_init(self):
        center = CommandCenter()
        assert len(center.repos) > 0

    def test_status(self):
        center = CommandCenter()
        statuses = center.status()
        assert len(statuses) > 0
        assert all(isinstance(s, RepoStatus) for s in statuses)

    def test_get_engines(self):
        center = CommandCenter()
        engines = center.get_engines()
        assert len(engines) > 0

    def test_get_stats(self):
        center = CommandCenter()
        stats = center.get_stats()
        assert stats["repos"] > 0
        assert stats["engines"] > 0

    def test_search(self):
        center = CommandCenter()
        results = center.search("def")
        assert isinstance(results, list)

    def test_health(self):
        center = CommandCenter()
        health = center.health()
        assert len(health) > 0


class TestRepos:
    def test_repos_registry(self):
        assert len(REPOS) > 0
        for name, config in REPOS.items():
            assert "path" in config
            assert "engines" in config
            assert "test_cmd" in config

    def test_version(self):
        assert VERSION == "2.0.0"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
