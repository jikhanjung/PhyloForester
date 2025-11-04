"""
Tests for PfDialog module - Dialog and UI components
"""

import PfDialog as pd
import PfLogger


class TestAnalysisViewer:
    """Tests for AnalysisViewer"""

    def test_create_viewer(self, qapp, test_db):
        """Test creating AnalysisViewer"""
        logger = PfLogger.setup_logger("test")
        viewer = pd.AnalysisViewer(logger=logger)
        assert viewer is not None

    def test_viewer_has_table(self, qapp, test_db):
        """Test that viewer has tab view"""
        logger = PfLogger.setup_logger("test")
        viewer = pd.AnalysisViewer(logger=logger)

        assert hasattr(viewer, "tabview")
        assert viewer.tabview is not None

    def test_viewer_has_log_output(self, qapp, test_db):
        """Test that viewer has log output widget"""
        logger = PfLogger.setup_logger("test")
        viewer = pd.AnalysisViewer(logger=logger)

        assert hasattr(viewer, "edtAnalysisOutput")
        assert viewer.edtAnalysisOutput is not None


class TestTreeViewer:
    """Tests for TreeViewer"""

    def test_create_viewer(self, qapp, test_db):
        """Test creating TreeViewer"""
        logger = PfLogger.setup_logger("test")
        viewer = pd.TreeViewer(logger=logger)
        assert viewer is not None

    def test_viewer_has_scene(self, qapp, test_db):
        """Test that viewer has tree label widget"""
        logger = PfLogger.setup_logger("test")
        viewer = pd.TreeViewer(logger=logger)

        # TreeViewer should have tree_label for drawing trees
        assert hasattr(viewer, "tree_label")
        assert viewer.tree_label is not None


class TestProjectDialog:
    """Tests for ProjectDialog"""

    def test_create_dialog(self, qapp, test_db):
        """Test creating ProjectDialog"""
        logger = PfLogger.setup_logger("test")
        dialog = pd.ProjectDialog(parent=None, logger=logger)
        assert dialog is not None
        assert dialog.windowTitle() == "PhyloForester - Project Information"

    def test_dialog_has_parent(self, qapp, test_db):
        """Test that dialog stores parent reference"""
        logger = PfLogger.setup_logger("test")
        dialog = pd.ProjectDialog(parent=None, logger=logger)

        # Dialog should have parent attribute
        assert hasattr(dialog, "parent")


class TestDatamatrixDialog:
    """Tests for DatamatrixDialog"""

    def test_create_dialog(self, qapp, test_project):
        """Test creating DatamatrixDialog"""
        logger = PfLogger.setup_logger("test")
        dialog = pd.DatamatrixDialog(parent=None, logger=logger)
        assert dialog is not None
        assert dialog.windowTitle() == "PhyloForester - Datamatrix Information"

    def test_dialog_has_parent(self, qapp, test_project):
        """Test that dialog stores parent reference"""
        logger = PfLogger.setup_logger("test")
        dialog = pd.DatamatrixDialog(parent=None, logger=logger)

        assert hasattr(dialog, "parent")


class TestAnalysisDialog:
    """Tests for AnalysisDialog"""

    def test_create_dialog(self, qapp, test_datamatrix):
        """Test creating AnalysisDialog"""
        logger = PfLogger.setup_logger("test")
        dialog = pd.AnalysisDialog(parent=None, logger=logger)
        assert dialog is not None
        assert dialog.windowTitle() == "PhyloForester - Run Analysis"

    def test_dialog_has_parent(self, qapp, test_datamatrix):
        """Test that dialog stores parent reference"""
        logger = PfLogger.setup_logger("test")
        dialog = pd.AnalysisDialog(parent=None, logger=logger)

        assert hasattr(dialog, "parent")


class TestPreferencesDialog:
    """Tests for PreferencesDialog"""

    def test_create_dialog(self, qapp, test_db):
        """Test creating PreferencesDialog"""
        logger = PfLogger.setup_logger("test")
        dialog = pd.PreferencesDialog(parent=None, logger=logger)
        assert dialog is not None
        assert dialog.windowTitle() == "Preferences"

    def test_dialog_has_parent(self, qapp, test_db):
        """Test that dialog stores parent reference"""
        logger = PfLogger.setup_logger("test")
        dialog = pd.PreferencesDialog(parent=None, logger=logger)

        assert hasattr(dialog, "parent")


class TestDialogIntegration:
    """Integration tests for basic dialog creation"""

    def test_all_dialogs_accept_logger(self, qapp, test_db):
        """Test that all dialog classes accept logger parameter"""
        logger = PfLogger.setup_logger("test")

        # All dialogs should accept logger without error
        project_dialog = pd.ProjectDialog(parent=None, logger=logger)
        dm_dialog = pd.DatamatrixDialog(parent=None, logger=logger)
        analysis_dialog = pd.AnalysisDialog(parent=None, logger=logger)
        pref_dialog = pd.PreferencesDialog(parent=None, logger=logger)

        assert all(
            [
                hasattr(project_dialog, "logger"),
                hasattr(dm_dialog, "logger"),
                hasattr(analysis_dialog, "logger"),
                hasattr(pref_dialog, "logger"),
            ]
        )

    def test_viewers_accept_logger(self, qapp, test_db):
        """Test that viewer classes accept logger parameter"""
        logger = PfLogger.setup_logger("test")

        # Viewers should accept logger
        analysis_viewer = pd.AnalysisViewer(logger=logger)
        tree_viewer = pd.TreeViewer(logger=logger)

        assert hasattr(analysis_viewer, "logger")
        assert hasattr(tree_viewer, "logger")
