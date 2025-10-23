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
        data = safe_json_loads('', default=None)
        assert data is None

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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
