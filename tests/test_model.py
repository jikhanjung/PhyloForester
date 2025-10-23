"""
Tests for PfModel module - Database models and operations
"""
import pytest
import json
from datetime import datetime
import os
import tempfile

import PfModel as pm
import PfUtils as pu


class TestPfProject:
    """Tests for PfProject model"""

    def test_create_project(self, test_db):
        """Test creating a new project"""
        project = pm.PfProject.create(
            project_name="New Project",
            project_desc="Test description"
        )
        assert project.project_name == "New Project"
        assert project.project_desc == "Test description"
        assert project.created_at is not None
        assert project.modified_at is not None

    def test_project_cascade_delete(self, test_db):
        """Test that deleting project cascades to datamatrices"""
        project = pm.PfProject.create(project_name="Test")
        dm = pm.PfDatamatrix.create(
            project=project,
            datamatrix_name="Test Matrix",
            n_taxa=3,
            n_chars=3
        )
        dm_id = dm.id

        project.delete_instance()

        # Datamatrix should be deleted
        assert pm.PfDatamatrix.select().where(pm.PfDatamatrix.id == dm_id).count() == 0


class TestPfDatamatrix:
    """Tests for PfDatamatrix model"""

    def test_create_datamatrix(self, test_project):
        """Test creating a new datamatrix"""
        dm = pm.PfDatamatrix.create(
            project=test_project,
            datamatrix_name="Test Matrix",
            datamatrix_desc="Test description",
            datatype=pm.DATATYPE_MORPHOLOGY,
            n_taxa=3,
            n_chars=5
        )
        assert dm.datamatrix_name == "Test Matrix"
        assert dm.n_taxa == 3
        assert dm.n_chars == 5
        assert dm.datatype == pm.DATATYPE_MORPHOLOGY

    def test_datamatrix_get_taxa_list(self, test_datamatrix):
        """Test getting taxa list from datamatrix"""
        taxa_list = test_datamatrix.get_taxa_list()
        assert len(taxa_list) == 3
        assert "Taxon_A" in taxa_list
        assert "Taxon_B" in taxa_list
        assert "Taxon_C" in taxa_list

    def test_datamatrix_as_list(self, test_datamatrix):
        """Test getting datamatrix as list"""
        data = test_datamatrix.datamatrix_as_list()
        assert len(data) == 3  # 3 taxa
        assert len(data[0]) == 3  # 3 characters

    def test_datamatrix_get_character_list_empty(self, test_datamatrix):
        """Test getting character list when none exists"""
        char_list = test_datamatrix.get_character_list()
        assert len(char_list) == test_datamatrix.n_chars
        assert all(c == "" for c in char_list)

    def test_datamatrix_copy(self, test_datamatrix):
        """Test copying a datamatrix"""
        copy_dm = test_datamatrix.copy()
        assert copy_dm.id != test_datamatrix.id
        assert copy_dm.datamatrix_name == test_datamatrix.datamatrix_name
        assert copy_dm.n_taxa == test_datamatrix.n_taxa
        assert copy_dm.n_chars == test_datamatrix.n_chars
        assert copy_dm.datamatrix_json == test_datamatrix.datamatrix_json

    def test_timetable_valid(self, test_datamatrix):
        """Test timetable validation"""
        # Initially no timetable
        assert not test_datamatrix.is_timetable_valid()

        # Add valid timetable
        timetable = [[1.0, 2.0], [2.0, 3.0], [0.0, 1.0]]
        test_datamatrix.taxa_timetable_json = json.dumps(timetable)
        test_datamatrix.save()
        assert test_datamatrix.is_timetable_valid()

        # All zeros should be invalid
        timetable_zeros = [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
        test_datamatrix.taxa_timetable_json = json.dumps(timetable_zeros)
        test_datamatrix.save()
        assert not test_datamatrix.is_timetable_valid()

    def test_get_taxa_timetable(self, test_datamatrix):
        """Test getting taxa timetable"""
        timetable = [[1.0, 2.0], [2.0, 3.0], [0.0, 1.0]]
        test_datamatrix.taxa_timetable_json = json.dumps(timetable)
        test_datamatrix.save()

        retrieved = test_datamatrix.get_taxa_timetable()
        assert retrieved == timetable

    def test_count_dna(self, test_datamatrix):
        """Test DNA character counting"""
        dna_string = "ATCGATCG"
        count = test_datamatrix.count_dna(dna_string)
        assert count == 8

        mixed_string = "ATCG012"
        count = test_datamatrix.count_dna(mixed_string)
        assert count == 4

    def test_count_morphology(self, test_datamatrix):
        """Test morphology character counting"""
        morph_string = "0123456789"
        count = test_datamatrix.count_morphology(morph_string)
        assert count == 10

        mixed_string = "012ABC"
        count = test_datamatrix.count_morphology(mixed_string)
        assert count == 3

    def test_import_file_nexus(self, test_datamatrix, sample_nexus_file):
        """Test importing a NEXUS file"""
        result = test_datamatrix.import_file(sample_nexus_file)
        assert result is True
        assert test_datamatrix.n_taxa > 0
        assert test_datamatrix.n_chars > 0
        assert test_datamatrix.taxa_list_json is not None

    def test_import_file_nonexistent(self, test_datamatrix):
        """Test importing non-existent file"""
        result = test_datamatrix.import_file("/nonexistent/file.nex")
        assert result is False

    def test_matrix_as_string(self, test_datamatrix):
        """Test converting matrix to string format"""
        matrix_str = test_datamatrix.matrix_as_string()
        assert "Taxon_A" in matrix_str
        assert "Taxon_B" in matrix_str
        assert "Taxon_C" in matrix_str

    def test_as_phylip_format(self, test_datamatrix):
        """Test converting to PHYLIP format"""
        phylip_str = test_datamatrix.as_phylip_format()
        assert "3 3" in phylip_str  # dimensions
        assert "Taxon_A" in phylip_str

    def test_as_nexus_format(self, test_datamatrix):
        """Test converting to NEXUS format"""
        nexus_str = test_datamatrix.as_nexus_format()
        assert "#NEXUS" in nexus_str
        assert "begin data;" in nexus_str
        assert "matrix" in nexus_str
        assert "end;" in nexus_str


class TestPfPackage:
    """Tests for PfPackage model"""

    def test_create_package(self, test_db):
        """Test creating an analysis package"""
        package = pm.PfPackage.create(
            package_name="IQ-TREE",
            package_version="2.0",
            package_desc="Maximum likelihood analysis",
            package_type=pm.ANALYSIS_TYPE_ML,
            run_path="/usr/local/bin/iqtree"
        )
        assert package.package_name == "IQ-TREE"
        assert package.package_type == pm.ANALYSIS_TYPE_ML
        assert package.run_path == "/usr/local/bin/iqtree"


class TestPfAnalysis:
    """Tests for PfAnalysis model"""

    def test_create_analysis(self, test_datamatrix, test_package):
        """Test creating an analysis"""
        analysis = pm.PfAnalysis.create(
            datamatrix=test_datamatrix,
            package=test_package,
            analysis_type=pm.ANALYSIS_TYPE_PARSIMONY,
            analysis_name="Test Analysis",
            analysis_status=pm.ANALYSIS_STATUS_READY
        )
        assert analysis.analysis_name == "Test Analysis"
        assert analysis.analysis_type == pm.ANALYSIS_TYPE_PARSIMONY
        assert analysis.analysis_status == pm.ANALYSIS_STATUS_READY
        assert analysis.completion_percentage == 0

    def test_analysis_status_transitions(self, test_analysis):
        """Test analysis status changes"""
        assert test_analysis.analysis_status == pm.ANALYSIS_STATUS_READY

        test_analysis.analysis_status = pm.ANALYSIS_STATUS_RUNNING
        test_analysis.save()
        assert test_analysis.analysis_status == pm.ANALYSIS_STATUS_RUNNING

        test_analysis.analysis_status = pm.ANALYSIS_STATUS_FINISHED
        test_analysis.finish_datetime = datetime.now()
        test_analysis.completion_percentage = 100
        test_analysis.save()
        assert test_analysis.analysis_status == pm.ANALYSIS_STATUS_FINISHED
        assert test_analysis.completion_percentage == 100

    def test_analysis_ml_parameters(self, test_datamatrix, test_package):
        """Test ML analysis parameters"""
        analysis = pm.PfAnalysis.create(
            datamatrix=test_datamatrix,
            package=test_package,
            analysis_type=pm.ANALYSIS_TYPE_ML,
            analysis_name="ML Test",
            ml_bootstrap=1000,
            ml_bootstrap_type=pm.BOOTSTRAP_TYPE_ULTRAFAST,
            ml_substitution_model="GTR+G"
        )
        assert analysis.ml_bootstrap == 1000
        assert analysis.ml_bootstrap_type == pm.BOOTSTRAP_TYPE_ULTRAFAST
        assert analysis.ml_substitution_model == "GTR+G"

    def test_analysis_mcmc_parameters(self, test_datamatrix, test_package):
        """Test MCMC analysis parameters"""
        analysis = pm.PfAnalysis.create(
            datamatrix=test_datamatrix,
            package=test_package,
            analysis_type=pm.ANALYSIS_TYPE_BAYESIAN,
            analysis_name="Bayesian Test",
            mcmc_ngen=2000000,
            mcmc_burnin=2000,
            mcmc_nruns=2,
            mcmc_nchains=4
        )
        assert analysis.mcmc_ngen == 2000000
        assert analysis.mcmc_burnin == 2000
        assert analysis.mcmc_nruns == 2
        assert analysis.mcmc_nchains == 4

    def test_analysis_cascade_delete(self, test_analysis):
        """Test cascade delete from datamatrix to analysis"""
        analysis_id = test_analysis.id
        datamatrix = test_analysis.datamatrix

        datamatrix.delete_instance()

        # Analysis should be deleted
        assert pm.PfAnalysis.select().where(pm.PfAnalysis.id == analysis_id).count() == 0


class TestPfTree:
    """Tests for PfTree model"""

    def test_create_tree(self, test_analysis):
        """Test creating a tree"""
        newick = "((A:1,B:1):1,C:2);"
        tree = pm.PfTree.create(
            analysis=test_analysis,
            tree_name="Consensus Tree",
            tree_type=pm.TREE_TYPE_CONSENSUS,
            newick_text=newick
        )
        assert tree.tree_name == "Consensus Tree"
        assert tree.tree_type == pm.TREE_TYPE_CONSENSUS
        assert tree.newick_text == newick

    def test_tree_options_default(self, test_tree):
        """Test getting default tree options"""
        options = test_tree.get_tree_options()
        assert 'tree_style' in options
        assert 'font_size' in options
        assert options['font_size'] == 10
        assert options['italic_taxa_name'] is False

    def test_tree_options_custom(self, test_tree):
        """Test setting custom tree options"""
        custom_options = {
            'tree_style': pu.TREE_STYLE_BRANCH_LENGTH,
            'font_size': 14,
            'italic_taxa_name': True,
            'timetree': True
        }
        test_tree.pack_tree_options(custom_options)
        test_tree.save()

        retrieved = test_tree.get_tree_options()
        assert retrieved['tree_style'] == pu.TREE_STYLE_BRANCH_LENGTH
        assert retrieved['font_size'] == 14
        assert retrieved['italic_taxa_name'] is True
        assert retrieved['timetree'] is True

    def test_tree_cascade_delete(self, test_tree):
        """Test cascade delete from analysis to tree"""
        tree_id = test_tree.id
        analysis = test_tree.analysis

        analysis.delete_instance()

        # Tree should be deleted
        assert pm.PfTree.select().where(pm.PfTree.id == tree_id).count() == 0


class TestModelIntegration:
    """Integration tests for model interactions"""

    def test_full_workflow(self, test_db):
        """Test a complete workflow from project to tree"""
        # Create project
        project = pm.PfProject.create(
            project_name="Integration Test",
            project_desc="Full workflow test"
        )

        # Create datamatrix
        taxa = ["Species_A", "Species_B", "Species_C"]
        matrix = [["0", "1"], ["1", "0"], ["1", "1"]]
        datamatrix = pm.PfDatamatrix.create(
            project=project,
            datamatrix_name="Test Data",
            n_taxa=3,
            n_chars=2,
            taxa_list_json=json.dumps(taxa),
            datamatrix_json=json.dumps(matrix),
            datatype=pm.DATATYPE_MORPHOLOGY
        )

        # Create package
        package = pm.PfPackage.create(
            package_name="TNT",
            package_version="1.5",
            package_type=pm.ANALYSIS_TYPE_PARSIMONY
        )

        # Create analysis
        analysis = pm.PfAnalysis.create(
            datamatrix=datamatrix,
            package=package,
            analysis_type=pm.ANALYSIS_TYPE_PARSIMONY,
            analysis_name="Integration Analysis",
            analysis_status=pm.ANALYSIS_STATUS_READY
        )

        # Create tree
        tree = pm.PfTree.create(
            analysis=analysis,
            tree_name="Result Tree",
            tree_type=pm.TREE_TYPE_CONSENSUS,
            newick_text="((Species_A,Species_B),Species_C);"
        )

        # Verify relationships
        assert datamatrix.project == project
        assert analysis.datamatrix == datamatrix
        assert tree.analysis == analysis

        # Test cascade delete
        project.delete_instance()
        assert pm.PfDatamatrix.select().where(pm.PfDatamatrix.id == datamatrix.id).count() == 0
        assert pm.PfAnalysis.select().where(pm.PfAnalysis.id == analysis.id).count() == 0
        assert pm.PfTree.select().where(pm.PfTree.id == tree.id).count() == 0

    def test_multiple_analyses_per_datamatrix(self, test_datamatrix, test_package):
        """Test creating multiple analyses from same datamatrix"""
        analysis1 = pm.PfAnalysis.create(
            datamatrix=test_datamatrix,
            package=test_package,
            analysis_type=pm.ANALYSIS_TYPE_PARSIMONY,
            analysis_name="Analysis 1"
        )

        analysis2 = pm.PfAnalysis.create(
            datamatrix=test_datamatrix,
            package=test_package,
            analysis_type=pm.ANALYSIS_TYPE_PARSIMONY,
            analysis_name="Analysis 2"
        )

        # Both should reference same datamatrix
        assert analysis1.datamatrix == test_datamatrix
        assert analysis2.datamatrix == test_datamatrix

        # Check backref
        analyses = list(test_datamatrix.analyses)
        assert len(analyses) >= 2
