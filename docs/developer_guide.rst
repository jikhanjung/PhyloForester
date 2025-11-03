Developer Guide
===============

This guide is for developers who want to contribute to PhyloForester or extend its functionality.

Architecture Overview
---------------------

PhyloForester follows a layered architecture:

.. code-block:: text

   ┌─────────────────────────────┐
   │   PhyloForester.py          │  Main Application
   │   (Qt Main Window)          │
   └──────────────┬──────────────┘
                  │
   ┌──────────────┴──────────────┐
   │   PfDialog.py               │  Dialog Layer
   │   (UI Components)           │
   └──────────────┬──────────────┘
                  │
   ┌──────────────┴──────────────┐
   │   PfModel.py                │  Data Model Layer
   │   (Peewee ORM)              │
   └──────────────┬──────────────┘
                  │
   ┌──────────────┴──────────────┐
   │   PfUtils.py                │  Utility Layer
   │   (Helpers, Parsers)        │
   └─────────────────────────────┘

Core Components
~~~~~~~~~~~~~~~

**PhyloForester.py** (Main Application)

- ``PhyloForesterMainWindow``: Main window class
- Tree view management
- Signal/slot connections
- Menu and toolbar setup

**PfModel.py** (Database Models)

- ``PfProject``: Project model
- ``PfDatamatrix``: Datamatrix model
- ``PfAnalysis``: Analysis model
- ``PfTree``: Tree model
- ``PfPackage``: External software metadata

**PfDialog.py** (Dialogs)

- ``ProjectDialog``: Project properties
- ``DatamatrixDialog``: Datamatrix editor
- ``AnalysisDialog``: Analysis configuration
- ``AnalysisViewer``: Results viewer
- ``TreeViewer``: Tree visualization

**PfUtils.py** (Utilities)

- ``PhyloDatafile``: Data import/export
- ``PhyloTreefile``: Tree parsing
- File format parsers (Nexus, Phylip, TNT)
- Fitch algorithm for ancestral reconstruction

Setting Up Development Environment
-----------------------------------

Prerequisites
~~~~~~~~~~~~~

- Python 3.9+
- Git
- Qt5 development libraries (for PyQt5)

Clone Repository
~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/jikhanjung/PhyloForester.git
   cd PhyloForester

Create Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python -m venv venv

   # Windows
   venv\\Scripts\\activate

   # macOS/Linux
   source venv/bin/activate

Install Dependencies
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Runtime dependencies
   pip install -r requirements.txt

   # Development dependencies
   pip install -r requirements-ci.txt

Run from Source
~~~~~~~~~~~~~~~

.. code-block:: bash

   python PhyloForester.py

Code Structure
--------------

Data Storage
~~~~~~~~~~~~

Runtime state stored in ``self.data_storage`` dictionary:

.. code-block:: python

   data_storage = {
       'project': {
           <project_id>: {
               'object': <PfProject instance>,
               'widget': <QWidget>,
               'tree_item': <QStandardItem>,
               'datamatrix': {}  # nested datamatrices
           }
       },
       'datamatrix': {
           <datamatrix_id>: {
               'object': <PfDatamatrix instance>,
               'widget': <QWidget>,
               'tree_item': <QStandardItem>,
               'analysis': {}  # nested analyses
           }
       },
       'analysis': {
           <analysis_id>: {
               'object': <PfAnalysis instance>,
               'widget': <QWidget>,
               'tree_item': <QStandardItem>
           }
       }
   }

This prevents redundant database queries and maintains UI consistency.

Database Schema
~~~~~~~~~~~~~~~

.. code-block:: python

   class PfProject(BaseModel):
       name = CharField()
       description = TextField(null=True)

   class PfDatamatrix(BaseModel):
       project = ForeignKeyField(PfProject, backref='datamatrices')
       name = CharField()
       datamatrix_json = TextField()  # JSON serialized matrix
       taxa_list_json = TextField()   # JSON serialized taxa names
       character_list_json = TextField()  # JSON serialized characters

   class PfAnalysis(BaseModel):
       datamatrix = ForeignKeyField(PfDatamatrix, backref='analyses')
       name = CharField()
       analysis_type = CharField()  # 'Parsimony', 'ML', 'Bayesian'
       status = CharField()  # 'READY', 'RUNNING', 'COMPLETED', etc.
       parameters_json = TextField()

   class PfTree(BaseModel):
       analysis = ForeignKeyField(PfAnalysis, backref='trees')
       tree_newick = TextField()
       tree_options_json = TextField()

