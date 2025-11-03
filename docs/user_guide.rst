User Guide
==========

This guide provides a comprehensive overview of using PhyloForester for phylogenetic analysis.

Getting Started
---------------

Main Window Overview
~~~~~~~~~~~~~~~~~~~~

When you launch PhyloForester, you'll see:

- **Menu Bar**: File, Edit, View, Tools, Help menus
- **Toolbar**: Quick access to common operations
- **Tree View** (Left): Hierarchical view of projects, datamatrices, and analyses
- **Content Area** (Right): Display area for selected items
- **Status Bar** (Bottom): Current status and messages

Working with Projects
---------------------

Creating a Project
~~~~~~~~~~~~~~~~~~

Projects organize your phylogenetic studies.

1. Click **File → New Project** or press ``Ctrl+N``
2. Enter a project name
3. Optionally add a description
4. Click **OK**

The project appears in the tree view with a folder icon.

Editing Project Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Right-click the project in the tree view
2. Select **Edit Project**
3. Modify name or description
4. Click **OK**

Deleting a Project
~~~~~~~~~~~~~~~~~~

1. Right-click the project
2. Select **Delete Project**
3. Confirm deletion

.. warning::
   Deleting a project removes all associated datamatrices and analyses permanently.

Working with Datamatrices
--------------------------

A datamatrix contains your character data (taxa × characters matrix).

Creating a New Datamatrix
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Right-click a project
2. Select **New Datamatrix**
3. Enter:
   - Datamatrix name
   - Number of taxa
   - Number of characters
4. Click **OK**

The datamatrix editor opens automatically.

Importing a Datamatrix
~~~~~~~~~~~~~~~~~~~~~~

PhyloForester supports multiple file formats:

**Drag and Drop:**

1. Drag a file from your file manager
2. Drop it onto a project in the tree view
3. PhyloForester auto-detects the format

**File Menu:**

1. Right-click a project
2. Select **Import Datamatrix**
3. Choose file format (Nexus, Phylip, TNT)
4. Select the file
5. Click **Open**

**Supported Formats:**

- **Nexus (.nex, .nexus)**: Standard phylogenetic format
- **Phylip (.phy, .phylip)**: Sequential or interleaved
- **TNT (.tnt)**: TNT's xread format

Editing a Datamatrix
~~~~~~~~~~~~~~~~~~~~~

1. Double-click a datamatrix in the tree view
2. The datamatrix editor dialog opens

The editor has three main areas:

- **Character List** (Left): All defined characters
- **Taxa List** (Right): All taxa in the study
- **Data Table** (Center): Character states for each taxon

**Adding Taxa:**

1. Type taxon name in the input field
2. Click **Add** button (or press Enter)
3. The taxon appears in the list and table

**Adding Characters:**

1. Type character name in the input field
2. Click **Add** button (or press Enter)
3. A new column appears in the table

**Editing Cell Values:**

1. Click a cell in the table
2. Type the character state:
   - ``0``, ``1``, ``2``, etc. - discrete states
   - ``?`` - missing data
   - ``-`` - inapplicable
   - Multiple states: separate with spaces (e.g., ``0 1``)

**Excel-Style Editing:**

- **Copy**: Select cells → ``Ctrl+C``
- **Paste**: Select destination → ``Ctrl+V``
- **Clear**: Select cells → ``Delete``
- **Fill**: Select cells → Right-click → Fill
- **Undo**: ``Ctrl+Z``
- **Redo**: ``Ctrl+Y``

**Reordering:**

- Select a taxon/character
- Click **↑** or **↓** buttons to move

**Removing:**

- Select a taxon/character
- Click **Remove** button

**Saving Changes:**

- Click **Save** button in the editor
- Or click **OK** to save and close

Exporting a Datamatrix
~~~~~~~~~~~~~~~~~~~~~~~

1. Right-click a datamatrix
2. Select **Export**
3. Choose format (Nexus, Phylip, TNT)
4. Select destination
5. Click **Save**

Running Analyses
----------------

PhyloForester supports three types of phylogenetic analyses.

Creating an Analysis
~~~~~~~~~~~~~~~~~~~~

1. Right-click a datamatrix
2. Select **New Analysis**
3. Choose analysis type:
   - **Parsimony** (requires TNT)
   - **Maximum Likelihood** (requires IQTree)
   - **Bayesian** (requires MrBayes)
4. Configure analysis parameters
5. Click **OK**

Parsimony Analysis (TNT)
~~~~~~~~~~~~~~~~~~~~~~~~

**Parameters:**

- **Number of replicates**: Wagner trees to build
- **Hold**: Maximum trees to keep in memory
- **TBR**: Tree bisection-reconnection
- **Mult**: Number of random addition sequences

**Common Settings:**

- Quick analysis: 10 replicates, Hold 100
- Standard: 100 replicates, Hold 1000
- Thorough: 1000 replicates, Hold 10000

**Running:**

