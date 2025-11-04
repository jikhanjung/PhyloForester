"""
PyTest configuration and fixtures for PhyloForester tests
"""
import pytest
import os
import tempfile
import shutil
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from peewee import SqliteDatabase
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import PfModel as pm
import PfUtils as pu


@pytest.fixture(scope='session')
def qapp():
    """Create QApplication instance for all Qt tests"""
    from PyQt5.QtCore import QSettings

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Set up settings object that dialogs expect
    app.settings = QSettings("PaleoBytes", "PhyloForester")

    # Set up software paths that dialogs expect
    app.tnt_path = ""
    app.iqtree_path = ""
    app.mrbayes_path = ""
    app.result_path = pu.DEFAULT_RESULT_DIRECTORY

    yield app
    # Don't quit the app as it may be needed by other tests


@pytest.fixture
def test_db():
    """Create a temporary test database"""
    # Create temporary database
    test_db_path = tempfile.mktemp(suffix='.db')
    test_database = SqliteDatabase(test_db_path, pragmas={'foreign_keys': 1})

    # Bind models to test database
    models = [pm.PfProject, pm.PfDatamatrix, pm.PfPackage, pm.PfAnalysis, pm.PfTree]
    test_database.bind(models, bind_refs=False, bind_backrefs=False)

    # Create tables
    test_database.create_tables(models)

    yield test_database

    # Cleanup
    test_database.close()
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture
def test_project(test_db):
    """Create a test project"""
    project = pm.PfProject.create(
        project_name="Test Project",
        project_desc="Test project for unit tests",
        created_at=datetime.now(),
        modified_at=datetime.now()
    )
    yield project
    # Cleanup happens automatically with cascade delete


@pytest.fixture
def test_datamatrix(test_project):
    """Create a test datamatrix"""
    import json

    taxa_list = ["Taxon_A", "Taxon_B", "Taxon_C"]
    datamatrix = [
        ["0", "1", "0"],
        ["1", "0", "1"],
        ["0", "0", "1"]
    ]

    dm = pm.PfDatamatrix.create(
        project=test_project,
        datamatrix_name="Test Matrix",
        datamatrix_desc="Test data matrix",
        datamatrix_index=1,
        datatype=pm.DATATYPE_MORPHOLOGY,
        n_taxa=3,
        n_chars=3,
        taxa_list_json=json.dumps(taxa_list),
        datamatrix_json=json.dumps(datamatrix),
        created_at=datetime.now(),
        modified_at=datetime.now()
    )
    yield dm


@pytest.fixture
def test_package(test_db):
    """Create a test analysis package"""
    package = pm.PfPackage.create(
        package_name="TNT",
        package_version="1.5",
        package_desc="Tree analysis using New Technology",
        package_type=pm.ANALYSIS_TYPE_PARSIMONY,
        run_path="/usr/local/bin/tnt",
        created_at=datetime.now(),
        modified_at=datetime.now()
    )
    yield package


@pytest.fixture
def test_analysis(test_datamatrix, test_package):
    """Create a test analysis"""
    analysis = pm.PfAnalysis.create(
        datamatrix=test_datamatrix,
        package=test_package,
        analysis_type=pm.ANALYSIS_TYPE_PARSIMONY,
        analysis_name="Test Analysis",
        analysis_status=pm.ANALYSIS_STATUS_READY,
        result_directory="/tmp/test_analysis",
        datafile="/tmp/test_data.tnt",
        completion_percentage=0,
        start_datetime=datetime.now()
    )
    yield analysis


@pytest.fixture
def test_tree(test_analysis):
    """Create a test tree"""
    newick = "((Taxon_A:1.0,Taxon_B:1.0):1.0,Taxon_C:2.0);"

    tree = pm.PfTree.create(
        analysis=test_analysis,
        tree_name="Test Tree",
        tree_type=pm.TREE_TYPE_CONSENSUS,
        tree_desc="Test consensus tree",
        newick_text=newick,
        created_at=datetime.now(),
        modified_at=datetime.now()
    )
    yield tree


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)


@pytest.fixture
def sample_nexus_file(temp_dir):
    """Create a sample NEXUS file for testing"""
    nexus_content = """#NEXUS

begin data;
dimensions ntax=3 nchar=3;
format datatype=standard gap=- missing=?;
matrix
Taxon_A 010
Taxon_B 101
Taxon_C 001
;
end;
"""
    nexus_path = os.path.join(temp_dir, "test_data.nex")
    with open(nexus_path, 'w', encoding='utf-8') as f:
        f.write(nexus_content)

    yield nexus_path


@pytest.fixture
def sample_phylip_file(temp_dir):
    """Create a sample PHYLIP file for testing"""
    phylip_content = """3 3
Taxon_A 010
Taxon_B 101
Taxon_C 001
"""
    phylip_path = os.path.join(temp_dir, "test_data.phy")
    with open(phylip_path, 'w', encoding='utf-8') as f:
        f.write(phylip_content)

    yield phylip_path


@pytest.fixture
def sample_tnt_file(temp_dir):
    """Create a sample TNT file for testing"""
    # TNT format: xread on one line, then dataset name and dimensions on next lines
    tnt_content = """xread
'Test data'
3 3
Taxon_A 010
Taxon_B 101
Taxon_C 001
;
"""
    tnt_path = os.path.join(temp_dir, "test_data.tnt")
    with open(tnt_path, 'w', encoding='utf-8') as f:
        f.write(tnt_content)

    yield tnt_path
