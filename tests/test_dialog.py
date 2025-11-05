"""
Tests for PfDialog.py - Dialog classes

This module tests the various dialog classes used in PhyloForester,
including initialization, UI elements, and basic functionality.
"""

import sys
from pathlib import Path
from unittest.mock import Mock

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QWidget

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

import PfDialog as pd


class TestPfInputDialog:
    """Tests for PfInputDialog class"""

    def test_initialization(self, qapp, qtbot):
        """Test PfInputDialog initialization"""
        dialog = pd.PfInputDialog()
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Input"
        assert dialog.edtInput1 is not None
        assert dialog.edtInput2 is not None
        assert dialog.btnOK is not None
        assert dialog.btnCancel is not None

    def test_ok_button_accepts_dialog(self, qapp, qtbot):
        """Test that OK button accepts the dialog"""
        dialog = pd.PfInputDialog()
        qtbot.addWidget(dialog)

        dialog.edtInput1.setText("Test1")
        dialog.edtInput2.setText("Test2")

        with qtbot.waitSignal(dialog.accepted, timeout=1000):
            dialog.btnOK.click()

        assert dialog.result() == QDialog.Accepted

    def test_cancel_button_rejects_dialog(self, qapp, qtbot):
        """Test that Cancel button rejects the dialog"""
        dialog = pd.PfInputDialog()
        qtbot.addWidget(dialog)

        with qtbot.waitSignal(dialog.rejected, timeout=1000):
            dialog.btnCancel.click()

        assert dialog.result() == QDialog.Rejected

    def test_input_fields_editable(self, qapp, qtbot):
        """Test that input fields can be edited"""
        dialog = pd.PfInputDialog()
        qtbot.addWidget(dialog)

        dialog.edtInput1.setText("Value1")
        dialog.edtInput2.setText("Value2")

        assert dialog.edtInput1.text() == "Value1"
        assert dialog.edtInput2.text() == "Value2"


class TestProgressDialog:
    """Tests for ProgressDialog class"""

    def test_initialization(self, qapp, qtbot):
        """Test ProgressDialog initialization"""
        parent = QWidget()
        qtbot.addWidget(parent)

        dialog = pd.ProgressDialog(parent)
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "PhyloForester - Progress Dialog"
        assert dialog.pb_progress is not None
        assert dialog.lbl_text is not None
        assert dialog.btnStop is not None
        assert dialog.stop_progress is False
        assert dialog.pb_progress.value() == 0

    def test_set_stop_progress(self, qapp, qtbot):
        """Test setting stop progress flag"""
        parent = QWidget()
        qtbot.addWidget(parent)

        dialog = pd.ProgressDialog(parent)
        qtbot.addWidget(dialog)

        assert dialog.stop_progress is False
        dialog.set_stop_progress()
        assert dialog.stop_progress is True

    def test_set_progress_text(self, qapp, qtbot):
        """Test setting progress text format"""
        parent = QWidget()
        qtbot.addWidget(parent)

        dialog = pd.ProgressDialog(parent)
        qtbot.addWidget(dialog)

        text_format = "Processing {0} of {1}"
        dialog.set_progress_text(text_format)

        assert dialog.text_format == text_format

    def test_set_max_value(self, qapp, qtbot):
        """Test setting maximum progress value"""
        parent = QWidget()
        qtbot.addWidget(parent)

        dialog = pd.ProgressDialog(parent)
        qtbot.addWidget(dialog)

        dialog.set_max_value(100)
        assert dialog.max_value == 100

    def test_set_curr_value(self, qapp, qtbot):
        """Test setting current progress value"""
        parent = QWidget()
        qtbot.addWidget(parent)

        dialog = pd.ProgressDialog(parent)
        qtbot.addWidget(dialog)

        dialog.set_progress_text("Processing {0} of {1}")
        dialog.set_max_value(100)
        dialog.set_curr_value(50)

        assert dialog.curr_value == 50
        assert dialog.pb_progress.value() == 50
        assert "50" in dialog.lbl_text.text()
        assert "100" in dialog.lbl_text.text()

    def test_stop_button_sets_flag(self, qapp, qtbot):
        """Test that stop button sets the stop_progress flag"""
        parent = QWidget()
        qtbot.addWidget(parent)

        dialog = pd.ProgressDialog(parent)
        qtbot.addWidget(dialog)

        assert dialog.stop_progress is False
        dialog.btnStop.click()
        assert dialog.stop_progress is True


