Changelog
=========

All notable changes to PhyloForester are documented here.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[0.1.0] - 2025-11-03
--------------------

Added
~~~~~

**Datamatrix Editor Enhancements:**

- Excel-style copy/paste functionality (Ctrl+C/V) with tab-delimited format
- Professional undo/redo system using Qt's QUndoStack framework
- Clear selected cells with Delete key
- Fill multiple cells with a value via context menu
- Move Up/Down buttons (↑/↓) for reordering taxa and characters
- Context menu with Undo, Redo, Copy, Paste, Clear, and Fill actions
- Full-width input fields for character and taxon names
- Metadata tracking for robust datamatrix synchronization

**CI/CD Pipeline:**

- Automated testing workflow for Python 3.9, 3.10, 3.11
- PyQt5 GUI testing with xvfb on Linux
- Ruff linter integration
- Code coverage reporting with Codecov
- Cross-platform build automation (Windows/macOS/Linux)
- Automated GitHub releases on git tags
- Manual release workflow via GitHub Actions UI
- SHA256 checksum generation for releases
- Windows Inno Setup installer creation

**Testing Infrastructure:**

- 82 automated tests covering utilities, models, and dialogs
- pytest configuration with test markers (unit/model/dialog)
- Test separation with individual timeouts
- pytest-qt for GUI testing

**Build System:**

- Unified ``build.py`` script for cross-platform builds
- Version extraction from ``version.py``
- Platform-specific optimizations
- Artifact naming with version and build numbers

**Version Management:**

- Semantic versioning system with ``version.py``
- ``manage_version.py`` script for automated version updates
- CHANGELOG.md integration
- Git commit and tag automation

**Error Handling:**

- 27 error handlers with custom exception classes
- Comprehensive error management across modules

**Logging System:**

- Professional logging with file and console handlers
- Replaced 200+ print() statements with structured logging
- Appropriate log levels (DEBUG/INFO/WARNING/ERROR)

Changed
~~~~~~~

- Datamatrix Dialog now properly synchronizes taxa/character list changes with datamatrix JSON
- Character and Taxon input fields display above buttons with full-width layout
- Main table automatically refreshes after editing datamatrix in dialog
- Input field placeholder text corrected for taxon field
- Enhanced Inno Setup script with environment variable version support
- PyInstaller spec file optimized

Fixed
~~~~~

- Cell visual state (yellow highlighting) now properly restored on undo/redo
- Datamatrix changes in dialog correctly reflected in main table view
- Taxa and character list modifications properly update underlying datamatrix structure
- List widget synchronization with actual datamatrix data

[Pre-0.1.0] - Development Versions
-----------------------------------

Earlier development focused on core functionality:

- PyQt5-based desktop application framework
- SQLite database with Peewee ORM
- Project/Datamatrix/Analysis hierarchy
- Integration with TNT, IQTree, MrBayes
- Nexus/Phylip/TNT file format support
- Tree visualization with SVG rendering
- Character state mapping
- Fitch algorithm for ancestral reconstruction

Unreleased
----------

Planned features for future releases:

- Additional file format support (FASTA, Stockholm)
- Advanced character mapping options
- Interactive tree editing
- Batch analysis operations
- Performance optimizations for large datasets
- macOS code signing
- Linux AppImage packaging
- Comprehensive user documentation
- API documentation

Version History
---------------

.. list-table::
   :header-rows: 1

   * - Version
     - Date
     - Highlights
   * - 0.1.0
     - 2025-11-03
     - Excel-style editing, CI/CD pipeline, testing infrastructure
   * - Pre-release
     - 2024-2025
     - Core phylogenetic analysis functionality

See Also
--------

- `GitHub Releases <https://github.com/jikhanjung/PhyloForester/releases>`_
- `Issue Tracker <https://github.com/jikhanjung/PhyloForester/issues>`_
- `Pull Requests <https://github.com/jikhanjung/PhyloForester/pulls>`_
