from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_IGNORED_NAMES = {
    ".git",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "htmlcov",
    "node_modules",
    "venv",
}


def should_ignore(
    path: Path,
    ignored_names: set[str],
) -> bool:
    """
    Return True when the path should be excluded from the tree.
    """

    return path.name in ignored_names


def sorted_children(
    directory: Path,
    ignored_names: set[str],
) -> list[Path]:
    """
    Return directory contents sorted with folders first.
    """

    children = [
        child
        for child in directory.iterdir()
        if not should_ignore(
            child,
            ignored_names,
        )
    ]

    return sorted(
        children,
        key=lambda child: (
            not child.is_dir(),
            child.name.lower(),
        ),
    )


def build_tree_lines(
    root: Path,
    ignored_names: set[str],
) -> list[str]:
    """
    Build the complete folder and file tree.
    """

    lines = [root.name]

    def walk(
        directory: Path,
        prefix: str,
    ) -> None:
        children = sorted_children(
            directory,
            ignored_names,
        )

        for index, child in enumerate(children):
            is_last = index == len(children) - 1

            connector = (
                "└── "
                if is_last
                else "├── "
            )

            lines.append(
                f"{prefix}{connector}{child.name}"
            )

            if child.is_dir():
                child_prefix = (
                    f"{prefix}    "
                    if is_last
                    else f"{prefix}│   "
                )

                walk(
                    child,
                    child_prefix,
                )

    walk(
        root,
        "",
    )

    return lines


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a complete project folder "
            "and file tree."
        ),
    )

    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Project root directory. Default: current directory.",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="project_tree.txt",
        help="Output file. Default: project_tree.txt.",
    )

    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help=(
            "Include ignored folders such as .git, "
            ".venv and __pycache__."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    root = Path(args.root).resolve()

    if not root.exists():
        raise FileNotFoundError(
            f"Directory does not exist: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Path is not a directory: {root}"
        )

    ignored_names = (
        set()
        if args.include_hidden
        else DEFAULT_IGNORED_NAMES
    )

    lines = build_tree_lines(
        root,
        ignored_names,
    )

    tree_text = "\n".join(lines)

    output_path = Path(args.output)

    output_path.write_text(
        tree_text,
        encoding="utf-8",
    )

    print(tree_text)
    print()
    print(
        f"Tree written to: "
        f"{output_path.resolve()}"
    )


if __name__ == "__main__":
    main()