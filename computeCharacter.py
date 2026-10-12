#!/usr/bin/env python3
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from autosheet import load_character, calculate, save_character_with_effective


def main():
    if len(sys.argv) < 2:
        print("Usage: python computeCharacter.py [characterfile]", file=sys.stderr)
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: File {path} does not exist.", file=sys.stderr)
        sys.exit(1)

    character = load_character(path)
    effective = calculate(character)
    save_character_with_effective(character, effective, path)


if __name__ == "__main__":
    main()
