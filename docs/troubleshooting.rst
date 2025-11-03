Troubleshooting
===============

This guide helps resolve common issues with PhyloForester.

Installation Issues
-------------------

Application Won't Start
~~~~~~~~~~~~~~~~~~~~~~~

**Windows:**

- Error: "VCRUNTIME140.dll is missing"

  Solution: Install Visual C++ Redistributable from Microsoft

- Error: "Application failed to start"

  Solution: Run as Administrator, check antivirus isn't blocking

**macOS:**

- Error: "App is damaged and can't be opened"

  Solution: Run ``xattr -cr /path/to/PhyloForester.app``

- Error: "Cannot verify developer"

  Solution: Right-click → Open (bypass Gatekeeper)

**Linux:**

- Error: "error while loading shared libraries: libQt5Core.so.5"

  Solution: Install Qt5 libraries (see :doc:`installation`)

Python Source Installation Fails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Error: "No module named 'PyQt5'"

  Solution: ``pip install PyQt5``

- Error: "Microsoft Visual C++ 14.0 is required" (Windows)

  Solution: Install Visual Studio Build Tools

Data Management Issues
----------------------

Can't Open Database
~~~~~~~~~~~~~~~~~~~

**Symptoms:** "Failed to open database" error

**Solutions:**

1. Check file permissions (read/write access)
2. Verify database file isn't corrupted:
   - Try opening in SQLite browser
   - Restore from backup
3. Check disk space (database needs room to grow)

Database Corruption
~~~~~~~~~~~~~~~~~~~

**Symptoms:** Application crashes, data missing, errors on save

**Recovery:**

1. Close PhyloForester
2. Locate database file:
   - Windows: ``C:\\Users\\<name>\\PaleoBytes\\PhyloForester\\PhyloForester.db``
   - macOS/Linux: ``~/PaleoBytes/PhyloForester/PhyloForester.db``
3. Try SQLite recovery:

   .. code-block:: bash

      sqlite3 PhyloForester.db "PRAGMA integrity_check;"

4. If corrupted, restore from backup

**Prevention:**

- Regular backups (copy .db file)
- Don't force-quit during saves
- Ensure sufficient disk space

Import/Export Problems
-----------------------

File Won't Import
~~~~~~~~~~~~~~~~~

**Common causes:**

1. **Unsupported format**

   Check file extension (.nex, .phy, .tnt)

2. **Malformed file**

   Validate format with text editor

3. **Encoding issues**

   Try UTF-8 or ASCII encoding

**Solutions:**

- Check log messages for specific errors
- Try opening file in text editor
- Convert to Nexus format (most robust)

Export Fails
~~~~~~~~~~~~

**Solutions:**

1. Check write permissions in destination folder
2. Verify disk space available
3. Try different export format
4. Use simpler filename (no special characters)

Analysis Issues
---------------

External Software Not Found
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms:** "TNT not found" or similar error

**Solutions:**

1. **Set software path:**
   - Edit → Preferences
   - Browse to executable location
   - Click OK

2. **Verify executable:**
   - Run software from command line
   - Check file permissions (execute bit on Linux/macOS)

3. **Check spelling:**
   - Windows: ``tnt.exe``
   - Linux/macOS: ``tnt`` (no extension)

Analysis Fails to Start
~~~~~~~~~~~~~~~~~~~~~~~~

**Check:**

1. Datamatrix has data (not empty)
2. External software path correct
3. No special characters in project/datamatrix names
4. Sufficient disk space for output files

**Look in Log tab for error messages**

Analysis Runs but No Results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Possible causes:**

1. **No trees found** (parsimony)
   - Data may be too homogeneous
   - Try more replicates

2. **Analysis stopped prematurely**
   - Check if you clicked Stop
   - Check system resources

3. **Output parsing failed**
   - Check Log tab for raw output
   - May need software update

Analysis Takes Too Long
~~~~~~~~~~~~~~~~~~~~~~~

**For Parsimony:**

- Should complete in seconds-minutes
- If stuck, reduce Hold parameter

**For Maximum Likelihood:**

- Can take minutes-hours
- Reduce bootstrap replicates for testing
- Use "Fast" algorithm option

**For Bayesian:**

- Expected to take hours-days
- Check convergence periodically
- Can stop and resume (in MrBayes directly)

Solutions:

- Reduce dataset size for testing
- Use faster computer
- Run overnight
- Consider cloud computing for large datasets

UI and Display Issues
---------------------

Window Layout Broken
~~~~~~~~~~~~~~~~~~~~~

Reset window geometry:

