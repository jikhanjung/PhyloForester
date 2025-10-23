"""
Tests for PfUtils module
"""
import pytest
import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PfUtils import (
    PhyloForesterException,
    FileOperationError,
    ProcessExecutionError,
    DataParsingError,
    safe_file_read,
    safe_file_write,
    safe_json_loads
)


class TestExceptionClasses:
    """Test custom exception classes"""

    def test_base_exception(self):
        """Test PhyloForesterException"""
        exc = PhyloForesterException("Test error")
        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)

    def test_file_operation_error(self):
        """Test FileOperationError"""
        exc = FileOperationError("File error")
        assert isinstance(exc, PhyloForesterException)
        assert isinstance(exc, Exception)

    def test_process_execution_error(self):
        """Test ProcessExecutionError"""
        exc = ProcessExecutionError("Process error")
        assert isinstance(exc, PhyloForesterException)

    def test_data_parsing_error(self):
        """Test DataParsingError"""
        exc = DataParsingError("Parse error")
        assert isinstance(exc, PhyloForesterException)


class TestSafeFileRead:
    """Test safe_file_read function"""

    def test_read_success(self, tmp_path):
        """Test successful file read"""
        test_file = tmp_path / "test.txt"
        test_content = "Hello World\nLine 2"
        test_file.write_text(test_content, encoding='utf-8')

        content = safe_file_read(str(test_file))
        assert content == test_content

    def test_read_not_found(self):
        """Test file not found error"""
        with pytest.raises(FileOperationError) as exc_info:
            safe_file_read("nonexistent_file.txt")
        assert "File not found" in str(exc_info.value)

    def test_read_permission_denied(self, tmp_path):
        """Test permission denied error"""
        test_file = tmp_path / "noperm.txt"
        test_file.write_text("content")
        test_file.chmod(0o000)

        try:
            with pytest.raises(FileOperationError) as exc_info:
                safe_file_read(str(test_file))
            assert "Permission denied" in str(exc_info.value)
        finally:
            test_file.chmod(0o644)  # Restore permissions

    def test_read_binary_mode(self, tmp_path):
        """Test reading in binary mode"""
        test_file = tmp_path / "binary.dat"
        test_data = b'\x00\x01\x02\x03'
        test_file.write_bytes(test_data)

        content = safe_file_read(str(test_file), mode='rb', encoding=None)
        assert content == test_data


class TestSafeFileWrite:
    """Test safe_file_write function"""

    def test_write_success(self, tmp_path):
        """Test successful file write"""
        test_file = tmp_path / "output.txt"
        test_content = "Test Content\nLine 2"

        safe_file_write(str(test_file), test_content)

        assert test_file.read_text(encoding='utf-8') == test_content

    def test_write_creates_directory(self, tmp_path):
        """Test that parent directories are created"""
        test_file = tmp_path / "subdir" / "nested" / "file.txt"
        test_content = "Content"

        safe_file_write(str(test_file), test_content)

        assert test_file.exists()
        assert test_file.read_text(encoding='utf-8') == test_content

    def test_write_permission_denied(self, tmp_path):
        """Test permission denied error"""
        test_dir = tmp_path / "nowrite"
        test_dir.mkdir()
        test_dir.chmod(0o444)  # Read-only

        try:
            with pytest.raises(FileOperationError) as exc_info:
                safe_file_write(str(test_dir / "file.txt"), "content")
            assert "Permission denied" in str(exc_info.value) or "OS error" in str(exc_info.value)
        finally:
            test_dir.chmod(0o755)  # Restore permissions

    def test_write_append_mode(self, tmp_path):
        """Test append mode"""
        test_file = tmp_path / "append.txt"
        test_file.write_text("Line 1\n")

        safe_file_write(str(test_file), "Line 2\n", mode='a')

        assert test_file.read_text() == "Line 1\nLine 2\n"