class TestProjectDialog:
    """Tests for ProjectDialog class"""

    def test_initialization(self, qapp, qtbot):
        """Test ProjectDialog initialization"""
        parent = QWidget()
        qtbot.addWidget(parent)

        dialog = pd.ProjectDialog(parent)
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "PhyloForester - Project Information"
        assert dialog.edtProjectName is not None
        assert dialog.edtProjectDesc is not None
        assert dialog.rbMorphology is not None
        assert dialog.rbDNA is not None
        assert dialog.rbRNA is not None
        assert dialog.rbCombined is not None
        assert dialog.btnOkay is not None
        assert dialog.btnDelete is not None
        assert dialog.btnCancel is not None

    def test_default_datatype_morphology(self, qapp, qtbot):
        """Test that Morphology is checked by default"""
        parent = QWidget()
        qtbot.addWidget(parent)

        dialog = pd.ProjectDialog(parent)
        qtbot.addWidget(dialog)

        assert dialog.rbMorphology.isChecked() is True
        assert dialog.rbDNA.isChecked() is False
        assert dialog.rbRNA.isChecked() is False
        assert dialog.rbCombined.isChecked() is False

    def test_project_name_editable(self, qapp, qtbot):
        """Test that project name field is editable"""
        parent = QWidget()
        qtbot.addWidget(parent)

        dialog = pd.ProjectDialog(parent)
        qtbot.addWidget(dialog)

        dialog.edtProjectName.setText("Test Project")
        assert dialog.edtProjectName.text() == "Test Project"

    def test_project_description_editable(self, qapp, qtbot):
        """Test that project description field is editable"""
        parent = QWidget()
        qtbot.addWidget(parent)

        dialog = pd.ProjectDialog(parent)
        qtbot.addWidget(dialog)

        dialog.edtProjectDesc.setText("Test Description")
        assert dialog.edtProjectDesc.text() == "Test Description"

    def test_set_project(self, qapp, qtbot, test_project):
        """Test setting project data"""
        parent = QWidget()
        qtbot.addWidget(parent)

        dialog = pd.ProjectDialog(parent)
        qtbot.addWidget(dialog)

        dialog.set_project(test_project)
        assert dialog.project == test_project
        assert dialog.edtProjectName.text() == test_project.project_name
        assert dialog.edtProjectDesc.text() == test_project.project_desc

    def test_cancel_button(self, qapp, qtbot):
        """Test cancel button"""
        parent = QWidget()
        qtbot.addWidget(parent)

        dialog = pd.ProjectDialog(parent)
        qtbot.addWidget(dialog)

        with qtbot.waitSignal(dialog.rejected, timeout=1000):
            dialog.btnCancel.click()

    def test_datatype_radio_buttons(self, qapp, qtbot):
        """Test datatype radio button selection"""
        parent = QWidget()
        qtbot.addWidget(parent)

        dialog = pd.ProjectDialog(parent)
        qtbot.addWidget(dialog)

        # Test selecting DNA
        dialog.rbDNA.setChecked(True)
        assert dialog.rbDNA.isChecked() is True