1. Configure parameters
2. Click **Start Analysis**
3. Monitor progress (percentage shown)
4. Analysis completes → consensus tree generated

Maximum Likelihood (IQTree)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Parameters:**

- **Substitution model**: Auto-detect or specify (GTR, JC, K2P, etc.)
- **Bootstrap replicates**: 0 (none), 1000 (standard), or more
- **Search algorithm**: Standard or fast

**Running:**

1. Configure parameters
2. Click **Start Analysis**
3. IQTree tests models (if auto-detect)
4. Tree search begins
5. Bootstrap analysis (if specified)
6. Best tree saved

Bayesian Analysis (MrBayes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Parameters:**

- **Generations**: MCMC chain length (1M - 10M typical)
- **Sample frequency**: Save trees every N generations
- **Burnin**: Proportion to discard (0.25 = 25%)
- **Priors**: Model parameters

**Running:**

1. Configure parameters
2. Click **Start Analysis**
3. MCMC chains run (can take hours/days)
4. Convergence diagnostics shown
5. Consensus tree generated

Stopping an Analysis
~~~~~~~~~~~~~~~~~~~~

If an analysis is running:

1. Click **Stop Analysis** button
2. Partial results are saved
3. Status changes to "Stopped"

Viewing Results
---------------

Analysis Output
~~~~~~~~~~~~~~~

1. Double-click an analysis in the tree view
2. The Analysis Viewer opens with tabs:
   - **Info**: Analysis parameters and status
   - **Log**: Real-time output from software
   - **Trees**: Phylogenetic trees found

Tree Visualization
~~~~~~~~~~~~~~~~~~

In the **Trees** tab:

- **Tree List**: All trees from the analysis
- **Tree View**: SVG rendering of selected tree
- **Controls**:
  - Zoom in/out
  - Export as SVG/PNG
  - Map characters

Character Mapping
~~~~~~~~~~~~~~~~~

To visualize character evolution:

1. Open an analysis with trees
2. Select a tree
3. Click **Map Characters**
4. Choose character to map
5. Character states appear on branches

The visualization shows:

- **Nodes**: Ancestral states (reconstructed)
- **Branches**: State changes (synapomorphies)
- **Terminal nodes**: Observed states

Advanced Features
-----------------

Batch Operations
~~~~~~~~~~~~~~~~

Copy Datamatrix:

1. Right-click a datamatrix
2. Select **Copy**
3. Right-click destination project
4. Select **Paste**

Duplicate Analysis:

1. Right-click an analysis
2. Select **Duplicate**
3. Modify parameters
4. Run comparison study

Database Management
~~~~~~~~~~~~~~~~~~~

**Location:**

- Windows: ``C:\\Users\\<username>\\PaleoBytes\\PhyloForester``
- macOS/Linux: ``~/PaleoBytes/PhyloForester``

**Backup:**

1. Close PhyloForester
2. Copy ``PhyloForester.db`` to safe location
3. Restore by replacing the file

**Opening Different Database:**

1. **File → Open Database**
2. Select ``.db`` file
3. Database loads (previous one closes)

Preferences
~~~~~~~~~~~

**Edit → Preferences** allows you to set:

- External software paths (TNT, IQTree, MrBayes)
- Default parameters for analyses
- UI preferences

Keyboard Shortcuts
------------------

**General:**

- ``Ctrl+N`` - New Project
- ``Ctrl+O`` - Open Database
- ``Ctrl+S`` - Save Changes
- ``Ctrl+W`` - Close Window
- ``Ctrl+Q`` - Quit Application

**Editing:**

- ``Ctrl+Z`` - Undo
- ``Ctrl+Y`` - Redo
- ``Ctrl+C`` - Copy
- ``Ctrl+V`` - Paste
- ``Ctrl+X`` - Cut
- ``Delete`` - Delete/Clear

**Navigation:**

- ``Ctrl+Tab`` - Next Tab
- ``Ctrl+Shift+Tab`` - Previous Tab
- ``F5`` - Refresh

Tips and Best Practices
------------------------

Organizing Projects
~~~~~~~~~~~~~~~~~~~

- Use descriptive project names (e.g., "Mammal_Phylogeny_2024")
- Group related analyses in the same project
- Keep separate projects for different studies

Data Quality
~~~~~~~~~~~~

- Check for missing data (``?``) before analysis
- Verify character coding consistency
- Use inapplicable (``-``) for logically impossible states

Analysis Settings
~~~~~~~~~~~~~~~~~

- Start with quick settings for initial exploration
- Use thorough settings for publication-quality results
- Always check convergence for Bayesian analyses

File Management
~~~~~~~~~~~~~~~

- Back up database regularly
- Export important datamatrices in multiple formats
- Keep original data files separate

Next Steps
----------

- See :doc:`analysis_guide` for detailed analysis workflows
- See :doc:`troubleshooting` if you encounter problems
- See :doc:`developer_guide` for customization and scripting