class TestSafeJsonLoads:
    """Test safe_json_loads function"""

    def test_valid_json(self):
        """Test valid JSON parsing"""
        json_str = '{"key": "value", "number": 42}'
        data = safe_json_loads(json_str)

        assert data == {"key": "value", "number": 42}

    def test_valid_json_array(self):
        """Test valid JSON array"""
        json_str = '[1, 2, 3, "four"]'
        data = safe_json_loads(json_str)

        assert data == [1, 2, 3, "four"]

    def test_invalid_json_with_default(self):
        """Test invalid JSON with default value"""
        json_str = 'invalid json {not valid}'
        data = safe_json_loads(json_str, default={})

        assert data == {}

    def test_invalid_json_with_default_list(self):
        """Test invalid JSON with default list"""
        json_str = 'bad json'
        data = safe_json_loads(json_str, default=[])

        assert data == []

    def test_invalid_json_no_default(self):
        """Test invalid JSON without default raises exception"""
        json_str = 'invalid json'

        with pytest.raises(DataParsingError) as exc_info:
            safe_json_loads(json_str)
        assert "Invalid JSON" in str(exc_info.value)

    def test_empty_string_with_default(self):
        """Test empty string with default"""
        data = safe_json_loads('', default={})
        assert data == {}

    def test_empty_string_no_default(self):
        """Test empty string without default"""
        with pytest.raises(DataParsingError) as exc_info:
            safe_json_loads('')
        assert "Empty JSON" in str(exc_info.value)

    def test_none_with_default(self):
        """Test None with default"""
        data = safe_json_loads(None, default=[])
        assert data == []

    def test_none_no_default(self):
        """Test None without default"""
        with pytest.raises(DataParsingError):
            safe_json_loads(None)