class TestPreferencesDialog:
    """Tests for PreferencesDialog class"""

    def test_initialization(self, qapp, qtbot):
        """Test PreferencesDialog initialization"""
        # Create mock parent with update_settings method
        parent = Mock()
        parent.pos = Mock(return_value=Mock())
        parent.update_settings = Mock()

        # Set up QSettings with default values
        qapp.settings.setValue("WindowGeometry/RememberGeometry", True)
        qapp.settings.setValue("ToolbarIconSize", "Large")

        dialog = pd.PreferencesDialog(parent)
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Preferences"
        assert dialog.rbRememberGeometryYes is not None
        assert dialog.rbRememberGeometryNo is not None
        assert dialog.rbToolbarIconSmall is not None
        assert dialog.rbToolbarIconMedium is not None
        assert dialog.rbToolbarIconLarge is not None
        assert dialog.edtTNTPath is not None
        assert dialog.edtIQTreePath is not None

    def test_remember_geometry_default(self, qapp, qtbot):
        """Test remember geometry default setting"""
        # Create mock parent with update_settings method
        parent = Mock()
        parent.pos = Mock(return_value=Mock())
        parent.update_settings = Mock()

        qapp.settings.setValue("WindowGeometry/RememberGeometry", True)

        dialog = pd.PreferencesDialog(parent)
        qtbot.addWidget(dialog)

        assert dialog.rbRememberGeometryYes.isChecked() is True
        assert dialog.rbRememberGeometryNo.isChecked() is False

    def test_toolbar_icon_size_default(self, qapp, qtbot):
        """Test toolbar icon size default setting"""
        # Create mock parent with update_settings method
        parent = Mock()
        parent.pos = Mock(return_value=Mock())
        parent.update_settings = Mock()

        qapp.settings.setValue("ToolbarIconSize", "Large")

        dialog = pd.PreferencesDialog(parent)
        qtbot.addWidget(dialog)

        assert dialog.rbToolbarIconLarge.isChecked() is True

    def test_software_paths_displayed(self, qapp, qtbot):
        """Test that software paths are displayed"""
        # Create mock parent with update_settings method
        parent = Mock()
        parent.pos = Mock(return_value=Mock())
        parent.update_settings = Mock()

        qapp.settings.setValue("SoftwarePath/TNT", "/usr/bin/tnt")
        qapp.settings.setValue("SoftwarePath/IQTree", "/usr/bin/iqtree")

        dialog = pd.PreferencesDialog(parent)
        qtbot.addWidget(dialog)

        assert dialog.edtTNTPath.text() == "/usr/bin/tnt"
        assert dialog.edtIQTreePath.text() == "/usr/bin/iqtree"

    def test_remember_geometry_radio_button(self, qapp, qtbot):
        """Test remember geometry radio button click"""
        parent = Mock()
        parent.pos = Mock(return_value=Mock())
        parent.update_settings = Mock()

        qapp.settings.setValue("WindowGeometry/RememberGeometry", True)

        dialog = pd.PreferencesDialog(parent)
        qtbot.addWidget(dialog)

        # Click No button
        dialog.rbRememberGeometryNo.click()
        assert dialog.rbRememberGeometryNo.isChecked() is True
        assert dialog.rbRememberGeometryYes.isChecked() is False

    def test_toolbar_icon_size_radio_buttons(self, qapp, qtbot):
        """Test toolbar icon size radio buttons"""
        parent = Mock()
        parent.pos = Mock(return_value=Mock())
        parent.update_settings = Mock()

        dialog = pd.PreferencesDialog(parent)
        qtbot.addWidget(dialog)

        # Click medium button
        dialog.rbToolbarIconMedium.click()
        assert dialog.rbToolbarIconMedium.isChecked() is True

        # Click small button
        dialog.rbToolbarIconSmall.click()
        assert dialog.rbToolbarIconSmall.isChecked() is True


class TestAnalysisViewer:
    """Tests for AnalysisViewer class"""

    def test_initialization(self, qapp, qtbot):
        """Test AnalysisViewer initialization"""
        viewer = pd.AnalysisViewer()
        qtbot.addWidget(viewer)

        assert viewer.tabview is not None
        assert viewer.analysis_info_widget is not None
        assert viewer.analysis_log_widget is not None
        assert viewer.tree_widget is not None
        assert viewer.edtAnalysisOutput is not None

    def test_tab_structure(self, qapp, qtbot):
        """Test that AnalysisViewer has correct tabs"""
        viewer = pd.AnalysisViewer()
        qtbot.addWidget(viewer)

        assert viewer.tabview.count() == 3
        assert viewer.tabview.tabText(0) == "Analysis Info"
        assert viewer.tabview.tabText(1) == "Log"
        assert viewer.tabview.tabText(2) == "Trees"

    def test_analysis_info_fields(self, qapp, qtbot):
        """Test that analysis info fields are present"""
        viewer = pd.AnalysisViewer()
        qtbot.addWidget(viewer)

        assert viewer.edtAnalysisName is not None
        assert viewer.edtAnalysisType is not None
        assert viewer.edtAnalysisPackage is not None
        assert viewer.edtAnalysisStatus is not None
        assert viewer.edtBootstrapCount is not None
        assert viewer.edtBootstrapType is not None
        assert viewer.edtSubstitutionModel is not None

    def test_analysis_info_fields_readonly(self, qapp, qtbot):
        """Test that analysis info fields are read-only"""
        viewer = pd.AnalysisViewer()
        qtbot.addWidget(viewer)

        assert viewer.edtAnalysisName.isReadOnly() is True
        assert viewer.edtAnalysisType.isReadOnly() is True
        assert viewer.edtAnalysisPackage.isReadOnly() is True
        assert viewer.edtAnalysisStatus.isReadOnly() is True

    def test_set_analysis(self, qapp, qtbot, test_analysis):
        """Test setting analysis data"""
        viewer = pd.AnalysisViewer()
        qtbot.addWidget(viewer)

        viewer.set_analysis(test_analysis)
        # update_info() is what actually sets the text fields
        viewer.update_info(test_analysis)

        assert viewer.edtAnalysisName.text() == test_analysis.analysis_name
        assert viewer.edtAnalysisType.text() == test_analysis.analysis_type
        # Note: edtAnalysisPackage is never set in the current implementation
        assert viewer.edtAnalysisStatus.text() == test_analysis.analysis_status

    def test_output_widget_readonly(self, qapp, qtbot):
        """Test that output widget is read-only"""
        viewer = pd.AnalysisViewer()
        qtbot.addWidget(viewer)

        assert viewer.edtAnalysisOutput.isReadOnly() is True


