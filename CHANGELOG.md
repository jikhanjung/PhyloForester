# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-03

### Added
- **Excel-style Copy/Paste**: Copy (Ctrl+C) and Paste (Ctrl+V) functionality for datamatrix cells with tab-delimited format
- **Undo/Redo System**: Professional undo (Ctrl+Z) and redo (Ctrl+Y) functionality using Qt's QUndoStack framework
  - Supports single cell edits
  - Supports multi-cell paste operations
  - Supports clear and fill operations
  - Properly restores cell values and visual states (yellow highlighting)
- **Clear/Fill Operations**: Clear selected cells with Delete key or Fill cells with a value via context menu
- **Move Up/Down Buttons**: Reorder taxa and characters in datamatrix dialog using arrow buttons (↑/↓)
- **Context Menu**: Right-click menu for datamatrix table with Undo, Redo, Copy, Paste, Clear, and Fill actions
- **Version Management System**: Implemented semantic versioning with `version.py` and `manage_version.py` script
- **Comprehensive Test Suite**: 82 automated tests covering utilities, models, and dialogs (from P01 improvement plan)
- **Error Handling**: Added 27 error handlers with custom exception classes for robust error management
- **Logging System**: Professional logging with file and console handlers across all modules
- **Build Automation**: PyInstaller integration with automated build scripts for Windows, macOS, and Linux

### Changed
- **Datamatrix Synchronization**: Dialog now properly synchronizes taxa/character list changes (add/edit/delete/move) with actual datamatrix JSON data using metadata tracking
- **Improved UI Layout**: Character and Taxon input fields now display above buttons with full-width layout for better usability
- **Main Table Refresh**: Datamatrix table in main window now automatically refreshes after editing in dialog
- **Input Field Placeholders**: Corrected placeholder text for taxon input field
- **Logging**: Replaced 200+ print() statements with structured logging using appropriate log levels

### Fixed
- Cell visual state (yellow highlighting) now properly restored on undo/redo operations
- Datamatrix changes in dialog now correctly reflected in main table view
- Taxa and character list modifications now properly update the underlying datamatrix structure

