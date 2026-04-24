from __future__ import annotations

from pathlib import Path

import pytest

from codebase_rag.utils.path_utils import should_skip_path


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("")
    (tmp_path / "src" / ".DS_Store").write_text("")
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist" / "bundle.js").write_text("")
    (tmp_path / "vendor").mkdir()
    (tmp_path / "vendor" / "lib.py").write_text("")
    (tmp_path / "vendor" / "keep.py").write_text("")
    (tmp_path / ".env").write_text("")
    (tmp_path / ".env.local").write_text("")
    (tmp_path / ".env.production").write_text("")
    (tmp_path / ".env.example").write_text("")
    (tmp_path / "cert.pem").write_text("")
    (tmp_path / "README.md").write_text("")
    return tmp_path


def test_no_excludes_keeps_regular_files(repo: Path) -> None:
    assert should_skip_path(repo / "src" / "main.py", repo) is False


def test_dir_exclude_skips_children(repo: Path) -> None:
    excludes = frozenset({"vendor"})
    assert should_skip_path(repo / "vendor" / "lib.py", repo, excludes) is True


def test_dir_exclude_does_not_affect_sibling(repo: Path) -> None:
    excludes = frozenset({"vendor"})
    assert should_skip_path(repo / "src" / "main.py", repo, excludes) is False


def test_basename_glob_matches_file_anywhere(repo: Path) -> None:
    excludes = frozenset({".DS_Store"})
    assert should_skip_path(repo / "src" / ".DS_Store", repo, excludes) is True


def test_glob_pattern_matches_dotted_variants(repo: Path) -> None:
    excludes = frozenset({".env.*"})
    assert should_skip_path(repo / ".env.local", repo, excludes) is True
    assert should_skip_path(repo / ".env.production", repo, excludes) is True


def test_glob_pattern_does_not_match_base_name(repo: Path) -> None:
    excludes = frozenset({".env.*"})
    assert should_skip_path(repo / ".env", repo, excludes) is False


def test_extension_glob_matches(repo: Path) -> None:
    excludes = frozenset({"*.pem"})
    assert should_skip_path(repo / "cert.pem", repo, excludes) is True


def test_basename_unignore_whitelists_file(repo: Path) -> None:
    excludes = frozenset({".env.*"})
    unignores = frozenset({".env.example"})
    assert should_skip_path(repo / ".env.example", repo, excludes, unignores) is False
    assert should_skip_path(repo / ".env.local", repo, excludes, unignores) is True


def test_directory_exclude_beats_basename_unignore(repo: Path) -> None:
    (repo / "dist" / ".env.example").write_text("")
    excludes = frozenset({"dist"})
    unignores = frozenset({".env.example"})
    assert (
        should_skip_path(repo / "dist" / ".env.example", repo, excludes, unignores)
        is True
    )


def test_path_unignore_restores_subtree_of_ignore_pattern(repo: Path) -> None:
    (repo / "node_modules").mkdir()
    (repo / "node_modules" / "keep.py").write_text("")
    (repo / "node_modules" / "drop.py").write_text("")
    unignores = frozenset({"node_modules/keep.py"})
    assert (
        should_skip_path(repo / "node_modules" / "keep.py", repo, None, unignores)
        is False
    )
    assert (
        should_skip_path(repo / "node_modules" / "drop.py", repo, None, unignores)
        is True
    )


def test_trailing_slash_stripped_entries_still_match(repo: Path) -> None:
    excludes = frozenset({"dist"})
    assert should_skip_path(repo / "dist" / "bundle.js", repo, excludes) is True


def test_suffix_ignore_always_wins(repo: Path) -> None:
    pyc = repo / "src" / "main.pyc"
    pyc.write_text("")
    assert should_skip_path(pyc, repo) is True


def test_directory_itself_excluded(repo: Path) -> None:
    excludes = frozenset({"vendor"})
    assert should_skip_path(repo / "vendor", repo, excludes) is True