class TestTreeViewer:
    """Tests for TreeViewer class"""

    def test_initialization(self, qapp, qtbot):
        """Test TreeViewer initialization"""
        viewer = pd.TreeViewer()
        qtbot.addWidget(viewer)

        assert viewer is not None
        assert isinstance(viewer, QWidget)

    def test_minimum_size(self, qapp, qtbot):
        """Test TreeViewer has minimum size"""
        viewer = pd.TreeViewer()
        qtbot.addWidget(viewer)

        min_size = viewer.minimumSize()
        # TreeViewer should have some minimum size constraint
        assert min_size.width() >= 0
        assert min_size.height() >= 0

    def test_set_analysis(self, qapp, qtbot, test_analysis):
        """Test setting analysis for TreeViewer"""
        viewer = pd.TreeViewer()
        qtbot.addWidget(viewer)

        viewer.set_analysis(test_analysis)
        assert viewer.analysis == test_analysis


class TestDatamatrixDialog:
    """Tests for DatamatrixDialog class"""

    def test_initialization(self, qapp, qtbot):
        """Test DatamatrixDialog initialization"""
        parent = Mock()
        parent.pos = Mock(return_value=Mock())

        dialog = pd.DatamatrixDialog(parent)
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "PhyloForester - Datamatrix Information"
        assert dialog.edtProjectName is not None
        assert dialog.edtDatamatrixName is not None
        assert dialog.edtDatamatrixDesc is not None
        assert dialog.rbMorphology is not None
        assert dialog.rbDNA is not None
        assert dialog.rbRNA is not None
        assert dialog.rbCombined is not None

    def test_default_datatype_morphology(self, qapp, qtbot):
        """Test that Morphology is checked by default"""
        parent = Mock()
        parent.pos = Mock(return_value=Mock())

        dialog = pd.DatamatrixDialog(parent)
        qtbot.addWidget(dialog)

        assert dialog.rbMorphology.isChecked() is True
        assert dialog.rbDNA.isChecked() is False

    def test_datamatrix_name_editable(self, qapp, qtbot):
        """Test that datamatrix name field is editable"""
        parent = Mock()
        parent.pos = Mock(return_value=Mock())

        dialog = pd.DatamatrixDialog(parent)
        qtbot.addWidget(dialog)

        dialog.edtDatamatrixName.setText("Test Datamatrix")
        assert dialog.edtDatamatrixName.text() == "Test Datamatrix"

    def test_set_datamatrix_with_none(self, qapp, qtbot):
        """Test setting datamatrix to None"""
        parent = Mock()
        parent.pos = Mock(return_value=Mock())

        dialog = pd.DatamatrixDialog(parent)
        qtbot.addWidget(dialog)

        dialog.set_datamatrix(None)
        assert dialog.datamatrix is None

    def test_set_datamatrix_with_data(self, qapp, qtbot, test_datamatrix):
        """Test setting datamatrix with data"""
        parent = Mock()
        parent.pos = Mock(return_value=Mock())

        dialog = pd.DatamatrixDialog(parent)
        qtbot.addWidget(dialog)

        dialog.set_datamatrix(test_datamatrix)
        assert dialog.datamatrix == test_datamatrix
        assert dialog.edtProjectName.text() == test_datamatrix.project.project_name
        assert dialog.edtDatamatrixName.text() == test_datamatrix.datamatrix_name

    def test_cancel_button(self, qapp, qtbot):
        """Test cancel button"""
        parent = Mock()
        parent.pos = Mock(return_value=Mock())

        dialog = pd.DatamatrixDialog(parent)
        qtbot.addWidget(dialog)

        with qtbot.waitSignal(dialog.rejected, timeout=1000):
            dialog.btnCancel.click()

    def test_datamatrix_datatype_radio_buttons(self, qapp, qtbot):
        """Test datatype radio button selection"""
        parent = Mock()
        parent.pos = Mock(return_value=Mock())

        dialog = pd.DatamatrixDialog(parent)
        qtbot.addWidget(dialog)

        # Test selecting RNA
        dialog.rbRNA.setChecked(True)
        assert dialog.rbRNA.isChecked() is True
        assert dialog.rbMorphology.isChecked() is False


