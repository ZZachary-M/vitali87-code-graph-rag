from fnmatch import fnmatch
from pathlib import Path

from .. import constants as cs


def _dir_excluded(
    rel_path_str: str,
    dir_parts: tuple[str, ...],
    exclude_paths: frozenset[str],
) -> bool:
    return (
        not exclude_paths.isdisjoint(dir_parts)
        or rel_path_str in exclude_paths
        or any(rel_path_str.startswith(f"{p}/") for p in exclude_paths)
    )


def _path_unignored(
    rel_path_str: str,
    unignore_paths: frozenset[str],
) -> bool:
    return any(
        rel_path_str == p or rel_path_str.startswith(f"{p}/") for p in unignore_paths
    )


def should_skip_path(
    path: Path,
    repo_path: Path,
    exclude_paths: frozenset[str] | None = None,
    unignore_paths: frozenset[str] | None = None,
) -> bool:
    if path.is_file() and path.suffix in cs.IGNORE_SUFFIXES:
        return True
    rel_path = path.relative_to(repo_path)
    rel_path_str = rel_path.as_posix()
    dir_parts = rel_path.parent.parts if path.is_file() else rel_path.parts

    if exclude_paths and _dir_excluded(rel_path_str, dir_parts, exclude_paths):
        return True

    if (
        unignore_paths
        and path.is_file()
        and any(fnmatch(path.name, p) for p in unignore_paths)
    ):
        return False

    if (
        exclude_paths
        and path.is_file()
        and any(fnmatch(path.name, p) for p in exclude_paths)
    ):
        return True

    if unignore_paths and _path_unignored(rel_path_str, unignore_paths):
        return False

    return not cs.IGNORE_PATTERNS.isdisjoint(dir_parts)