1. Close PhyloForester
2. Delete settings file:
   - Windows: ``C:\\Users\\<name>\\AppData\\Roaming\\PaleoBytes\\PhyloForester``
   - macOS: ``~/Library/Preferences/com.paleobytes.PhyloForester.plist``
   - Linux: ``~/.config/PaleoBytes/PhyloForester.conf``
3. Restart PhyloForester

Trees Not Displaying
~~~~~~~~~~~~~~~~~~~~

**Solutions:**

1. Check if tree data exists (look in Log)
2. Try different tree from list
3. Export tree as Newick, verify it's valid
4. Restart application

Text Too Small/Large
~~~~~~~~~~~~~~~~~~~~

Adjust with system DPI settings:

**Windows:**
  Settings → Display → Scale

**macOS:**
  System Preferences → Displays → Resolution

**Linux:**
  Desktop environment settings

Keyboard Shortcuts Not Working
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Check:**

1. Focus is in correct window/widget
2. No conflicting OS shortcuts
3. NumLock state (if using numpad)

**macOS:**
  Ctrl shortcuts may need Cmd instead

Datamatrix Editor Issues
-------------------------

Can't Edit Cells
~~~~~~~~~~~~~~~~

**Check:**

1. Datamatrix is open in edit mode (not view-only)
2. Cell is selected (click once to select)
3. No dialog box hidden behind

Undo/Redo Not Working
~~~~~~~~~~~~~~~~~~~~~~

**Limitations:**

- Only works within a single editing session
- Closing editor clears undo history
- Max undo stack size: 50 operations

**If broken:**

- Save and reopen editor
- Restart application

Copy/Paste Not Working
~~~~~~~~~~~~~~~~~~~~~~~

**Check:**

1. Cells are selected (should be highlighted)
2. Clipboard has data (paste elsewhere to verify)
3. Format is compatible (tab-delimited for cross-app)

**Workaround:**

- Use Export/Import for large data transfers
- Copy through external text editor

Performance Issues
------------------

Application Slow
~~~~~~~~~~~~~~~~

**Causes and solutions:**

1. **Large database**
   - Archive old projects
   - Split into multiple databases

2. **Many trees in analysis**
   - Limit trees saved (Hold parameter)
   - Delete old analyses

3. **Insufficient RAM**
   - Close other applications
   - Upgrade hardware

4. **Slow disk**
   - Move database to SSD
   - Defragment disk (Windows)

Tree Rendering Slow
~~~~~~~~~~~~~~~~~~~

**For large trees (>100 taxa):**

- Disable character mapping temporarily
- Export as Newick, view in specialized viewer
- Use summary trees (consensus) instead of all trees

Error Messages
--------------

"Permission Denied"
~~~~~~~~~~~~~~~~~~~

**Cause:** Insufficient file system permissions

**Solutions:**

1. Run PhyloForester with elevated permissions
2. Move database to folder with write access
3. Check file isn't open in another program

"Out of Memory"
~~~~~~~~~~~~~~~

**Cause:** Not enough RAM for operation

**Solutions:**

1. Close other applications
2. Reduce dataset size
3. Increase virtual memory/swap
4. Use 64-bit version (if available)

"Database Locked"
~~~~~~~~~~~~~~~~~

**Cause:** Another process accessing database

**Solutions:**

1. Close all PhyloForester instances
2. Kill zombie processes
3. Restart computer
4. Copy database to new location

"Invalid Datamatrix"
~~~~~~~~~~~~~~~~~~~~

**Cause:** Data format issue

**Solutions:**

1. Check for:
   - Inconsistent row lengths
   - Invalid characters
   - Missing taxa/character names
2. Re-import from original file
3. Recreate datamatrix manually

Reporting Bugs
--------------

If you encounter a persistent issue:

1. Check if issue is already reported: https://github.com/jikhanjung/PhyloForester/issues
2. Create new issue with:
   - PhyloForester version (Help → About)
   - Operating system and version
   - Steps to reproduce
   - Error messages (exact text)
   - Log files (if available)
   - Screenshots

**Logs location:**

- Windows: ``C:\\Users\\<name>\\AppData\\Local\\PaleoBytes\\PhyloForester\\Logs``
- macOS/Linux: ``~/.local/share/PaleoBytes/PhyloForester/Logs``

Getting Help
------------

- **Documentation**: https://jikhanjung.github.io/PhyloForester/
- **Issues**: https://github.com/jikhanjung/PhyloForester/issues
- **Email**: (if provided by maintainers)

When asking for help, include:

- What you were trying to do
- What you expected to happen
- What actually happened
- Error messages
- PhyloForester version
- Operating system

Next Steps
----------

- Return to :doc:`user_guide` for general usage
- See :doc:`analysis_guide` for analysis-specific help
- See :doc:`developer_guide` for advanced troubleshooting
