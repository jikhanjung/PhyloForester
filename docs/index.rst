PhyloForester Documentation
===========================

Welcome to PhyloForester's documentation!

PhyloForester is a PyQt5-based desktop application for phylogenetic analysis. It provides a graphical interface for managing phylogenetic projects, datamatrices, and running various tree reconstruction analyses (Parsimony, Maximum Likelihood, and Bayesian inference).

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   user_guide
   analysis_guide
   troubleshooting
   developer_guide
   changelog

Features
--------

* **Project Management**: Organize phylogenetic analyses in a hierarchical structure
* **Datamatrix Editor**:

  * Excel-style editing with copy/paste support
  * Undo/redo functionality (Ctrl+Z/Y)
  * Clear and fill operations
  * Reorder taxa and characters with drag and drop

* **Multiple Analysis Types**:

  * **Parsimony Analysis**: TNT (Tree analysis using New Technology)
  * **Maximum Likelihood**: IQTree
  * **Bayesian Inference**: MrBayes

* **Tree Visualization**:

  * SVG-based phylogenetic tree rendering
  * Character state mapping
  * Synapomorphy visualization
  * Ancestral state reconstruction (Fitch algorithm)

* **Data Import/Export**:

  * Nexus format support
  * Phylip format support
  * TNT format support
  * Tree file import (Newick, Nexus)

* **Database Storage**: All data persisted in SQLite with Peewee ORM

Quick Start
-----------

Installation
~~~~~~~~~~~~

Download the latest version from the `releases page <https://github.com/jikhanjung/PhyloForester/releases>`_.

**For Windows:**
   Download and run the installer (``PhyloForester-Setup-vX.Y.Z.exe``)

**For macOS:**
   Download and extract the ZIP file, then run ``PhyloForester``

**For Linux:**
   Download and extract the tarball, then run ``./PhyloForester``

**From Source:**
   .. code-block:: bash

      git clone https://github.com/jikhanjung/PhyloForester.git
      cd PhyloForester
      pip install -r requirements.txt
      python PhyloForester.py

Basic Usage
~~~~~~~~~~~

1. **Create a New Project**

   Click "New Project" or press ``Ctrl+N`` to create a project for your phylogenetic study.

2. **Create or Import a Datamatrix**

   * Create new: Right-click project → "New Datamatrix"
   * Import: Drag and drop Nexus/Phylip/TNT files

3. **Edit Datamatrix**

   * Double-click to open the datamatrix editor
   * Add/remove taxa and characters
   * Fill in character states (0, 1, 2, ?, etc.)
   * Use Excel-style editing: Ctrl+C, Ctrl+V, Ctrl+Z

4. **Configure Analysis**

   * Right-click datamatrix → "New Analysis"
   * Choose analysis type (Parsimony/ML/Bayesian)
   * Set parameters (search settings, models, etc.)

5. **Run Analysis**

   * Click "Start Analysis" button
   * Monitor progress in real-time
   * View results in the Analysis tab

6. **View Results**

   * Examine tree topologies
   * Map character states on trees
   * Export results

**Keyboard Shortcuts:**

- ``Ctrl+N`` - New Project
- ``Ctrl+S`` - Save changes
- ``Ctrl+Z`` - Undo
- ``Ctrl+Y`` - Redo
- ``Ctrl+C`` - Copy
- ``Ctrl+V`` - Paste
- ``Delete`` - Clear selection / Delete items

For more detailed instructions, see the :doc:`user_guide`.

Technology Stack
----------------

- **Language**: Python 3.9+
- **GUI Framework**: PyQt5
- **Core Libraries**:
    - **Database ORM**: Peewee
    - **Numerical/Scientific**: NumPy, Matplotlib
    - **Bioinformatics**: BioPython
    - **Tree Reconstruction**: TNT, IQTree, MrBayes (external)

System Requirements
-------------------

**Minimum Requirements:**

- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 20.04+)
- **RAM**: 4GB
- **Disk Space**: 500MB
- **Display**: 1280x720

**Recommended:**

- **RAM**: 8GB or more
- **Display**: 1920x1080 or higher

**External Software (Optional):**

- TNT for parsimony analysis
- IQTree for maximum likelihood
- MrBayes for Bayesian inference

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
