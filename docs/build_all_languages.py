#!/usr/bin/env python3
"""Build Sphinx documentation for all languages.

This script builds the PhyloForester documentation for both English and Korean,
creating separate output directories for each language.

Usage:
    python build_all_languages.py

Output:
    _build/html/en/  - English documentation
    _build/html/ko/  - Korean documentation
"""

import subprocess
import sys
from pathlib import Path

LANGUAGES = ["en", "ko"]
DOCS_DIR = Path(__file__).parent


def build_language(lang: str) -> bool:
    """Build documentation for a specific language.

    Args:
        lang: Language code ('en' or 'ko')

    Returns:
        True if build succeeded, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"Building documentation for: {lang}")
    print("=" * 60)

    build_dir = DOCS_DIR / "_build" / "html" / lang

    if lang == "en":
        # English (default language)
        cmd = ["sphinx-build", "-b", "html", ".", str(build_dir)]
    else:
        # Other languages (Korean)
        cmd = ["sphinx-build", "-b", "html", "-D", f"language={lang}", ".", str(build_dir)]

    result = subprocess.run(cmd, cwd=DOCS_DIR, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: Build failed for {lang}")
        print(result.stderr)
        return False

    print(f"SUCCESS: Documentation built at {build_dir}")
    return True


def main() -> int:
    """Build documentation for all languages.

    Returns:
        0 if all builds succeeded, 1 if any build failed
    """
    print("=" * 60)
    print("PhyloForester Documentation - Multi-language Build")
    print("=" * 60)

    success = True

    for lang in LANGUAGES:
        if not build_language(lang):
            success = False

    if success:
        print(f"\n{'='*60}")
        print("All language builds completed successfully!")
        print("=" * 60)
        print("\nOutput directories:")
        for lang in LANGUAGES:
            lang_name = "English" if lang == "en" else "한국어"
            print(f"  {lang_name:10} -> _build/html/{lang}/index.html")
        print()
        return 0
    print("\nERROR: Some builds failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