Running Tests
-------------

PhyloForester uses pytest for testing.

Run All Tests
~~~~~~~~~~~~~

.. code-block:: bash

   pytest tests/ -v

Run Specific Test File
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pytest tests/test_utils.py -v

Run with Coverage
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pytest tests/ --cov=. --cov-report=html

View coverage report: ``htmlcov/index.html``

Test Categories
~~~~~~~~~~~~~~~

Tests are marked by category:

- ``@pytest.mark.unit``: Unit tests
- ``@pytest.mark.model``: Database/model tests
- ``@pytest.mark.dialog``: UI/dialog tests

Run specific category:

.. code-block:: bash

   pytest -m unit

Code Quality
------------

Linting
~~~~~~~

PhyloForester uses Ruff for linting:

.. code-block:: bash

   ruff check .

Auto-fix issues:

.. code-block:: bash

   ruff check . --fix

Code Style
~~~~~~~~~~

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to public functions/classes
- Keep functions focused and short

Type Hints
~~~~~~~~~~

Use type hints where practical:

.. code-block:: python

   def parse_nexus_file(filepath: str) -> Dict[str, Any]:
       """Parse a Nexus format file.

       Args:
           filepath: Path to Nexus file

       Returns:
           Dictionary with parsed data
       """
       pass

Contributing
------------

Workflow
~~~~~~~~

1. Fork the repository
2. Create a feature branch: ``git checkout -b feature/my-feature``
3. Make changes and commit: ``git commit -m "Add my feature"``
4. Push to branch: ``git push origin feature/my-feature``
5. Create Pull Request on GitHub

Commit Messages
~~~~~~~~~~~~~~~

Follow conventional commits:

- ``feat:``: New feature
- ``fix:``: Bug fix
- ``docs:``: Documentation changes
- ``refactor:``: Code refactoring
- ``test:``: Test additions/changes
- ``chore:``: Maintenance tasks

Example:

.. code-block:: text

   feat: Add support for FASTA format import

   - Implement FASTA parser in PfUtils
   - Add FASTA to import dialog options
   - Add tests for FASTA parsing

Pull Request Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~

- Describe what the PR does
- Reference any related issues
- Include tests for new features
- Update documentation if needed
- Ensure CI tests pass

Building Documentation
----------------------

Install Sphinx:

.. code-block:: bash

   pip install -r docs/requirements.txt

Build HTML docs:

.. code-block:: bash

   cd docs
   sphinx-build -b html . _build/html

View: ``docs/_build/html/index.html``

Auto-rebuild on changes:

.. code-block:: bash

   sphinx-autobuild docs docs/_build/html

Building Executables
--------------------

PhyloForester uses PyInstaller for building standalone executables.

Build Script
~~~~~~~~~~~~

Use the ``build.py`` script:

.. code-block:: bash

   python build.py

This automatically:

- Detects your platform
- Reads version from ``version.py``
- Bundles all dependencies
- Creates executable in ``dist/``

Manual PyInstaller
~~~~~~~~~~~~~~~~~~

Or use PyInstaller directly:

.. code-block:: bash

   pyinstaller PhyloForester.spec

Platform-Specific Notes
~~~~~~~~~~~~~~~~~~~~~~~

**Windows:**

- Creates ``.exe`` file
- Optional Inno Setup installer creation
- Requires Visual C++ Redistributable on target systems

**macOS:**

- Creates ``.app`` bundle
- May need code signing for distribution
- Use ``create-dmg`` for DMG images

**Linux:**

- Creates standalone executable
- May need to ship Qt5 libraries
- Consider AppImage for distribution

Version Management
------------------

PhyloForester uses semantic versioning (semver).

Update Version
~~~~~~~~~~~~~~

Use the ``manage_version.py`` script:

.. code-block:: bash

   # Increment patch (0.1.0 -> 0.1.1)
   python manage_version.py patch

   # Increment minor (0.1.0 -> 0.2.0)
   python manage_version.py minor

   # Increment major (0.1.0 -> 1.0.0)
   python manage_version.py major

   # Start pre-release (0.1.0 -> 0.2.0-alpha.1)
   python manage_version.py preminor