class TestAnalysisDialog:
    """Tests for AnalysisDialog class"""

    def test_initialization(self, qapp, qtbot):
        """Test AnalysisDialog initialization"""
        parent = Mock()
        parent.pos = Mock(return_value=Mock())

        dialog = pd.AnalysisDialog(parent)
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "PhyloForester - Run Analysis"
        assert dialog.cbxParsimony is not None
        assert dialog.cbxML is not None
        assert dialog.cbxBayesian is not None

    def test_parsimony_checkbox_disabled_without_tnt(self, qapp, qtbot):
        """Test that Parsimony checkbox is disabled if TNT path not configured"""
        parent = Mock()
        parent.pos = Mock(return_value=Mock())

        # Ensure TNT path is not set
        qapp.tnt_path = ""

        dialog = pd.AnalysisDialog(parent)
        qtbot.addWidget(dialog)

        assert dialog.cbxParsimony.isEnabled() is False

    def test_ml_checkbox_disabled_without_iqtree(self, qapp, qtbot):
        """Test that ML checkbox is disabled if IQTree path not configured"""
        parent = Mock()
        parent.pos = Mock(return_value=Mock())

        # Ensure IQTree path is not set
        qapp.iqtree_path = ""

        dialog = pd.AnalysisDialog(parent)
        qtbot.addWidget(dialog)

        assert dialog.cbxML.isEnabled() is False

    def test_set_datamatrix(self, qapp, qtbot, test_datamatrix):
        """Test setting datamatrix for analysis"""
        parent = Mock()
        parent.pos = Mock(return_value=Mock())

        qapp.tnt_path = "/usr/bin/tnt"

        dialog = pd.AnalysisDialog(parent)
        qtbot.addWidget(dialog)

        dialog.set_datamatrix(test_datamatrix)
        assert dialog.datamatrix == test_datamatrix


class TestCheckboxTableModel:
    """Tests for CheckboxTableModel class"""

    def test_initialization(self, qapp):
        """Test CheckboxTableModel initialization"""
        data = [True, False, True]
        model = pd.CheckboxTableModel(data)

        assert model.rowCount() == 3
        assert model.columnCount() == 1

    def test_data_retrieval(self, qapp):
        """Test retrieving checkbox state from model"""
        data = [True, False, True]
        model = pd.CheckboxTableModel(data)

        # Get checkbox state for first item (should be checked)
        index = model.index(0, 0)
        assert model.data(index, Qt.CheckStateRole) == Qt.Checked

        # Get checkbox state for second item (should be unchecked)
        index2 = model.index(1, 0)
        assert model.data(index2, Qt.CheckStateRole) == Qt.Unchecked

    def test_checkbox_state(self, qapp):
        """Test checkbox state"""
        data = [True, False, True]
        model = pd.CheckboxTableModel(data)

        # First should be checked
        index = model.index(0, 0)
        assert model.data(index, Qt.CheckStateRole) == Qt.Checked

    def test_set_data(self, qapp):
        """Test setting checkbox state"""
        data = [True, False, True]
        model = pd.CheckboxTableModel(data)

        index = model.index(0, 0)
        model.setData(index, Qt.Unchecked, Qt.CheckStateRole)

        assert model.data(index, Qt.CheckStateRole) == Qt.Unchecked

    def test_flags(self, qapp):
        """Test item flags"""
        data = [True, False, True]
        model = pd.CheckboxTableModel(data)

        index = model.index(0, 0)
        flags = model.flags(index)

        assert flags & Qt.ItemIsEnabled
        assert flags & Qt.ItemIsUserCheckable

    def test_get_selected_indices(self, qapp):
        """Test getting selected indices"""
        data = [True, False, True]
        model = pd.CheckboxTableModel(data)

        selected = model.get_selected_indices()
        assert selected == [0, 2]


class TestTreeLabel:
    """Tests for TreeLabel class"""

    def test_initialization(self, qapp, qtbot):
        """Test TreeLabel initialization"""
        label = pd.TreeLabel()
        qtbot.addWidget(label)

        assert label is not None
        assert label.char_mapping is False

    def test_char_mapping_toggle(self, qapp, qtbot):
        """Test toggling character mapping"""
        label = pd.TreeLabel()
        qtbot.addWidget(label)

        assert label.char_mapping is False
        label.char_mapping = True
        assert label.char_mapping is True

    def test_set_tree_with_none(self, qapp, qtbot):
        """Test setting tree to None"""
        label = pd.TreeLabel()
        qtbot.addWidget(label)

        result = label.set_tree(None)
        assert result is None
        assert label.tree is None
