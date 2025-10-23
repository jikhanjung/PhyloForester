# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PhyloForester is a PyQt5-based desktop application for phylogenetic analysis. It provides a graphical interface for managing phylogenetic projects, datamatrices, and running various tree reconstruction analyses (Parsimony, Maximum Likelihood, and Bayesian inference).

## Architecture

### Core Components

**Main Application Layer** (`PhyloForester.py`)
- `PhyloForesterMainWindow`: Main window with tree view for projects/datamatrices/analyses and dynamic content area
- Manages application state through `data_storage` dictionary with nested structure for projects, datamatrices, and analyses
- Uses Qt's signal/slot mechanism for UI updates and user interactions
- Implements drag-and-drop for file import and datamatrix copying between projects

**Data Model Layer** (`PfModel.py`)
- Uses Peewee ORM with SQLite backend
- Database location: `~/{COMPANY_NAME}/{PROGRAM_NAME}/PhyloForester.db`
- Core models with CASCADE delete relationships:
  - `PfProject` → `PfDatamatrix` → `PfAnalysis` → `PfTree`
  - `PfPackage` for external analysis software metadata
- Datamatrices store data as JSON in `datamatrix_json`, `taxa_list_json`, `character_list_json`
- Analysis models support three types: Parsimony, ML (Maximum Likelihood), Bayesian

**Dialog Layer** (`PfDialog.py`)
- Custom dialogs for project, datamatrix, and analysis configuration
- `AnalysisViewer`: Tabbed interface showing analysis info, logs, and tree visualizations
- `TreeViewer`: SVG-based phylogenetic tree rendering with character mapping support

**Utility Layer** (`PfUtils.py`)
- File format parsers for Nexus, Phylip, and TNT formats
- `PhyloDatafile`: Handles importing various phylogenetic data formats
- `PhyloTreefile`: Parses tree files (Nexus, Newick)
- Fitch algorithm implementation for ancestral state reconstruction
- Resource path handling for PyInstaller bundled executables

### Key Architectural Patterns

**Process Management**
- Uses `QProcess` for running external phylogenetic software (TNT, IQTree, MrBayes)
- Analysis runs asynchronously with real-time output capture and progress tracking
- Progress parsing via regex patterns specific to each analysis type
- Analysis status stored in database: Ready → Running → Completed/Stopped/Failed

**Data Storage Strategy**
- Runtime state: `self.data_storage` dictionary caches database objects and their associated widgets
- Structure: `data_storage[type][id]` where type is 'project', 'datamatrix', or 'analysis'
- Each entry contains: object reference, Qt widgets, tree items, and child references
- Prevents redundant database queries and maintains UI consistency

**Widget Lifecycle**
- Widgets created lazily when first selected in tree view
- Stored in `data_storage` for reuse when re-selected
- Replaced in main splitter rather than recreated
- Deleted explicitly when parent object is deleted (see `on_action_delete_datamatrix_triggered`)

**File Format Handling**
- Auto-detection based on file extension and content
- Nexus: Block-based parsing with command extraction
- Phylip: Sequential vs. interleaved format detection
- TNT: Custom xread format support
- Polymorphic characters stored as lists within the datamatrix

## Commands

### Running the Application

```bash
# Development mode
python PhyloForester.py

# Install dependencies
pip install -r requirements.txt
```

### Building Executables

**Windows:**
```bash
pyinstaller --onedir --noconsole --add-data "icons/*.png;icons" --add-data "data/*.*;data" --add-data "translations/*.qm;translations" --add-data "migrations/*;migrations" --icon="icons/PhyloForester.png" --noconfirm PhyloForester.py
```

**MacOS:**
```bash
pyinstaller --onedir --noconsole --add-data "icons/*.png:icons" --add-data "data/*.*:data" --add-data "translations/*.qm:translations" --add-data "migrations/*:migrations" --icon="icons/PhyloForester.png" --noconfirm PhyloForester.py
```

### Database Migrations

```bash
# Migrations are run automatically on startup via peewee-migrate
# Migration files are in migrations/ directory
# To create new migration:
python migration.py
```

### Translations

```bash
# Extract translatable strings
pylupdate5 PhyloForester.py -ts translations/PhyloForester_en.ts
pylupdate5 PhyloForester.py -ts translations/PhyloForester_ko.ts

# Edit with Qt Linguist
linguist
```

## External Dependencies

PhyloForester integrates with external phylogenetic software that must be installed separately:

- **TNT** (Parsimony analysis): Configure path in Preferences
- **IQTree** (Maximum Likelihood): Configure path in Preferences
- **MrBayes** (Bayesian inference): Configure path in Preferences

Paths are stored in QSettings: `SoftwarePath/TNT`, `SoftwarePath/IQTree`, `SoftwarePath/MrBayes`

## Important Implementation Details

### Analysis Execution Flow

1. User creates analysis via `AnalysisDialog` → saves to database with status=READY
2. `startAnalysis()` picks first READY analysis or runs specified analysis
3. Exports datamatrix to appropriate format (Nexus/Phylip) in result directory
4. Starts QProcess with software-specific arguments
5. Progress tracked via regex parsing of stdout/stderr
6. On completion, generates consensus tree and stores in `PfTree` table

### Tree Visualization

- Trees rendered as SVG using matplotlib
- Character state mapping overlays synapomorphies on branches
- Fitch algorithm implementation in PfUtils.py for ancestral reconstruction
- Trees stored as Newick strings in database
- Rendering options stored as JSON in `tree_options_json`

### Datamatrix Table Editing

- Custom `PfTableModel` tracks cell changes via dict structure: `{'value': str, 'changed': bool}`
- Changed cells highlighted with yellow background
- Save button serializes table back to JSON in database
- Supports polymorphic characters displayed as space-separated values

### Custom Widgets

- `PfItemDelegate`: Renders progress bars in tree view for running analyses
- `PfTabBar`: Editable tab names with double-click
- `PfTreeView`, `PfTableView`: Enhanced with drag/drop event handlers
- All custom widgets defined inline in PhyloForester.py

## Configuration Files

- **Settings**: Stored via QSettings in platform-specific location
  - Windows: Registry
  - macOS/Linux: `.ini` files in user home
- **Database**: `~/PaleoBytes/PhyloForester/PhyloForester.db`
- **Result directories**: Named by analysis, stored under project structure

## Testing

Currently no automated test suite. Testing is manual via the GUI.

For test data files, see `data/` directory (e.g., `Cloudina.nex`, `ComparisonTL2.nex`).
