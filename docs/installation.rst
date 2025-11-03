Installation
============

PhyloForester can be installed in several ways depending on your needs and platform.

Installing Pre-built Binaries
------------------------------

The easiest way to install PhyloForester is to download pre-built binaries from the GitHub releases page.

Windows
~~~~~~~

1. Go to the `releases page <https://github.com/jikhanjung/PhyloForester/releases>`_
2. Download the latest ``PhyloForester-Setup-vX.Y.Z.exe`` installer
3. Run the installer and follow the installation wizard
4. Launch PhyloForester from the Start Menu or Desktop shortcut

**Portable Version:**

Alternatively, download the ZIP file (``PhyloForester-Windows-vX.Y.Z-buildN.zip``):

1. Extract the ZIP to any folder
2. Run ``PhyloForester.exe`` from the extracted folder
3. No installation required - run from USB drives

macOS
~~~~~

1. Go to the `releases page <https://github.com/jikhanjung/PhyloForester/releases>`_
2. Download the latest ``PhyloForester-macOS-vX.Y.Z-buildN.zip``
3. Extract the ZIP file
4. Drag ``PhyloForester`` to your Applications folder (optional)
5. Double-click to run

**Note:** On first launch, you may need to right-click → Open to bypass Gatekeeper.

Linux
~~~~~

1. Go to the `releases page <https://github.com/jikhanjung/PhyloForester/releases>`_
2. Download the latest ``PhyloForester-Linux-vX.Y.Z-buildN.tar.gz``
3. Extract the tarball:

   .. code-block:: bash

      tar -xzf PhyloForester-Linux-vX.Y.Z-buildN.tar.gz
      cd PhyloForester

4. Run the application:

   .. code-block:: bash

      ./PhyloForester

**System Dependencies:**

On some Linux distributions, you may need to install Qt5 libraries:

.. code-block:: bash

   # Ubuntu/Debian
   sudo apt-get install libqt5gui5 libqt5core5a libqt5widgets5

   # Fedora/RHEL
   sudo dnf install qt5-qtbase qt5-qtbase-gui

Installing from Source
----------------------

Prerequisites
~~~~~~~~~~~~~

- Python 3.9 or higher
- pip (Python package manager)
- Git (optional, for cloning repository)

Steps
~~~~~

1. **Clone or Download the Repository**

   .. code-block:: bash

      git clone https://github.com/jikhanjung/PhyloForester.git
      cd PhyloForester

   Or download and extract the ZIP from GitHub.

2. **Create a Virtual Environment (Recommended)**

   .. code-block:: bash

      # Windows
      python -m venv venv
      venv\\Scripts\\activate

      # macOS/Linux
      python3 -m venv venv
      source venv/bin/activate

3. **Install Dependencies**

   .. code-block:: bash

      pip install -r requirements.txt

4. **Run PhyloForester**

   .. code-block:: bash

      python PhyloForester.py

Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~

For development, install additional dependencies:

.. code-block:: bash

   pip install -r requirements-ci.txt

This includes testing tools (pytest, pytest-qt) and code quality tools (ruff).

Installing External Analysis Software
--------------------------------------

PhyloForester integrates with external phylogenetic software for analysis. These are optional but required for their respective analysis types.

TNT (Parsimony Analysis)
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Download TNT from http://www.lillo.org.ar/phylogeny/tnt/
2. Extract the executable
3. In PhyloForester, go to **Edit → Preferences**
4. Set the path to the TNT executable

IQTree (Maximum Likelihood)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Download IQTree from http://www.iqtree.org/
2. Extract the executable
3. In PhyloForester, go to **Edit → Preferences**
4. Set the path to the IQTree executable

MrBayes (Bayesian Inference)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Download MrBayes from https://nbisweden.github.io/MrBayes/
2. Install following the platform-specific instructions
3. In PhyloForester, go to **Edit → Preferences**
4. Set the path to the MrBayes executable

Verifying Installation
-----------------------

To verify PhyloForester is installed correctly:

1. Launch the application
2. The main window should appear with an empty project tree
3. Check **Help → About** to see the version number
4. Try creating a new project (Ctrl+N)

If you encounter issues, see the :doc:`troubleshooting` guide.

Updating PhyloForester
----------------------

Binary Installation
~~~~~~~~~~~~~~~~~~~

1. Download the latest version from the releases page
2. Install over the existing installation (Windows installer)
3. Or replace the old files with the new ones (portable/macOS/Linux)

Your data is stored in a separate database location and will not be affected:

- **Windows**: ``C:\\Users\\<username>\\PaleoBytes\\PhyloForester\\PhyloForester.db``
- **macOS/Linux**: ``~/PaleoBytes/PhyloForester/PhyloForester.db``

Source Installation
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd PhyloForester
   git pull origin main
   pip install -r requirements.txt --upgrade

Uninstalling
------------

Windows (Installer)
~~~~~~~~~~~~~~~~~~~

1. Go to **Settings → Apps → Installed Apps**
2. Find "PhyloForester"
3. Click **Uninstall**

Windows (Portable) / macOS / Linux
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Simply delete the PhyloForester folder.

**Removing User Data:**

If you want to completely remove all PhyloForester data:

- **Windows**: Delete ``C:\\Users\\<username>\\PaleoBytes``
- **macOS/Linux**: Delete ``~/PaleoBytes``

This will remove all projects, datamatrices, and analyses.

Next Steps
----------

After installation, see the :doc:`user_guide` to get started with your first phylogenetic analysis.