class TestPhyloDatafile:
    """Tests for PhyloDatafile class"""

    def test_create_datafile(self):
        """Test creating PhyloDatafile instance"""
        from PfUtils import PhyloDatafile
        datafile = PhyloDatafile()
        assert datafile is not None
        assert datafile.dataset_name == ''
        assert datafile.n_taxa == 0
        assert datafile.n_chars == 0

    def test_loadfile_nexus(self, sample_nexus_file):
        """Test loading a NEXUS file"""
        from PfUtils import PhyloDatafile
        datafile = PhyloDatafile()
        result = datafile.loadfile(sample_nexus_file)

        assert result is True
        assert datafile.file_type == 'Nexus'
        assert datafile.n_taxa == 3
        assert datafile.n_chars == 3
        assert len(datafile.taxa_list) == 3
        assert 'Taxon_A' in datafile.taxa_list
        assert 'Taxon_B' in datafile.taxa_list
        assert 'Taxon_C' in datafile.taxa_list

    def test_loadfile_phylip(self, sample_phylip_file):
        """Test loading a PHYLIP file"""
        from PfUtils import PhyloDatafile
        datafile = PhyloDatafile()
        result = datafile.loadfile(sample_phylip_file)

        assert result is True
        assert datafile.file_type == 'Phylip'
        # n_taxa and n_chars are stored as strings in PHYLIP parsing
        assert int(datafile.n_taxa) == 3
        assert int(datafile.n_chars) == 3
        assert len(datafile.taxa_list) == 3

    def test_loadfile_tnt(self, sample_tnt_file):
        """Test loading a TNT file"""
        from PfUtils import PhyloDatafile
        datafile = PhyloDatafile()
        result = datafile.loadfile(sample_tnt_file)

        assert result is True
        assert datafile.file_type == 'TNT'
        # TNT format: first number is nchar, second is ntax
        assert int(datafile.n_chars) == 3
        assert int(datafile.n_taxa) == 3
        assert len(datafile.taxa_list) == 3

    def test_loadfile_nonexistent(self):
        """Test loading non-existent file"""
        from PfUtils import PhyloDatafile
        datafile = PhyloDatafile()
        result = datafile.loadfile('/nonexistent/file.nex')

        assert result is False

    def test_loadfile_by_extension_nex(self, temp_dir):
        """Test file type detection by .nex extension"""
        from PfUtils import PhyloDatafile
        import os

        nex_path = os.path.join(temp_dir, "test.nex")
        with open(nex_path, 'w') as f:
            f.write("#NEXUS\n\nbegin data;\ndimensions ntax=2 nchar=2;\nformat datatype=standard;\nmatrix\nA 01\nB 10\n;\nend;")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        assert result is True
        assert datafile.file_type == 'Nexus'

    def test_loadfile_by_extension_phylip(self, temp_dir):
        """Test file type detection by .phy extension"""
        from PfUtils import PhyloDatafile
        import os

        phy_path = os.path.join(temp_dir, "test.phy")
        with open(phy_path, 'w') as f:
            f.write("2 2\nA 01\nB 10\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(phy_path)

        assert result is True
        assert datafile.file_type == 'Phylip'

    def test_loadfile_by_content_nexus(self, temp_dir):
        """Test file type detection by content (#NEXUS)"""
        from PfUtils import PhyloDatafile
        import os

        # File without standard extension but with NEXUS content
        txt_path = os.path.join(temp_dir, "test.txt")
        with open(txt_path, 'w') as f:
            f.write("#NEXUS\n\nbegin data;\ndimensions ntax=2 nchar=2;\nformat datatype=standard;\nmatrix\nA 01\nB 10\n;\nend;")

        datafile = PhyloDatafile()
        result = datafile.loadfile(txt_path)

        assert result is True
        assert datafile.file_type == 'Nexus'

    def test_loadfile_by_content_tnt(self, temp_dir):
        """Test file type detection by content (xread)"""
        from PfUtils import PhyloDatafile
        import os

        # File without standard extension but with TNT content
        txt_path = os.path.join(temp_dir, "test.txt")
        with open(txt_path, 'w') as f:
            f.write("xread 'test' 2 2\nA 01\nB 10\n;")

        datafile = PhyloDatafile()
        result = datafile.loadfile(txt_path)

        assert result is True
        assert datafile.file_type == 'TNT'

    def test_datafile_taxa_list(self, sample_nexus_file):
        """Test that taxa list is properly populated"""
        from PfUtils import PhyloDatafile
        datafile = PhyloDatafile()
        datafile.loadfile(sample_nexus_file)

        assert len(datafile.taxa_list) == datafile.n_taxa
        assert all(isinstance(taxon, str) for taxon in datafile.taxa_list)

    def test_datafile_datamatrix(self, sample_nexus_file):
        """Test that data matrix is properly populated"""
        from PfUtils import PhyloDatafile
        datafile = PhyloDatafile()
        datafile.loadfile(sample_nexus_file)

        assert len(datafile.datamatrix) == datafile.n_taxa
        if len(datafile.datamatrix) > 0:
            assert len(datafile.datamatrix[0]) == datafile.n_chars


class TestPhyloTreefile:
    """Tests for PhyloTreefile class"""

    def test_create_treefile(self):
        """Test creating PhyloTreefile instance"""
        from PfUtils import PhyloTreefile
        treefile = PhyloTreefile()
        assert treefile is not None
        assert len(treefile.tree_list) == 0
        assert treefile.file_type is None

    def test_readtree_newick(self, temp_dir):
        """Test reading Newick tree file"""
        from PfUtils import PhyloTreefile
        import os

        tre_path = os.path.join(temp_dir, "test.tre")
        newick = "((A:1.0,B:1.0):1.0,C:2.0);"
        with open(tre_path, 'w') as f:
            f.write(newick)

        treefile = PhyloTreefile()
        result = treefile.readtree(tre_path, 'tre')

        assert result is not False
        assert treefile.file_type == 'tre'
        assert treefile.file_text is not None
        assert newick in treefile.file_text

    def test_readtree_nexus(self, temp_dir):
        """Test reading NEXUS tree file"""
        from PfUtils import PhyloTreefile
        import os

        nex_path = os.path.join(temp_dir, "test.nex")
        content = "#NEXUS\n\nbegin trees;\ntree tree1 = ((A,B),C);\nend;"
        with open(nex_path, 'w') as f:
            f.write(content)

        treefile = PhyloTreefile()
        result = treefile.readtree(nex_path, 'Nexus')

        assert result is not False
        assert treefile.file_type == 'Nexus'

    def test_readtree_nonexistent(self):
        """Test reading non-existent tree file"""
        from PfUtils import PhyloTreefile
        treefile = PhyloTreefile()
        result = treefile.readtree('/nonexistent/file.tre', 'tre')

        assert result is False

    def test_readtree_auto_detect_nexus(self, temp_dir):
        """Test automatic detection of NEXUS file type"""
        from PfUtils import PhyloTreefile
        import os

        nex_path = os.path.join(temp_dir, "test.nexus")
        content = "#NEXUS\n\nbegin trees;\ntree tree1 = ((A,B),C);\nend;"
        with open(nex_path, 'w') as f:
            f.write(content)

        treefile = PhyloTreefile()
        # Pass None or empty string for filetype to trigger auto-detection
        result = treefile.readtree(nex_path, None)

        assert result is not False
        assert treefile.file_type == 'Nexus'

    def test_readtree_auto_detect_tre(self, temp_dir):
        """Test automatic detection of .tre file type"""
        from PfUtils import PhyloTreefile
        import os

        tre_path = os.path.join(temp_dir, "test.tre")
        newick = "((A,B),C);"
        with open(tre_path, 'w') as f:
            f.write(newick)

        treefile = PhyloTreefile()
        # Pass None for filetype to trigger auto-detection
        result = treefile.readtree(tre_path, None)

        assert result is not False
        assert treefile.file_type == 'tre'


class TestPhyloMatrix:
    """Tests for PhyloMatrix class"""

    def test_create_matrix(self):
        """Test creating PhyloMatrix instance"""
        from PfUtils import PhyloMatrix
        matrix = PhyloMatrix()
        assert matrix is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