The script:

- Updates ``version.py``
- Updates ``CHANGELOG.md``
- Creates git commit and tag
- Prompts for confirmation

Release Process
~~~~~~~~~~~~~~~

1. Update version: ``python manage_version.py minor``
2. Update ``CHANGELOG.md`` with release notes
3. Commit changes
4. Push to GitHub: ``git push origin main``
5. Create and push tag: ``git push origin v0.2.0``
6. GitHub Actions automatically builds and releases

CI/CD Pipeline
--------------

PhyloForester uses GitHub Actions for CI/CD.

Workflows
~~~~~~~~~

**test.yml** - Automated Testing

- Runs on push/PR
- Tests Python 3.9, 3.10, 3.11
- Measures code coverage
- Runs linter

**build.yml** - Build Artifacts

- Runs on push to main
- Builds Windows/macOS/Linux
- Uploads build artifacts
- Uses ``build.py`` script

**release.yml** - Automated Release

- Triggers on git tag (v*.*.*)
- Runs tests first
- Builds all platforms
- Creates GitHub release
- Uploads installers/packages

Manual Release
~~~~~~~~~~~~~~

Use GitHub Actions UI:

1. Go to Actions → Manual Release
2. Click "Run workflow"
3. Enter version number
4. Choose pre-release/draft options
5. Click "Run workflow"

Adding Features
---------------

Adding a New Analysis Type
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Update PfModel.py:**

   Add new analysis type constant

2. **Update AnalysisDialog:**

   Add configuration UI for new type

3. **Implement runner:**

   Add execution logic in ``startAnalysis()``

4. **Add parser:**

   Parse output files in ``PfUtils.py``

5. **Update tests:**

   Add tests for new analysis type

Adding a New Import Format
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Update PfUtils.py:**

   .. code-block:: python

      class PhyloDatafile:
          def load_myformat(self, filepath):
              """Load MyFormat data file."""
              # Parse file
              # Return taxa_list, character_list, datamatrix

2. **Update import dialog:**

   Add format to file filter

3. **Add tests:**

   Create test file in ``data/``
   Add test in ``tests/test_utils.py``

Extending the UI
~~~~~~~~~~~~~~~~

Custom widgets should:

- Inherit from appropriate Qt widget
- Use signal/slot for communication
- Be added to ``PfDialog.py`` or inline in ``PhyloForester.py``

Example:

.. code-block:: python

   class CustomTableView(QTableView):
       cellChanged = pyqtSignal(int, int, str)

       def __init__(self, parent=None):
           super().__init__(parent)
           # Custom initialization

       def custom_method(self):
           # Custom functionality
           self.cellChanged.emit(row, col, value)

Debugging
---------

Logging
~~~~~~~

PhyloForester uses Python's logging module:

.. code-block:: python

   import logging
   logger = logging.getLogger(__name__)

   logger.debug("Debug message")
   logger.info("Info message")
   logger.warning("Warning message")
   logger.error("Error message")

Logs are written to ``PaleoBytes/PhyloForester/Logs/``

PyQt Debugging
~~~~~~~~~~~~~~

Enable Qt warnings:

.. code-block:: bash

   export QT_DEBUG_PLUGINS=1
   python PhyloForester.py

Database Inspection
~~~~~~~~~~~~~~~~~~~

Use SQLite browser:

.. code-block:: bash

   sqlite3 ~/PaleoBytes/PhyloForester/PhyloForester.db

Or use DB Browser for SQLite (GUI)

Resources
---------

- **PyQt5 Documentation**: https://www.riverbankcomputing.com/static/Docs/PyQt5/
- **Peewee ORM**: http://docs.peewee-orm.com/
- **Pytest**: https://docs.pytest.org/
- **Sphinx**: https://www.sphinx-doc.org/

Contact
-------

- **Issues**: https://github.com/jikhanjung/PhyloForester/issues
- **Pull Requests**: https://github.com/jikhanjung/PhyloForester/pulls
- **Discussions**: https://github.com/jikhanjung/PhyloForester/discussions

Next Steps
----------

- See :doc:`user_guide` for user-facing features
- See :doc:`troubleshooting` for common issues
- See :doc:`changelog` for version history
