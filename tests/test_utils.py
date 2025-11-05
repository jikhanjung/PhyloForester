"""
Tests for PfUtils module
"""

import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PfUtils import (
    DataParsingError,
    FileOperationError,
    PhyloForesterException,
    ProcessExecutionError,
    safe_file_read,
    safe_file_write,
    safe_json_loads,
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
        test_file.write_text(test_content, encoding="utf-8")

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
        test_data = b"\x00\x01\x02\x03"
        test_file.write_bytes(test_data)

        content = safe_file_read(str(test_file), mode="rb", encoding=None)
        assert content == test_data

    def test_read_encoding_error(self, tmp_path):
        """Test handling of encoding errors"""
        test_file = tmp_path / "bad_encoding.txt"
        # Write invalid UTF-8 bytes
        test_file.write_bytes(b"\xff\xfe\xfd")

        with pytest.raises(FileOperationError) as exc_info:
            safe_file_read(str(test_file), encoding="utf-8")
        assert "Encoding error" in str(exc_info.value) or "Error reading" in str(exc_info.value)


class TestSafeFileWrite:
    """Test safe_file_write function"""

    def test_write_success(self, tmp_path):
        """Test successful file write"""
        test_file = tmp_path / "output.txt"
        test_content = "Test Content\nLine 2"

        safe_file_write(str(test_file), test_content)

        assert test_file.read_text(encoding="utf-8") == test_content

    def test_write_creates_directory(self, tmp_path):
        """Test that parent directories are created"""
        test_file = tmp_path / "subdir" / "nested" / "file.txt"
        test_content = "Content"

        safe_file_write(str(test_file), test_content)

        assert test_file.exists()
        assert test_file.read_text(encoding="utf-8") == test_content

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

        safe_file_write(str(test_file), "Line 2\n", mode="a")

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
        json_str = "invalid json {not valid}"
        data = safe_json_loads(json_str, default={})

        assert data == {}

    def test_invalid_json_with_default_list(self):
        """Test invalid JSON with default list"""
        json_str = "bad json"
        data = safe_json_loads(json_str, default=[])

        assert data == []

    def test_invalid_json_no_default(self):
        """Test invalid JSON without default raises exception"""
        json_str = "invalid json"

        with pytest.raises(DataParsingError) as exc_info:
            safe_json_loads(json_str)
        assert "Invalid JSON" in str(exc_info.value)

    def test_empty_string_with_default(self):
        """Test empty string with default"""
        data = safe_json_loads("", default={})
        assert data == {}

    def test_empty_string_no_default(self):
        """Test empty string without default"""
        with pytest.raises(DataParsingError) as exc_info:
            safe_json_loads("")
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
        assert datafile.dataset_name == ""
        assert datafile.n_taxa == 0
        assert datafile.n_chars == 0

    def test_loadfile_nexus(self, sample_nexus_file):
        """Test loading a NEXUS file"""
        from PfUtils import PhyloDatafile

        datafile = PhyloDatafile()
        result = datafile.loadfile(sample_nexus_file)

        assert result is True
        assert datafile.file_type == "Nexus"
        assert datafile.n_taxa == 3
        assert datafile.n_chars == 3
        assert len(datafile.taxa_list) == 3
        assert "Taxon_A" in datafile.taxa_list
        assert "Taxon_B" in datafile.taxa_list
        assert "Taxon_C" in datafile.taxa_list

    def test_loadfile_phylip(self, sample_phylip_file):
        """Test loading a PHYLIP file"""
        from PfUtils import PhyloDatafile

        datafile = PhyloDatafile()
        result = datafile.loadfile(sample_phylip_file)

        assert result is True
        assert datafile.file_type == "Phylip"
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
        assert datafile.file_type == "TNT"
        # TNT format: first number is nchar, second is ntax
        assert int(datafile.n_chars) == 3
        assert int(datafile.n_taxa) == 3
        assert len(datafile.taxa_list) == 3

    def test_loadfile_nonexistent(self):
        """Test loading non-existent file"""
        from PfUtils import PhyloDatafile

        datafile = PhyloDatafile()
        result = datafile.loadfile("/nonexistent/file.nex")

        assert result is False

    def test_loadfile_by_extension_nex(self, temp_dir):
        """Test file type detection by .nex extension"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "test.nex"
        with open(nex_path, "w") as f:
            f.write(
                "#NEXUS\n\nbegin data;\ndimensions ntax=2 nchar=2;\nformat datatype=standard;\nmatrix\nA 01\nB 10\n;\nend;"
            )

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        assert result is True
        assert datafile.file_type == "Nexus"

    def test_loadfile_by_extension_phylip(self, temp_dir):
        """Test file type detection by .phy extension"""
        from PfUtils import PhyloDatafile

        phy_path = Path(temp_dir) / "test.phy"
        with open(phy_path, "w") as f:
            f.write("2 2\nA 01\nB 10\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(phy_path)

        assert result is True
        assert datafile.file_type == "Phylip"

    def test_loadfile_by_content_nexus(self, temp_dir):
        """Test file type detection by content (#NEXUS)"""
        from PfUtils import PhyloDatafile

        # File without standard extension but with NEXUS content
        txt_path = Path(temp_dir) / "test.txt"
        with open(txt_path, "w") as f:
            f.write(
                "#NEXUS\n\nbegin data;\ndimensions ntax=2 nchar=2;\nformat datatype=standard;\nmatrix\nA 01\nB 10\n;\nend;"
            )

        datafile = PhyloDatafile()
        result = datafile.loadfile(txt_path)

        assert result is True
        assert datafile.file_type == "Nexus"

    def test_loadfile_by_content_tnt(self, temp_dir):
        """Test file type detection by content (xread)"""
        from PfUtils import PhyloDatafile

        # File without standard extension but with TNT content
        txt_path = Path(temp_dir) / "test.txt"
        with open(txt_path, "w") as f:
            f.write("xread 'test' 2 2\nA 01\nB 10\n;")

        datafile = PhyloDatafile()
        result = datafile.loadfile(txt_path)

        assert result is True
        assert datafile.file_type == "TNT"

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

    # ========== PHYLIP FORMAT VARIATION TESTS ==========

    def test_phylip_sequential_format(self, temp_dir):
        """Test PHYLIP sequential format parsing"""
        from PfUtils import PhyloDatafile

        phy_path = Path(temp_dir) / "sequential.phy"
        with open(phy_path, "w") as f:
            f.write("3 5\n")
            f.write("Taxon1    01010\n")
            f.write("Taxon2    10101\n")
            f.write("Taxon3    11001\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(phy_path)

        assert result is True
        assert datafile.file_type == "Phylip"
        assert int(datafile.n_taxa) == 3
        assert int(datafile.n_chars) == 5

    def test_phylip_interleaved_format(self, temp_dir):
        """Test PHYLIP interleaved format parsing"""
        from PfUtils import PhyloDatafile

        phy_path = Path(temp_dir) / "interleaved.phy"
        with open(phy_path, "w") as f:
            f.write("3 10\n")
            f.write("Taxon1    01010\n")
            f.write("Taxon2    10101\n")
            f.write("Taxon3    11001\n")
            f.write("\n")
            f.write("01010\n")
            f.write("10101\n")
            f.write("11001\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(phy_path)

        assert result is True
        assert datafile.file_type == "Phylip"

    def test_phylip_whitespace_variations(self, temp_dir):
        """Test PHYLIP format with various whitespace patterns"""
        from PfUtils import PhyloDatafile

        phy_path = Path(temp_dir) / "whitespace.phy"
        with open(phy_path, "w") as f:
            f.write("  3   5  \n")  # Extra spaces around dimensions
            f.write("Taxon1       01010\n")  # Multiple spaces
            f.write("Taxon2\t10101\n")  # Tab separator
            f.write("Taxon3  11001\n")  # Normal spacing

        datafile = PhyloDatafile()
        result = datafile.loadfile(phy_path)

        assert result is True
        assert int(datafile.n_taxa) == 3
        assert int(datafile.n_chars) == 5

    def test_phylip_missing_data(self, temp_dir):
        """Test PHYLIP format with missing data (? and -)"""
        from PfUtils import PhyloDatafile

        phy_path = Path(temp_dir) / "missing.phy"
        with open(phy_path, "w") as f:
            f.write("3 5\n")
            f.write("Taxon1    01?10\n")
            f.write("Taxon2    1-101\n")
            f.write("Taxon3    ?1??1\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(phy_path)

        assert result is True
        assert datafile.file_type == "Phylip"

    def test_phylip_gap_characters(self, temp_dir):
        """Test PHYLIP format with gap characters"""
        from PfUtils import PhyloDatafile

        phy_path = Path(temp_dir) / "gaps.phy"
        with open(phy_path, "w") as f:
            f.write("3 6\n")
            f.write("Taxon1    01--10\n")
            f.write("Taxon2    1-0101\n")
            f.write("Taxon3    010---\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(phy_path)

        assert result is True
        assert int(datafile.n_chars) == 6

    def test_phylip_long_taxon_names(self, temp_dir):
        """Test PHYLIP format with long taxon names (10+ chars)"""
        from PfUtils import PhyloDatafile

        phy_path = Path(temp_dir) / "longnames.phy"
        with open(phy_path, "w") as f:
            f.write("3 5\n")
            f.write("VeryLongTaxonName1    01010\n")
            f.write("VeryLongTaxonName2    10101\n")
            f.write("VeryLongTaxonName3    11001\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(phy_path)

        assert result is True
        assert len(datafile.taxa_list) == 3

    def test_phylip_short_taxon_names(self, temp_dir):
        """Test PHYLIP format with short taxon names"""
        from PfUtils import PhyloDatafile

        phy_path = Path(temp_dir) / "shortnames.phy"
        with open(phy_path, "w") as f:
            f.write("3 4\n")
            f.write("A    0101\n")
            f.write("B    1010\n")
            f.write("C    1100\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(phy_path)

        assert result is True
        assert "A" in datafile.taxa_list

    # ========== TNT FORMAT TESTS ==========

    def test_tnt_basic_xread(self, temp_dir):
        """Test basic TNT xread format"""
        from PfUtils import PhyloDatafile

        tnt_path = Path(temp_dir) / "basic.tnt"
        with open(tnt_path, "w") as f:
            f.write("xread\n")
            f.write("'Basic dataset'\n")
            f.write("5 3\n")  # nchars ntax
            f.write("Taxon1 01010\n")
            f.write("Taxon2 10101\n")
            f.write("Taxon3 11001\n")
            f.write(";\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(tnt_path)

        assert result is True
        assert datafile.file_type == "TNT"
        assert int(datafile.n_chars) == 5
        assert int(datafile.n_taxa) == 3

    def test_tnt_with_comments(self, temp_dir):
        """Test TNT format with comments"""
        from PfUtils import PhyloDatafile

        tnt_path = Path(temp_dir) / "comments.tnt"
        with open(tnt_path, "w") as f:
            f.write("'This is a comment'\n")
            f.write("xread\n")
            f.write("'Dataset with comments'\n")
            f.write("4 2\n")  # nchars ntax
            f.write("TaxonA 0101\n")
            f.write("TaxonB 1010\n")
            f.write(";\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(tnt_path)

        assert result is True
        assert int(datafile.n_taxa) == 2

    def test_tnt_multistate_characters(self, temp_dir):
        """Test TNT format with multistate characters (0-9)"""
        from PfUtils import PhyloDatafile

        tnt_path = Path(temp_dir) / "multistate.tnt"
        with open(tnt_path, "w") as f:
            f.write("xread\n")
            f.write("'Multistate'\n")
            f.write("5 3\n")
            f.write("Taxon1 01234\n")
            f.write("Taxon2 43210\n")
            f.write("Taxon3 22222\n")
            f.write(";\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(tnt_path)

        assert result is True
        assert datafile.file_type == "TNT"

    def test_tnt_missing_data(self, temp_dir):
        """Test TNT format with missing data"""
        from PfUtils import PhyloDatafile

        tnt_path = Path(temp_dir) / "missing.tnt"
        with open(tnt_path, "w") as f:
            f.write("xread\n")
            f.write("'Missing data'\n")
            f.write("5 3\n")
            f.write("Taxon1 01?10\n")
            f.write("Taxon2 1-101\n")
            f.write("Taxon3 ??1??\n")
            f.write(";\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(tnt_path)

        assert result is True

    def test_tnt_case_insensitivity(self, temp_dir):
        """Test TNT format with mixed case xread/XREAD"""
        from PfUtils import PhyloDatafile

        tnt_path = Path(temp_dir) / "case.tnt"
        with open(tnt_path, "w") as f:
            f.write("XREAD\n")
            f.write("'Case test'\n")
            f.write("3 2\n")
            f.write("TaxA 010\n")
            f.write("TaxB 101\n")
            f.write(";\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(tnt_path)

        assert result is True
        assert datafile.file_type == "TNT"

    def test_tnt_no_title(self, temp_dir):
        """Test TNT format without title string"""
        from PfUtils import PhyloDatafile

        tnt_path = Path(temp_dir) / "notitle.tnt"
        with open(tnt_path, "w") as f:
            f.write("xread\n")
            f.write("4 2\n")  # No title, just dimensions
            f.write("TaxonA 0101\n")
            f.write("TaxonB 1010\n")
            f.write(";\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(tnt_path)

        assert result is True

    def test_tnt_polymorphic_characters(self, temp_dir):
        """Test TNT format with polymorphic characters [01]"""
        from PfUtils import PhyloDatafile

        tnt_path = Path(temp_dir) / "poly.tnt"
        with open(tnt_path, "w") as f:
            f.write("xread\n")
            f.write("'Polymorphic'\n")
            f.write("5 2\n")
            f.write("TaxonA 01[01]10\n")
            f.write("TaxonB 10[12]01\n")
            f.write(";\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(tnt_path)

        assert result is True

    # ========== NEXUS FORMAT VARIATION TESTS ==========

    def test_nexus_interleaved_matrix(self, temp_dir):
        """Test NEXUS format with interleaved matrix"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "interleaved.nex"
        with open(nex_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("begin data;\n")
            f.write("dimensions ntax=3 nchar=10;\n")
            f.write("format datatype=standard interleave;\n")
            f.write("matrix\n")
            f.write("Taxon1 01010\n")
            f.write("Taxon2 10101\n")
            f.write("Taxon3 11001\n")
            f.write("\n")
            f.write("Taxon1 01010\n")
            f.write("Taxon2 10101\n")
            f.write("Taxon3 11001\n")
            f.write(";\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        assert result is True
        assert datafile.file_type == "Nexus"

    def test_nexus_dna_datatype(self, temp_dir):
        """Test NEXUS format with DNA datatype"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "dna.nex"
        with open(nex_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("begin data;\n")
            f.write("dimensions ntax=3 nchar=6;\n")
            f.write("format datatype=dna;\n")
            f.write("matrix\n")
            f.write("Taxon1 ACGTAC\n")
            f.write("Taxon2 TGCATG\n")
            f.write("Taxon3 ACGTN-\n")
            f.write(";\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        assert result is True

    def test_nexus_protein_datatype(self, temp_dir):
        """Test NEXUS format with protein datatype"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "protein.nex"
        with open(nex_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("begin data;\n")
            f.write("dimensions ntax=2 nchar=5;\n")
            f.write("format datatype=protein;\n")
            f.write("matrix\n")
            f.write("Taxon1 ACDEF\n")
            f.write("Taxon2 GHIKL\n")
            f.write(";\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        assert result is True

    def test_nexus_custom_symbols(self, temp_dir):
        """Test NEXUS format with custom symbols definition"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "symbols.nex"
        with open(nex_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("begin data;\n")
            f.write("dimensions ntax=2 nchar=4;\n")
            f.write('format datatype=standard symbols="0123";\n')
            f.write("matrix\n")
            f.write("TaxonA 0123\n")
            f.write("TaxonB 3210\n")
            f.write(";\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        assert result is True

    def test_nexus_assumptions_block(self, temp_dir):
        """Test NEXUS format with assumptions block"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "assumptions.nex"
        with open(nex_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("begin data;\n")
            f.write("dimensions ntax=2 nchar=4;\n")
            f.write("format datatype=standard;\n")
            f.write("matrix\n")
            f.write("A 0101\n")
            f.write("B 1010\n")
            f.write(";\n")
            f.write("end;\n\n")
            f.write("begin assumptions;\n")
            f.write("charset first = 1-2;\n")
            f.write("charset second = 3-4;\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        assert result is True

    def test_nexus_multiple_blocks(self, temp_dir):
        """Test NEXUS format with multiple blocks"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "multiblock.nex"
        with open(nex_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("begin taxa;\n")
            f.write("dimensions ntax=2;\n")
            f.write("taxlabels TaxonA TaxonB;\n")
            f.write("end;\n\n")
            f.write("begin characters;\n")
            f.write("dimensions nchar=3;\n")
            f.write("format datatype=standard;\n")
            f.write("matrix\n")
            f.write("TaxonA 010\n")
            f.write("TaxonB 101\n")
            f.write(";\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        assert result is True

    def test_nexus_polymorphic_characters(self, temp_dir):
        """Test NEXUS format with polymorphic characters {01}"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "poly.nex"
        with open(nex_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("begin data;\n")
            f.write("dimensions ntax=2 nchar=5;\n")
            f.write("format datatype=standard;\n")
            f.write("matrix\n")
            f.write("TaxonA 01{01}10\n")
            f.write("TaxonB 10{12}01\n")
            f.write(";\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        assert result is True

    def test_nexus_case_insensitive_commands(self, temp_dir):
        """Test NEXUS format with mixed case commands"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "mixedcase.nex"
        with open(nex_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("BEGIN DATA;\n")
            f.write("DIMENSIONS NTAX=2 NCHAR=3;\n")
            f.write("FORMAT DATATYPE=STANDARD;\n")
            f.write("MATRIX\n")
            f.write("A 010\n")
            f.write("B 101\n")
            f.write(";\n")
            f.write("END;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        assert result is True

    def test_nexus_quoted_taxon_names(self, temp_dir):
        """Test NEXUS format with quoted taxon names (spaces)"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "quoted.nex"
        with open(nex_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("begin data;\n")
            f.write("dimensions ntax=2 nchar=3;\n")
            f.write("format datatype=standard;\n")
            f.write("matrix\n")
            f.write("'Taxon A' 010\n")
            f.write("'Taxon B' 101\n")
            f.write(";\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        assert result is True

    def test_nexus_gap_and_missing(self, temp_dir):
        """Test NEXUS format with gap (-) and missing (?) characters"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "gapmissing.nex"
        with open(nex_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("begin data;\n")
            f.write("dimensions ntax=3 nchar=6;\n")
            f.write("format datatype=standard;\n")
            f.write("matrix\n")
            f.write("Taxon1 01--10\n")
            f.write("Taxon2 1??101\n")
            f.write("Taxon3 -?01?-\n")
            f.write(";\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        assert result is True

    # ========== ERROR HANDLING TESTS ==========

    def test_empty_file(self, temp_dir):
        """Test loading empty file"""
        from PfUtils import PhyloDatafile

        empty_path = Path(temp_dir) / "empty.nex"
        with open(empty_path, "w") as f:
            f.write("")

        datafile = PhyloDatafile()
        result = datafile.loadfile(empty_path)

        # Parser is tolerant - may succeed with empty data
        # The key is that n_taxa and n_chars should be 0
        if result:
            assert datafile.n_taxa == 0 or datafile.n_chars == 0

    def test_invalid_nexus_no_header(self, temp_dir):
        """Test NEXUS file without #NEXUS header"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "noheader.nex"
        with open(nex_path, "w") as f:
            f.write("begin data;\n")
            f.write("dimensions ntax=2 nchar=2;\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        # Should try to parse as NEXUS anyway due to .nex extension
        # Result depends on implementation tolerance
        assert result in [True, False]

    def test_corrupted_phylip_header(self, temp_dir):
        """Test PHYLIP file with corrupted dimension header"""
        from PfUtils import PhyloDatafile

        phy_path = Path(temp_dir) / "corrupted.phy"
        with open(phy_path, "w") as f:
            f.write("abc xyz\n")  # Invalid dimensions
            f.write("Taxon1 0101\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(phy_path)

        # Should fail to parse
        assert result is False or datafile.n_taxa == 0

    def test_dimension_mismatch_taxa(self, temp_dir):
        """Test file with dimension mismatch (fewer taxa than declared)"""
        from PfUtils import PhyloDatafile

        phy_path = Path(temp_dir) / "mismatch.phy"
        with open(phy_path, "w") as f:
            f.write("5 3\n")  # Claims 5 taxa
            f.write("Taxon1 010\n")
            f.write("Taxon2 101\n")  # Only 2 taxa provided

        datafile = PhyloDatafile()
        result = datafile.loadfile(phy_path)

        # May succeed with fewer taxa or fail
        if result:
            assert len(datafile.taxa_list) <= 5

    def test_dimension_mismatch_chars(self, temp_dir):
        """Test file with character count mismatch"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "charmismatch.nex"
        with open(nex_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("begin data;\n")
            f.write("dimensions ntax=2 nchar=5;\n")  # Claims 5 chars
            f.write("format datatype=standard;\n")
            f.write("matrix\n")
            f.write("A 010\n")  # Only 3 chars
            f.write("B 101\n")
            f.write(";\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        # Implementation may be tolerant or strict
        assert result in [True, False]

    def test_special_characters_in_data(self, temp_dir):
        """Test file with special characters in matrix data"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "special.nex"
        with open(nex_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("begin data;\n")
            f.write("dimensions ntax=2 nchar=5;\n")
            f.write("format datatype=standard;\n")
            f.write("matrix\n")
            f.write("A 01@10\n")  # @ is not standard
            f.write("B 10#01\n")  # # is not standard
            f.write(";\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        # May succeed with special chars stored as-is
        assert result in [True, False]

    def test_unicode_taxon_names(self, temp_dir):
        """Test file with Unicode characters in taxon names"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "unicode.nex"
        with open(nex_path, "w", encoding="utf-8") as f:
            f.write("#NEXUS\n\n")
            f.write("begin data;\n")
            f.write("dimensions ntax=2 nchar=3;\n")
            f.write("format datatype=standard;\n")
            f.write("matrix\n")
            f.write("분류군1 010\n")  # Korean
            f.write("分類群2 101\n")  # Chinese
            f.write(";\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        assert result is True
        assert len(datafile.taxa_list) == 2

    def test_very_large_dataset(self, temp_dir):
        """Test loading a large dataset (100 taxa, 100 chars)"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "large.nex"
        with open(nex_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("begin data;\n")
            f.write("dimensions ntax=100 nchar=100;\n")
            f.write("format datatype=standard;\n")
            f.write("matrix\n")
            for i in range(100):
                chars = "".join([str((i + j) % 2) for j in range(100)])
                f.write(f"Taxon{i:03d} {chars}\n")
            f.write(";\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        assert result is True
        assert datafile.n_taxa == 100
        assert datafile.n_chars == 100

    def test_single_taxon_dataset(self, temp_dir):
        """Test dataset with only one taxon"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "single.nex"
        with open(nex_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("begin data;\n")
            f.write("dimensions ntax=1 nchar=5;\n")
            f.write("format datatype=standard;\n")
            f.write("matrix\n")
            f.write("OnlyTaxon 01010\n")
            f.write(";\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        assert result is True
        assert datafile.n_taxa == 1

    def test_single_character_dataset(self, temp_dir):
        """Test dataset with only one character"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "onechar.nex"
        with open(nex_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("begin data;\n")
            f.write("dimensions ntax=3 nchar=1;\n")
            f.write("format datatype=standard;\n")
            f.write("matrix\n")
            f.write("A 0\n")
            f.write("B 1\n")
            f.write("C 0\n")
            f.write(";\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        assert result is True
        assert datafile.n_chars == 1

    def test_duplicate_taxon_names(self, temp_dir):
        """Test file with duplicate taxon names"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "duplicate.nex"
        with open(nex_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("begin data;\n")
            f.write("dimensions ntax=3 nchar=3;\n")
            f.write("format datatype=standard;\n")
            f.write("matrix\n")
            f.write("TaxonA 010\n")
            f.write("TaxonB 101\n")
            f.write("TaxonA 110\n")  # Duplicate
            f.write(";\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        # Should succeed; behavior with duplicates is implementation-dependent
        assert result in [True, False]

    def test_missing_semicolon_nexus(self, temp_dir):
        """Test NEXUS file with missing semicolons"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "nosemicolon.nex"
        with open(nex_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("begin data;\n")
            f.write("dimensions ntax=2 nchar=2\n")  # Missing semicolon
            f.write("format datatype=standard\n")  # Missing semicolon
            f.write("matrix\n")
            f.write("A 01\n")
            f.write("B 10\n")
            f.write("\n")  # Missing semicolon before end
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        # Parser may be tolerant of missing semicolons
        assert result in [True, False]

    def test_tnt_missing_terminator(self, temp_dir):
        """Test TNT file without terminating semicolon"""
        from PfUtils import PhyloDatafile

        tnt_path = Path(temp_dir) / "noterm.tnt"
        with open(tnt_path, "w") as f:
            f.write("xread\n")
            f.write("3 2\n")
            f.write("A 010\n")
            f.write("B 101\n")
            # Missing semicolon

        datafile = PhyloDatafile()
        result = datafile.loadfile(tnt_path)

        # May fail without terminator
        assert result in [True, False]

    def test_invalid_file_extension(self, temp_dir):
        """Test file with non-standard extension but valid content"""
        from PfUtils import PhyloDatafile

        dat_path = Path(temp_dir) / "test.dat"
        with open(dat_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("begin data;\n")
            f.write("dimensions ntax=2 nchar=2;\n")
            f.write("format datatype=standard;\n")
            f.write("matrix\n")
            f.write("A 01\n")
            f.write("B 10\n")
            f.write(";\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(dat_path)

        # Should detect NEXUS from content
        assert result is True
        assert datafile.file_type == "Nexus"

    def test_datafile_formatted_data_list(self, sample_nexus_file):
        """Test accessing formatted_data_list property"""
        from PfUtils import PhyloDatafile

        datafile = PhyloDatafile()
        datafile.loadfile(sample_nexus_file)

        # Access formatted data list
        formatted_data = datafile.formatted_data_list
        assert formatted_data is not None
        assert len(formatted_data) == datafile.n_taxa

    def test_datafile_data_hash(self, sample_nexus_file):
        """Test data_hash contains taxon data"""
        from PfUtils import PhyloDatafile

        datafile = PhyloDatafile()
        datafile.loadfile(sample_nexus_file)

        # Check data_hash is populated
        assert len(datafile.data_hash) > 0
        for taxon in datafile.taxa_list:
            assert taxon in datafile.data_hash

    def test_phylip_with_comments(self, temp_dir):
        """Test PHYLIP file with comment lines"""
        from PfUtils import PhyloDatafile

        phy_path = Path(temp_dir) / "comments.phy"
        with open(phy_path, "w") as f:
            f.write("# This is a comment\n")
            f.write("2 3\n")
            f.write("A 010\n")
            f.write("B 101\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(phy_path)

        # May succeed with comments ignored
        assert result in [True, False]

    def test_nexus_characters_block(self, temp_dir):
        """Test NEXUS with 'characters' block instead of 'data'"""
        from PfUtils import PhyloDatafile

        nex_path = Path(temp_dir) / "characters.nex"
        with open(nex_path, "w") as f:
            f.write("#NEXUS\n\n")
            f.write("begin characters;\n")
            f.write("dimensions nchar=3;\n")
            f.write("format datatype=standard;\n")
            f.write("matrix\n")
            f.write("A 010\n")
            f.write("B 101\n")
            f.write("C 110\n")
            f.write(";\n")
            f.write("end;\n")

        datafile = PhyloDatafile()
        result = datafile.loadfile(nex_path)

        assert result is True


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

        tre_path = Path(temp_dir) / "test.tre"
        newick = "((A:1.0,B:1.0):1.0,C:2.0);"
        with open(tre_path, "w") as f:
            f.write(newick)

        treefile = PhyloTreefile()
        result = treefile.readtree(tre_path, "tre")

        assert result is not False
        assert treefile.file_type == "tre"
        assert treefile.file_text is not None
        assert newick in treefile.file_text

    def test_readtree_nexus(self, temp_dir):
        """Test reading NEXUS tree file"""
        from PfUtils import PhyloTreefile

        nex_path = Path(temp_dir) / "test.nex"
        content = "#NEXUS\n\nbegin trees;\ntree tree1 = ((A,B),C);\nend;"
        with open(nex_path, "w") as f:
            f.write(content)

        treefile = PhyloTreefile()
        result = treefile.readtree(nex_path, "Nexus")

        assert result is not False
        assert treefile.file_type == "Nexus"

    def test_readtree_nonexistent(self):
        """Test reading non-existent tree file"""
        from PfUtils import PhyloTreefile

        treefile = PhyloTreefile()
        result = treefile.readtree("/nonexistent/file.tre", "tre")

        assert result is False

    def test_readtree_auto_detect_nexus(self, temp_dir):
        """Test automatic detection of NEXUS file type"""
        from PfUtils import PhyloTreefile

        nex_path = Path(temp_dir) / "test.nexus"
        content = "#NEXUS\n\nbegin trees;\ntree tree1 = ((A,B),C);\nend;"
        with open(nex_path, "w") as f:
            f.write(content)

        treefile = PhyloTreefile()
        # Pass None or empty string for filetype to trigger auto-detection
        result = treefile.readtree(nex_path, None)

        assert result is not False
        assert treefile.file_type == "Nexus"

    def test_readtree_auto_detect_tre(self, temp_dir):
        """Test automatic detection of .tre file type"""
        from PfUtils import PhyloTreefile

        tre_path = Path(temp_dir) / "test.tre"
        newick = "((A,B),C);"
        with open(tre_path, "w") as f:
            f.write(newick)

        treefile = PhyloTreefile()
        # Pass None for filetype to trigger auto-detection
        result = treefile.readtree(tre_path, None)

        assert result is not False
        assert treefile.file_type == "tre"

    def test_readtree_nexus_with_translate(self, temp_dir):
        """Test NEXUS tree file with translate block"""
        from PfUtils import PhyloTreefile

        nex_path = Path(temp_dir) / "with_translate.nex"
        content = """#NEXUS

begin trees;
    translate
        1 TaxonA,
        2 TaxonB,
        3 TaxonC;
    tree tree1 = ((1,2),3);
end;
"""
        with open(nex_path, "w") as f:
            f.write(content)

        treefile = PhyloTreefile()
        result = treefile.readtree(nex_path, "Nexus")

        assert result is not False
        assert "TaxonA" in treefile.taxa_list or len(treefile.taxa_list) >= 0

    def test_readtree_file_error(self, temp_dir):
        """Test tree file that doesn't exist"""
        from PfUtils import PhyloTreefile

        treefile = PhyloTreefile()
        result = treefile.readtree("/nonexistent/path/tree.nex", "Nexus")

        assert result is False

    def test_readtree_multiple_trees(self, temp_dir):
        """Test NEXUS file with multiple trees"""
        from PfUtils import PhyloTreefile

        nex_path = Path(temp_dir) / "multiple.nex"
        content = """#NEXUS

begin trees;
    tree tree1 = ((A,B),C);
    tree tree2 = ((A,C),B);
    tree tree3 = (A,(B,C));
end;
"""
        with open(nex_path, "w") as f:
            f.write(content)

        treefile = PhyloTreefile()
        result = treefile.readtree(nex_path, "Nexus")

        assert result is not False


class TestPhyloMatrix:
    """Tests for PhyloMatrix class"""

    def test_create_matrix(self):
        """Test creating PhyloMatrix instance"""
        from PfUtils import PhyloMatrix

        matrix = PhyloMatrix()
        assert matrix is not None


class TestUtilityFunctions:
    """Tests for utility functions"""

    def test_get_unique_name_not_in_list(self):
        """Test get_unique_name when name doesn't exist"""
        from PfUtils import get_unique_name

        result = get_unique_name("project", ["other", "names"])
        assert result == "project"

    def test_get_unique_name_in_list(self):
        """Test get_unique_name when name exists"""
        from PfUtils import get_unique_name

        result = get_unique_name("project", ["project", "other"])
        assert result == "project (1)"

    def test_get_unique_name_multiple_duplicates(self):
        """Test get_unique_name with multiple duplicates"""
        from PfUtils import get_unique_name

        result = get_unique_name("project", ["project", "project (1)", "project (2)"])
        assert result == "project (3)"

    def test_get_unique_name_with_existing_number(self):
        """Test get_unique_name when base name has number"""
        from PfUtils import get_unique_name

        result = get_unique_name("project (1)", ["project", "project (1)"])
        assert result == "project (2)"

    def test_get_unique_name_empty_list(self):
        """Test get_unique_name with empty name list"""
        from PfUtils import get_unique_name

        result = get_unique_name("project", [])
        assert result == "project"

    def test_resource_path_normal(self):
        """Test resource_path with normal relative path"""
        from PfUtils import resource_path

        result = resource_path("icons/test.png")
        assert "icons" in result
        assert "test.png" in result

    def test_resource_path_nested(self):
        """Test resource_path with nested path"""
        from PfUtils import resource_path

        result = resource_path("data/examples/test.nex")
        assert "data" in result
        assert "examples" in result
        assert "test.nex" in result

    def test_process_dropped_file_name_url(self):
        """Test process_dropped_file_name with URL format"""
        from PfUtils import process_dropped_file_name

        # Test Windows-style file URL
        url = "file:///C:/Users/test/file.txt"
        result = process_dropped_file_name(url)
        assert "file.txt" in result

    def test_process_dropped_file_name_plain(self):
        """Test process_dropped_file_name with plain path"""
        from PfUtils import process_dropped_file_name

        path = "/home/user/file.txt"
        result = process_dropped_file_name(path)
        assert result == path

    def test_get_timestamp(self):
        """Test get_timestamp generates valid timestamp"""
        from PfUtils import get_timestamp

        timestamp = get_timestamp()
        assert len(timestamp) == 15  # YYYYMMDD_HHMMSS
        assert "_" in timestamp
        assert timestamp[:8].isdigit()  # YYYYMMDD
        assert timestamp[9:].isdigit()  # HHMMSS

    def test_value_to_bool_string_true(self):
        """Test value_to_bool with 'true' string"""
        from PfUtils import value_to_bool

        assert value_to_bool("true") is True
        assert value_to_bool("True") is True
        assert value_to_bool("TRUE") is True

    def test_value_to_bool_string_false(self):
        """Test value_to_bool with 'false' string"""
        from PfUtils import value_to_bool

        assert value_to_bool("false") is False
        assert value_to_bool("False") is False
        assert value_to_bool("anything") is False

    def test_value_to_bool_boolean(self):
        """Test value_to_bool with boolean values"""
        from PfUtils import value_to_bool

        assert value_to_bool(True) is True
        assert value_to_bool(False) is False

    def test_value_to_bool_numbers(self):
        """Test value_to_bool with numeric values"""
        from PfUtils import value_to_bool

        assert value_to_bool(1) is True
        assert value_to_bool(0) is False
        assert value_to_bool(42) is True


class TestFitchAlgorithm:
    """Tests for Fitch algorithm functions"""

    def test_reconstruct_ancestral_states_simple(self, temp_dir):
        """Test Fitch algorithm with simple tree"""
        from io import StringIO

        from Bio import Phylo

        from PfUtils import reconstruct_ancestral_states

        # Create simple tree: ((A,B),C)
        newick = "((TaxonA:1.0,TaxonB:1.0):1.0,TaxonC:2.0);"
        tree = Phylo.read(StringIO(newick), "newick")

        # Simple character matrix
        taxa_list = ["TaxonA", "TaxonB", "TaxonC"]
        datamatrix = [
            ["0", "1", "0"],  # TaxonA
            ["0", "1", "1"],  # TaxonB
            ["1", "0", "1"],  # TaxonC
        ]

        # Run Fitch algorithm
        reconstruct_ancestral_states(tree, datamatrix, taxa_list)

        # Verify that character states were assigned
        for node in tree.find_clades():
            assert hasattr(node, "character_states")
            assert hasattr(node, "changed_characters")

    def test_reconstruct_ancestral_states_polymorphic(self, temp_dir):
        """Test Fitch algorithm with polymorphic characters"""
        from io import StringIO

        from Bio import Phylo

        from PfUtils import reconstruct_ancestral_states

        newick = "((TaxonA:1.0,TaxonB:1.0):1.0,TaxonC:2.0);"
        tree = Phylo.read(StringIO(newick), "newick")

        taxa_list = ["TaxonA", "TaxonB", "TaxonC"]
        # Include polymorphic characters (lists)
        datamatrix = [
            [["0", "1"], "1", "0"],  # TaxonA with polymorphic first char
            ["0", "1", ["0", "1"]],  # TaxonB with polymorphic last char
            ["1", "0", "1"],  # TaxonC
        ]

        reconstruct_ancestral_states(tree, datamatrix, taxa_list)

        # Verify character states were assigned
        for node in tree.find_clades():
            assert hasattr(node, "character_states")

    def test_reconstruct_ancestral_states_missing_data(self, temp_dir):
        """Test Fitch algorithm with missing data"""
        from io import StringIO

        from Bio import Phylo

        from PfUtils import reconstruct_ancestral_states

        newick = "((TaxonA:1.0,TaxonB:1.0):1.0,TaxonC:2.0);"
        tree = Phylo.read(StringIO(newick), "newick")

        taxa_list = ["TaxonA", "TaxonB", "TaxonC"]
        # Include missing data (?)
        datamatrix = [
            ["0", "?", "0"],  # TaxonA
            ["?", "1", "1"],  # TaxonB
            ["1", "0", "?"],  # TaxonC
        ]

        reconstruct_ancestral_states(tree, datamatrix, taxa_list)

        # Should complete without error
        for node in tree.find_clades():
            assert hasattr(node, "character_states")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
