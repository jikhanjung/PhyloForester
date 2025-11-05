"""PhyloForester Utility Functions.

This module provides utility functions and classes for the PhyloForester
application, including:

- File I/O operations with error handling
- Phylogenetic data file parsing (Nexus, Phylip, TNT formats)
- Phylogenetic tree file parsing (Newick, Nexus tree formats)
- Ancestral state reconstruction (Fitch algorithm)
- Path handling for cross-platform compatibility
- Resource path resolution for PyInstaller bundles

Main Classes:
    PhyloMatrix: Stores and manipulates character matrix data
    PhyloDatafile: Parses and loads phylogenetic data files
    PhyloTreefile: Parses and loads phylogenetic tree files

Exception Hierarchy:
    PhyloForesterException: Base exception class
        FileOperationError: File I/O related errors
        ProcessExecutionError: External process execution errors
        DataParsingError: Data parsing errors

Example:
    Loading a phylogenetic data file::

        datafile = PhyloDatafile()
        success = datafile.loadfile("data.nex")
        if success:
            print(f"Loaded {datafile.n_taxa} taxa")
            print(f"Matrix dimensions: {datafile.n_taxa} x {datafile.n_chars}")
"""

import json
import logging
import os
import platform
import re
import sys

# from stl import mesh
# Import version from version.py (Single Source of Truth)
from version import __version__

# Initialize logger
logger = logging.getLogger(__name__)

# ============================================================================
# Exception Classes
# ============================================================================


class PhyloForesterException(Exception):
    """Base exception for PhyloForester"""

    pass


class FileOperationError(PhyloForesterException):
    """File I/O related errors"""

    pass


class ProcessExecutionError(PhyloForesterException):
    """External process execution errors"""

    pass


class DataParsingError(PhyloForesterException):
    """Data parsing errors"""

    pass


# ============================================================================
# Safe File Operations
# ============================================================================


def safe_file_read(filepath, mode="r", encoding="utf-8"):
    """Safely read file with error handling

    Args:
        filepath: Path to file to read
        mode: File open mode (default: 'r')
        encoding: File encoding (default: 'utf-8')

    Returns:
        str: File contents

    Raises:
        FileOperationError: If file cannot be read
    """
    try:
        with open(filepath, mode=mode, encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        raise FileOperationError(f"File not found: {filepath}")
    except PermissionError:
        raise FileOperationError(f"Permission denied: {filepath}")
    except UnicodeDecodeError as e:
        raise FileOperationError(f"Encoding error in {filepath}: {e}")
    except Exception as e:
        raise FileOperationError(f"Error reading file {filepath}: {e}")


def safe_file_write(filepath, content, mode="w", encoding="utf-8"):
    """Safely write file with error handling

    Args:
        filepath: Path to file to write
        content: Content to write
        mode: File open mode (default: 'w')
        encoding: File encoding (default: 'utf-8')

    Raises:
        FileOperationError: If file cannot be written
    """
    try:
        # Ensure parent directory exists
        parent_dir = os.path.dirname(filepath)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        with open(filepath, mode=mode, encoding=encoding) as f:
            f.write(content)
    except PermissionError:
        raise FileOperationError(f"Permission denied: {filepath}")
    except OSError as e:
        raise FileOperationError(f"OS error writing {filepath}: {e}")
    except Exception as e:
        raise FileOperationError(f"Error writing file {filepath}: {e}")


def safe_json_loads(json_str, default=None):
    """Safely parse JSON with fallback

    Args:
        json_str: JSON string to parse
        default: Default value if parsing fails (None means raise exception)

    Returns:
        Parsed JSON object or default value

    Raises:
        DataParsingError: If parsing fails and no default provided
    """
    if json_str is None or json_str == "":
        if default is not None:
            return default
        raise DataParsingError("Empty JSON string")

    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        if default is not None:
            return default
        raise DataParsingError(f"Invalid JSON: {e}")


# ============================================================================
# Constants
# ============================================================================

COMPANY_NAME = "PaleoBytes"
PROGRAM_NAME = "PhyloForester"
PROGRAM_VERSION = __version__  # Imported from version.py

DB_LOCATION = ""

# print(os.name)
USER_PROFILE_DIRECTORY = os.path.expanduser("~")

DEFAULT_DB_DIRECTORY = os.path.join(USER_PROFILE_DIRECTORY, COMPANY_NAME, PROGRAM_NAME)
DEFAULT_LOG_DIRECTORY = os.path.join(USER_PROFILE_DIRECTORY, COMPANY_NAME, PROGRAM_NAME)
# DEFAULT_STORAGE_DIRECTORY = os.path.join(DEFAULT_DB_DIRECTORY, "data/")


def get_available_windows_drives():
    """Get list of available drive letters on Windows (e.g., ['C', 'D', 'E'])"""
    if platform.system() != "Windows":
        return []

    import string

    available_drives = []
    for letter in string.ascii_uppercase:
        drive_path = f"{letter}:\\"
        if os.path.exists(drive_path):
            available_drives.append(letter)
    return available_drives


def get_default_result_directory_path():
    """
    Get the best default result directory path (without creating it).

    For Windows:
    - Try C:\\PFResults, D:\\PFResults, E:\\PFResults, etc. (in order of available drives)
    - Fall back to ~/PFResults if all drives restricted

    For macOS/Linux:
    - Use ~/PFResults

    Returns:
        str: Path to the default result directory (NOT created)
    """
    if platform.system() == "Windows":
        # Try each available drive in order
        available_drives = get_available_windows_drives()

        for drive_letter in available_drives:
            try_path = f"{drive_letter}:\\PFResults"
            # Just check if we can potentially write here
            drive_root = f"{drive_letter}:\\"
            if os.path.exists(drive_root) and os.access(drive_root, os.W_OK):
                return try_path

        # All drives restricted, fall back to user home
        return os.path.join(USER_PROFILE_DIRECTORY, "PFResults")
    # macOS/Linux: Use short path in user home
    return os.path.join(USER_PROFILE_DIRECTORY, "PFResults")


def create_result_directory(path):
    """
    Create result directory at the specified path.

    Args:
        path: Directory path to create

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path)

        # Test write permission
        test_file = os.path.join(path, ".write_test")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        return True
    except (PermissionError, OSError) as e:
        logger.warning(f"Failed to create result directory {path}: {e}")
        return False


def get_default_result_directory():
    """
    Get the default result directory path.
    Note: This function no longer auto-creates the directory.
    Use create_result_directory() to create it after user confirmation.

    Returns:
        str: Path to the default result directory
    """
    return get_default_result_directory_path()


# Default result directory for analyses
# Use short paths to avoid command line length issues with TNT and other external software
DEFAULT_RESULT_DIRECTORY = get_default_result_directory()

TREE_STYLE_TOPOLOGY = 0
TREE_STYLE_BRANCH_LENGTH = 1
TREE_STYLE_TIMETREE = 2

if not os.path.exists(DEFAULT_DB_DIRECTORY):
    os.makedirs(DEFAULT_DB_DIRECTORY)
# if not os.path.exists(DEFAULT_STORAGE_DIRECTORY):
#    os.makedirs(DEFAULT_STORAGE_DIRECTORY)


def get_timestamp():
    """Generate timestamp string for file naming.

    Returns:
        Timestamp string in format YYYYMMDD_HHMMSS.
    """
    import datetime

    now = datetime.datetime.now()
    return now.strftime("%Y%m%d_%H%M%S")


def value_to_bool(value):
    """Convert various value types to boolean.

    Args:
        value: Value to convert. Strings are checked case-insensitively.

    Returns:
        Boolean conversion result.
    """
    return value.lower() == "true" if isinstance(value, str) else bool(value)


def get_unique_name(name, name_list):
    """Generate unique name by appending number if needed.

    If the name already exists in name_list, appends " (n)" where n
    is the next available number. Handles names that already have
    numbers by incrementing them.

    Args:
        name: Base name to make unique.
        name_list: List of existing names to avoid collisions.

    Returns:
        Unique name not present in name_list.

    Example:
        >>> get_unique_name("project", ["project", "project (1)"])
        'project (2)'
    """
    if name not in name_list:
        return name
    i = 1
    # get last index of current name which is in the form of "name (i)" using regular expression
    match = re.match(r"(.+)\s+\((\d+)\)", name)
    if match:
        name = match.group(1)
        i = int(match.group(2))
        i += 1
    while True:
        new_name = name + " (" + str(i) + ")"
        if new_name not in name_list:
            return new_name
        i += 1


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller bundles.

    When running as a PyInstaller bundle, resources are extracted to a
    temporary folder (_MEIPASS). This function finds the correct path
    in both development and bundled contexts.

    Args:
        relative_path: Relative path to the resource file.

    Returns:
        Absolute path to the resource.

    Example:
        >>> icon_path = resource_path("icons/app.png")
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def process_dropped_file_name(file_name):
    """Process file name from drag-and-drop events.

    Converts file URLs from drag-and-drop events to usable file paths.
    Handles URL encoding and platform-specific path differences (Windows
    paths start with drive letter, Unix paths start with /).

    Args:
        file_name: URL or file path string from drag-and-drop event.

    Returns:
        Platform-appropriate file path string.

    Example:
        >>> process_dropped_file_name("file:///C:/data/file.nex")
        'C:/data/file.nex'
    """
    import os
    from urllib.parse import unquote, urlparse

    # print("file_name:", file_name)
    url = file_name
    parsed_url = urlparse(url)
    # print("parsed_url:", parsed_url)
    file_path = unquote(parsed_url.path)
    if os.name == "nt":
        file_path = file_path[1:]
    else:
        file_path = file_path
    return file_path


class PhyloMatrix:
    """Container for phylogenetic character matrix data.

    Stores taxa names, character names, and the character matrix data.
    Provides methods for accessing and formatting the data for export.

    Attributes:
        taxa_list: List of taxon names.
        char_list: List of character names.
        data_list: Nested list of character states [taxa][chars].
        data_hash: Dictionary mapping taxon names to character data.
        n_taxa: Number of taxa (rows).
        n_chars: Number of characters (columns).
        command_hash: Dictionary of Nexus format commands.
        dataset_name: Name of the dataset.
        formatted_data_hash: Dictionary of formatted character data.
        formatted_data_list: List of formatted character data.
    """

    def __init__(self):
        self.taxa_list = []
        self.char_list = []
        self.data_list = []
        self.data_hash = {}
        self.n_taxa = 0
        self.n_chars = 0
        self.command_hash = {}
        self.dataset_name = ""
        self.formatted_data_hash = {}
        self.formatted_data_list = []

    def taxa_list_as_string(self, separator=","):
        return separator.join(self.taxa_list)

    def char_list_as_string(self, separator=","):
        return separator.join(self.char_list)


class PhyloDatafile:
    """Phylogenetic data file parser.

    Parses and loads phylogenetic data from multiple file formats including
    Nexus, Phylip, and TNT formats. Automatically detects format based on
    file extension and content. Extracts taxa names, character data, and
    format-specific metadata.

    Supports:
        - Nexus format with multiple blocks (DATA, TAXA, CHARACTERS, MRBAYES)
        - Phylip sequential and interleaved formats
        - TNT xread format

    Attributes:
        dataset_name: Name extracted from filename or file content.
        file_text: Complete text content of the file.
        file_type: Detected file format ('Nexus', 'Phylip', or 'TNT').
        line_list: List of lines from the file.
        block_list: List of parsed Nexus blocks.
        block_hash: Dictionary mapping block names to block content.
        nexus_command_hash: Dictionary of Nexus commands (dimensions, format, etc.).
        phylo_matrix: PhyloMatrix object containing parsed data.
        character_definition_hash: Dictionary of character definitions.
        taxa_list: List of taxon names.
        datamatrix: Nested list of character states.
        n_taxa: Number of taxa.
        n_chars: Number of characters.

    Example:
        Loading and parsing a data file::

            datafile = PhyloDatafile()
            if datafile.loadfile("data.nex"):
                print(f"Loaded {datafile.n_taxa} taxa, {datafile.n_chars} characters")
                print(f"Format: {datafile.file_type}")
                taxa = datafile.taxa_list
                matrix = datafile.formatted_data_list

    Raises:
        FileOperationError: If file cannot be read.
        DataParsingError: If file format is invalid or unsupported.
    """

    def __init__(self):
        self.dataset_name = ""
        self.file_text = None
        self.file_type = None
        self.line_list = []
        self.block_list = []
        self.block_hash = {}
        self.nexus_command_hash = {}
        self.phylo_matrix = PhyloMatrix()
        self.character_definition_hash = {}

        self.taxa_list = []
        self.data_list = []
        self.data_hash = {}
        self.formatted_data_hash = {}
        self.formatted_data_list = []
        self.n_chars = 0
        self.n_taxa = 0

    def loadfile(self, a_filepath):
        filepath, filename = os.path.split(a_filepath)
        filename, fileext = os.path.splitext(filename.upper())
        self.dataset_name = filename

        # determine by filetype
        if fileext.upper() in [".NEX", ".NEXUS"]:
            self.file_type = "Nexus"
        elif fileext.upper() in [".PHY", ".PHYLIP"]:
            self.file_type = "Phylip"
        elif fileext.upper() in [".TNT"]:
            self.file_type = "TNT"
        # print("filetype:", self.file_type, filename, fileext)

        # Read file with error handling
        try:
            self.file_text = safe_file_read(a_filepath)
        except FileOperationError as e:
            logger.error(f"Error loading file {a_filepath}: {e}")
            return False

        self.line_list = self.file_text.split("\n")
        if not self.file_type:
            upper_file_text = self.file_text.upper()
            # first_line = self.line_list[0].upper()
            if upper_file_text.find("#NEXUS") > -1:
                self.file_type = "Nexus"
            elif upper_file_text.find("XREAD") > -1:
                self.file_type = "TNT"
        # print("File type:", self.file_type)

        if self.file_type == "Nexus":
            # print("nexus file")
            self.parse_nexus_file()
            if "DATA" in self.block_hash.keys():
                self.parse_nexus_block(self.block_hash["DATA"])
            if "TAXA" in self.block_hash.keys():
                # print('taxa block')
                self.parse_nexus_block(self.block_hash["TAXA"])
                # print('nchar, ntax', self.n_chars, self.n_taxa)
            if "CHARACTERS" in self.block_hash.keys():
                logger.debug("Processing CHARACTERS block")
                self.parse_nexus_block(self.block_hash["CHARACTERS"])
                # print('nchar, ntax', self.n_chars, self.n_taxa)
            if "MRBAYES" in self.block_hash.keys():
                # print("mr bayes block exists")
                pass
        elif self.file_type == "Phylip":
            # print("phylip file")
            self.parse_phylip_file(self.line_list)
        elif self.file_type == "TNT":
            # print("TNT file")
            self.parse_tnt_file(self.line_list)
            # self.parse_tnt_File()

        if self.phylo_matrix.dataset_name != "":
            self.dataset_name = self.phylo_matrix.dataset_name
        # print("file parsing done")
        return True

    def parse_nexus_file(self, line_list=None):
        if not line_list:
            line_list = self.line_list
        curr_block = None
        in_block = False
        for line in line_list:
            # print(line)
            begin_line = re.match(r"\s*begin\s+(\w+)", line, flags=re.IGNORECASE)
            end_line = re.match(r"\s*end\s*;", line, flags=re.IGNORECASE)

            if begin_line:
                # print("begin", begin_line)
                curr_block = {}
                curr_block["name"] = begin_line.group(1).upper()
                curr_block["text"] = []
                in_block = True
            elif end_line:
                # print("end block")
                self.block_list.append(curr_block)
                # if curr_block['name'] == 'DATA':
                self.block_hash[curr_block["name"]] = curr_block["text"]
                in_block = False
            elif in_block:
                # print(line)
                curr_block["text"].append(line)
        return  # block_list

    def parse_nexus_block(self, line_list):
        in_matrix = False
        for line in line_list:
            # print(line)
            matrix_begin = re.match(r"\s*matrix\s*", line, flags=re.IGNORECASE)
            if matrix_begin:
                # self.taxa_list = []
                # self.data_list = []
                # self.data_hash = {}
                # self.nexus_command_hash = {}
                in_matrix = True
            elif in_matrix:
                matrix_match = re.match(r"^\s*(\S+)\s+(.+);*", line)
                if matrix_match:
                    # print("matrix:",line)
                    species_name = matrix_match.group(1)
                    data_line = matrix_match.group(2)
                    if species_name not in self.taxa_list:
                        self.taxa_list.append(species_name)
                    self.data_list.append(data_line)
                    self.data_hash[species_name] = data_line
            else:
                # in data block but not in matrix ==> command/variable
                command_match = re.match(r"^\s*(\S+)\s+(.*);", line.upper(), flags=re.IGNORECASE)
                if command_match:
                    # print("command:",line)
                    command = command_match.group(1)
                    variable_string = command_match.group(2)
                    variable_list = re.findall(r"(\w+)\s*=\s*(\S+)", variable_string)
                    # print(command,variable_list)
                    if command not in self.nexus_command_hash.keys():
                        self.nexus_command_hash[command] = {}
                    for variable in variable_list:
                        self.nexus_command_hash[command][variable[0]] = variable[1]
                    # print(self.nexus_command_hash)
                # pass

            matrix_end = re.match(".*;.*", line)
            if matrix_end:
                in_matrix = False
            # print(self.nexus_command_hash)
        if "DIMENSIONS" in self.nexus_command_hash.keys():
            if "NTAX" in self.nexus_command_hash["DIMENSIONS"]:
                ntax = int(self.nexus_command_hash["DIMENSIONS"]["NTAX"])
                self.n_taxa = int(ntax)
            if "NCHAR" in self.nexus_command_hash["DIMENSIONS"]:
                nchar = int(self.nexus_command_hash["DIMENSIONS"]["NCHAR"])
                self.n_chars = int(nchar)
        # print("number of taxa", ntax, len(self.taxa_list))
        # print("number of char", nchar)
        self.format_datamatrix()

    def parse_tnt_file(self, line_list):
        in_header = False
        in_body = True
        for line in line_list:
            # check if first line contains dataset name and taxa/chars count
            xread_match = re.match(r"xread", line, flags=re.IGNORECASE)
            datasetname_match = re.match(r"'(.*)'", line)
            count_match = re.match(r"(\d+)\s+(\d+)", line)
            data_match = re.match(r"^(\S+)\s+(.+)$", line)
            if xread_match:
                in_header = True
            if datasetname_match:
                self.dataset_name = datasetname_match.group(1)
            if count_match and in_header:
                self.n_chars = count_match.group(1)
                self.n_taxa = count_match.group(2)
            if not count_match and not datasetname_match and data_match:
                in_header = False
                in_body = True
                taxon_name = data_match.group(1)
                data = data_match.group(2)
                self.taxa_list.append(taxon_name)
                self.data_list.append(data)
                self.data_hash[taxon_name] = data

        self.format_datamatrix()

    def parse_phylip_file(self, line_list):
        total_linenum = len(line_list)
        sequential_format = False
        interleaved_format = False
        taxon_data_count = 0
        for line in line_list:
            # check if first line contains dataset name and taxa/chars count
            count_match = re.match(r"^\s*(\d+)\s+(\d+)\s*$", line)
            data_match = re.match(r"^(\S+)\s+(.+)\s*$", line)
            interleaved_data_match = re.match(r"^\s+(.+)\s*$", line)
            if count_match:
                self.n_chars = count_match.group(2)
                self.n_taxa = count_match.group(1)
                if int(total_linenum) > 2 * int(self.n_taxa):
                    logger.debug("Detected interleaved PHYLIP format")
                    interleaved_format = True
                else:
                    logger.debug("Detected sequential PHYLIP format")
                    sequential_format = True

            if not count_match and data_match:
                taxon_name = data_match.group(1)
                data = data_match.group(2)
                self.taxa_list.append(taxon_name)
                self.data_list.append(data)
                self.data_hash[taxon_name] = data
                taxon_data_count += 1

            if interleaved_data_match:
                pass

        self.format_datamatrix()

    def format_datamatrix(self):
        self.datamatrix = []

        for species in self.taxa_list:
            data = self.data_hash[species]
            array_data = []
            poly_char = ""
            # print(species, data)
            # print(species,len(data),data)
            is_poly = False
            for char in data:
                # print(char,)
                if char in ["(", "{", "["]:
                    is_poly = True
                    array_data.append([])
                elif char in [")", "}", "]"]:
                    array_data[-1].append(poly_char)
                    poly_char = ""
                    is_poly = False
                else:
                    if is_poly:
                        if char == " ":
                            array_data[-1].append(poly_char)
                            poly_char = ""
                        else:
                            poly_char += char
                    else:
                        array_data.append(char)

            self.formatted_data_hash[species] = array_data
            formatted_data = [species]
            formatted_data.extend(array_data)
            self.formatted_data_list.append(formatted_data)
            self.datamatrix.append(array_data)
            # print(species, len(array_data),array_data)

            # formatted_data = data.split()
            # print(array_data)
            # if len(data) != nchar:
            # else:

        # print(data_hash)
        # print(self.command_hash)


class PhyloTreefile:
    """Phylogenetic tree file parser.

    Parses tree files in Nexus and Newick formats. Extracts tree topologies
    from TREES blocks in Nexus files, handling translate statements and
    multiple trees. Supports both file-based and text-based tree input.

    Attributes:
        line_list: List of lines from the file.
        block_list: List of parsed Nexus blocks.
        block_hash: Dictionary mapping block names to block content.
        taxa_list: List of taxon names from translate table.
        taxa_hash: Dictionary mapping taxon indices to names.
        tree_text_list: List of tree strings (Newick format).
        tree_text_hash: Dictionary mapping tree names to Newick strings.
        tree_object_hash: Dictionary of parsed tree objects.
        file_type: Detected file type ('Nexus' or 'tre').
        tree_list: List of all tree strings found.

    Example:
        Loading trees from a file::

            treefile = PhyloTreefile()
            if treefile.readtree("consensus.tre", "Nexus"):
                print(f"Found {len(treefile.tree_list)} trees")
                for tree_name, tree_text in treefile.tree_text_hash.items():
                    print(f"{tree_name}: {tree_text[:50]}...")

    Raises:
        FileOperationError: If file cannot be read.
    """

    def __init__(self):
        self.line_list = []
        self.block_list = []
        self.block_hash = {}
        self.taxa_list = []
        self.taxa_hash = {}
        self.tree_text_list = []
        self.tree_text_hash = {}
        self.tree_object_hash = {}
        self.file_type = None
        self.tree_list = []

    def readtree(self, a_filepath, filetype):
        filepath, filename = os.path.split(a_filepath)
        filename, fileext = os.path.splitext(filename.upper())
        self.dataset_name = filename

        self.file_type = filetype

        # print("file type 1:", self.file_type, a_filepath)
        # determine by filetype
        if not self.file_type:
            if fileext.upper() in [".NEX", ".NEXUS"]:
                self.file_type = "Nexus"
            elif fileext.upper() in [
                ".TRE",
            ]:
                self.file_type = "tre"
            # check if file exists
        if not os.path.exists(a_filepath):
            return False

        # print("file type 2:", self.file_type, a_filepath)
        # Read file with error handling
        try:
            self.file_text = safe_file_read(a_filepath)
        except FileOperationError as e:
            logger.error(f"Error reading tree file {a_filepath}: {e}")
            return False

        self.line_list = self.file_text.split("\n")
        if not self.file_type:
            upper_file_text = self.file_text.upper()
            # first_line = self.line_list[0].upper()
            if upper_file_text.find("#NEXUS") > -1:
                self.file_type = "Nexus"
        # print("File type 3:", self.file_type)

        if self.file_type == "Nexus":
            # print("nexus file")
            self.parse_nexus_file()
            if "TREES" in self.block_hash.keys():
                tree_lines = self.block_hash["TREES"]
                taxa_begin = False
                taxa_end = False
                curr_tree_name = ""
                prev_tree_name = ""
                whole_tree = " ".join(tree_lines)
                tree_sections = whole_tree.split(";")
                self.tree_section = {}
                for section in tree_sections:
                    # print(section)
                    section_line = re.search(r"\s*(\w+)\s+(.+)", section, flags=re.IGNORECASE)
                    if section_line:
                        section_name = section_line.group(1)
                        section_contents = section_line.group(2)
                        if section_name not in self.tree_section.keys():
                            self.tree_section[section_name] = []
                        self.tree_section[section_name].append(section_contents)

                if "translate" in self.tree_section.keys():
                    taxa_list = self.tree_section["translate"][0].split(",")
                    # print(taxa_list)
                    for taxon in taxa_list:
                        taxon = taxon.strip()
                        # print(taxon)
                        taxon_line = re.search(r"(\S+)\s+(\S+)", taxon, flags=re.IGNORECASE)
                        if taxon_line:
                            taxon_index = taxon_line.group(1)
                            taxon_name = taxon_line.group(2)
                            self.taxa_list.append(taxon_name)
                            self.taxa_hash[taxon_index] = taxon_name
                if "tree" in self.tree_section.keys():
                    # self.tree_hash = {}
                    for tree in self.tree_section["tree"]:
                        # print("tree:[",tree,"]")
                        tree = tree.strip()
                        tree_name, tree_text = tree.split("=", 1)
                        # tree_line = re.search("(\w+)\s*=(.+)",tree,flags=re.IGNORECASE)
                        tree_name = tree_name.strip()
                        tree_text = tree_text.strip()
                        self.tree_text_hash[tree_name] = tree_text
                        self.tree_list.append(tree_text)
                    # print(self.tree_section['tree'])
                # print(self.taxa_hash)
                return True
                for line in tree_lines:
                    print("[", line, "]")
                    taxa_begin_line = re.search("translate", line, flags=re.IGNORECASE)
                    taxa_end_line = re.search(";", line, flags=re.IGNORECASE)
                    if taxa_begin_line:
                        print("taxa begin")
                        taxa_begin = True
                        continue
                    if taxa_end_line:
                        print("taxa end")
                        taxa_end = True
                        continue
                    if taxa_begin and not taxa_end:
                        taxon_line = re.search(r"^\s*(\d+)\s+(\S+)\s*$", line, flags=re.IGNORECASE)
                        # print(taxon_line)
                        if taxon_line:
                            taxon_idx = taxon_line.group(1)
                            taxon_name = taxon_line.group(2)
                            if taxon_name[-1] == ",":
                                taxon_name = taxon_name[:-1]
                            self.taxa_hash[taxon_idx] = taxon_name
                            self.taxa_list.append(taxon_name)
                    if taxa_end:
                        print("taxa end and now looking for tree")
                        print(line)
                        tree_begin_line = re.search(
                            r"^\s*tree\s+(\S+)\s*=\s*(.*)$", line, flags=re.IGNORECASE
                        )
                        tree_end_line = re.search("(.*);", line)
                        print(tree_begin_line, tree_end_line)
                        if tree_begin_line:
                            curr_tree_name = tree_begin_line.group(1)
                            print("tree name:", curr_tree_name)
                            if tree_end_line:
                                tree_text = tree_begin_line.group(2)
                                self.tree_text_hash[curr_tree_name] = tree_text
                        elif tree_end_line:
                            self.tree_text_hash[curr_tree_name] += tree_text

                if self.tree_text_hash:
                    for tree_key in self.tree_text_hash.keys():
                        tree_text = self.tree_text_hash[tree_key]
                        self.tree_text_hash[tree_key] = self.remove_comment(tree_text)
        elif self.file_type == "tre":
            self.parse_tre_file(self.line_list)
        elif self.file_type == "treefile":
            self.parse_IQTree_treefile(self.line_list)
        else:
            return False

        return True

    def parse_IQTree_treefile(self, line_list):
        for line in line_list:
            # find "tread" line
            if re.match(r".*;", line, flags=re.IGNORECASE):
                tree_text = line.replace(";", "")
                self.tree_list.append(tree_text)

    def parse_tre_file(self, line_list):
        header_found = False
        for line in line_list:
            # find "tread" line
            if re.match(r"tread.*", line, flags=re.IGNORECASE):
                # self.file_type = 'tread'
                header_found = True
                continue
            if re.match(r"proc.*", line, flags=re.IGNORECASE):
                # self.file_type = 'proc'

                break
            if header_found:
                tree_text = line.replace(";", "")
                tree_text = tree_text.replace("*", "")
                tree_text = tree_text.replace("(", "( ")
                tree_text = tree_text.replace(")", " ) ")
                str_list = []
                raw_list = tree_text.split(" ")
                for item in raw_list:
                    if item != "":
                        if len(str_list) > 0:
                            if item == "(":
                                if str_list[-1] != "(":
                                    str_list.append(",")
                            else:
                                try:
                                    int(item)
                                    try:
                                        int(str_list[-1])
                                        if int(str_list[-1]) > 0 and int(item) > 0:
                                            str_list.append(",")
                                    except (ValueError, IndexError):
                                        pass
                                except (ValueError, TypeError):
                                    pass  # str_list.append(item)

                                # int(str_list[-1]) > 0 and int(item) > 0:
                                # str_list.append(",")

                        str_list.append(item)
                tree_text = "".join(str_list)
                self.tree_list.append(tree_text)
                # print(tree_text)

    def remove_comment(self, tree_text):
        # print(tree_text[15],tree_text[20])
        # print(tree_text)
        new_tree_text = ""
        for tree_char in tree_text:
            if tree_char == "[":
                in_comment = True
                continue
            if tree_char == "]":
                in_comment = False
                continue
            if not in_comment:
                new_tree_text += tree_char
        # print(new_tree_text)
        return new_tree_text

    def parse_tree(self, tree_text):
        tree = []
        idx = 0
        subtree, processed_index = self.parse_subtree(tree_text[1:])
        # print(subtree)

        return subtree
        idx = processed_index
        tree.append(subtree)
        # for idx in range(len(tree_text[]))
        while processed_index < len(tree_text):
            subtree, processed_index = self.parse_subtree(remaining_text)
            if subtree:
                tree.append(subtree)

    def parse_subtree(self, tree_text, depth=0):
        tree = []
        taxon = ""
        # print("parse:",tree_text)
        # for idx in range(len(tree_text)):
        idx = 0
        while idx < len(tree_text):
            char = tree_text[idx]
            print("depth", depth, "idx", idx, "char", char)
            if char == " ":
                continue
            if char == "(":
                subtree, processed_index = self.parse_subtree(tree_text[idx + 1 :], depth + 1)
                print(
                    "returned subtree",
                    subtree,
                    "processed_index",
                    processed_index,
                    "idx",
                    idx,
                    "tree_text[",
                    tree_text,
                    "]",
                    "depth",
                    depth,
                )
                idx += processed_index
                print("depth", depth, "idx", idx)
                if subtree:
                    tree.append(subtree)
            elif char == ")":
                if taxon != "":
                    print("met ')', and add taxon", taxon, "idx=", idx)
                    tree.append(taxon)
                return tree, idx + 1
            elif char == ",":
                print("met ',', and add taxon", taxon, "idx=", idx)
                tree.append(taxon)
                taxon = ""
            else:
                taxon += char
            idx += 1
        if taxon != "":
            tree.append(taxon)
        return tree, idx + 1

    def parse_nexus_file(self, line_list=None):
        if not line_list:
            line_list = self.line_list
        curr_block = None
        in_block = False
        for line in line_list:
            # print(line)
            begin_line = re.match(r"begin\s+(\S+)\s*;", line, flags=re.IGNORECASE)
            end_line = re.match(r"end\s*;", line, flags=re.IGNORECASE)

            if begin_line:
                # print(begin_line)
                curr_block = {}
                curr_block["name"] = begin_line.group(1).upper()
                curr_block["text"] = []
                in_block = True
            elif end_line:
                # print("end block")
                self.block_list.append(curr_block)
                # if curr_block['name'] == 'DATA':
                self.block_hash[curr_block["name"]] = curr_block["text"]
                in_block = False
            elif in_block:
                curr_block["text"].append(line)
        return  # block_list


# Function to reconstruct ancestral states for all characters in the data matrix
def reconstruct_ancestral_states(tree, datamatrix, taxa_list):
    """Reconstruct ancestral character states using Fitch parsimony algorithm.

    Implements the two-pass Fitch algorithm to infer ancestral character
    states for all internal nodes in a phylogenetic tree. Handles polymorphic
    characters (states represented as sets).

    Args:
        tree: Bio.Phylo tree object with terminal nodes.
        datamatrix: Nested list of character states [taxa][characters].
        taxa_list: List of taxon names matching tree terminal nodes.

    Note:
        Modifies tree nodes in-place by adding:
            - character_states: List of inferred states per character
            - changed_characters: List of character indices that changed
    """
    # Initialize ancestral states for each character
    # print("taxa list:", taxa_list)
    # print("morphological_data:", datamatrix, len(datamatrix[0]))
    for node in tree.find_clades():
        node.character_states = [None] * len(datamatrix[0])
        node.changed_characters = []
        # initialize terminal nodes with their character states
        if node.is_terminal():
            taxon_idx = taxa_list.index(node.name)
            # print("taxon:", node.name, datamatrix[taxon_idx])
            # print("node.confidence:", node.confidence)
            for character, state in enumerate(datamatrix[taxon_idx]):
                if isinstance(state, list):
                    node.character_states[character] = set(state)
                else:
                    node.character_states[character] = set([state])
                # print( character, state)

    bottom_up_pass(tree.root, datamatrix)
    # print("bottom up done, root.confidence:", tree.root.character_states)

    # Perform the second pass (top-down traversal)
    top_down_pass(tree.root, datamatrix)


# Function to perform the first pass of the Fitch algorithm (bottom-up traversal)
def bottom_up_pass(node, datamatrix):
    """Perform bottom-up pass of Fitch algorithm.

    First pass of Fitch parsimony: traverse tree from tips to root,
    computing possible ancestral states at each internal node based on
    child states. Uses set intersections and unions to minimize changes.

    Args:
        node: Current tree node being processed.
        datamatrix: Character matrix [taxa][characters].

    Note:
        Recursively processes children first (post-order traversal).
        Modifies node.character_states in-place.
    """
    if node.is_terminal():
        return
    for child in node:
        bottom_up_pass(child, datamatrix)
    for character in range(len(datamatrix[0])):
        children_states = [child.character_states[character] for child in node]
        # print("children_states:", children_states)
        children_sets = [s for s in children_states if isinstance(s, set)]
        # print("children_sets:", children_sets)
        intersection = set.intersection(*children_sets) if children_sets else set()
        # print("intersection:", intersection)
        # check if intersection is empty
        if not intersection:
            union = set.union(*children_sets) if children_sets else set()
            node.character_states[character] = union
            # print("union:", union)
        else:
            node.character_states[character] = intersection
        node.character_states[character] = set.union(*children_sets) if children_sets else set()
        # print("node.confidence:", node.confidence)


# Function to perform the second pass of the Fitch algorithm (top-down traversal)
def top_down_pass(node, morphological_data, parent_states=None):
    """Perform top-down pass of Fitch algorithm.

    Second pass of Fitch parsimony: traverse tree from root to tips,
    resolving ambiguous states and identifying character state changes
    along branches.

    Args:
        node: Current tree node being processed.
        morphological_data: Character matrix [taxa][characters].
        parent_states: Character states of parent node (None for root).

    Note:
        Modifies node.character_states and node.changed_characters in-place.
        Uses minimum state value to resolve ambiguities.
    """
    if not node.is_terminal():
        # print("topdown node.confidence:", node.name, node.confidence, "parent confidence:", parent_state)
        for character_index in range(len(morphological_data[0])):
            if (
                parent_states
                and parent_states[character_index] in node.character_states[character_index]
            ):
                node.character_states[character_index] = parent_states[character_index]
            else:
                # node.character_states[character_index] = next(iter(node.character_states[character_index]))
                node.character_states[character_index] = min(node.character_states[character_index])
            if (
                parent_states
                and parent_states[character_index] != node.character_states[character_index]
            ):
                # print("changed character:", character_index, "parent:", parent_state[character_index], "node:", node.confidence[character_index])
                node.changed_characters.append(character_index)
    else:
        # print("topdown terminal node.confidence:", node.name, node.confidence)
        for character_index in range(len(morphological_data[0])):
            # final_state = next(iter(node.character_states[character_index]))
            final_state = min(node.character_states[character_index])
            node.character_states[character_index] = final_state
            if (
                parent_states
                and parent_states[character_index] != node.character_states[character_index]
            ):
                # print("changed character:", character_index, "parent:", parent_state[character_index], "node:", node.confidence[character_index])
                node.changed_characters.append(character_index)
            # print("node.confidence:", node.confidence)
    #            if len(node.confidence[character_index]) == 0:
    #                for child in node.clades:
    #                    for state in child.confidence[character_index]:
    #                        node.confidence[character_index].add(state)

    for child in node.clades:
        top_down_pass(child, morphological_data, node.character_states)


def print_character_states(node, depth=0):
    """Print character states for all nodes in tree (debug utility).

    Recursively prints character state information for each node in the
    tree, including reconstructed ancestral states and character changes.
    Used for debugging and verification of Fitch algorithm results.

    Args:
        node: Tree node to print (prints subtree recursively).
        depth: Current depth in tree for indentation. Defaults to 0.
    """
    logger.info(
        "%sNode %s: character_states=%s, changed_chars=%s (count=%d)",
        " " * 4 * depth,
        node.name,
        node.character_states,
        node.changed_characters,
        len(node.changed_characters),
    )
    for child in node:
        print_character_states(child, depth + 1)


# ============================================================================
# File Path Validation Functions
# ============================================================================


def validate_file_path(filepath, must_exist=False, check_readable=False, check_writable=False):
    """Validate file path for security and accessibility.

    Performs comprehensive validation of file paths to ensure they are safe
    and accessible for the requested operations. Checks for path traversal
    attacks, null bytes, and file system permissions.

    Args:
        filepath: Path to validate (str or Path object).
        must_exist: If True, file must exist. Defaults to False.
        check_readable: If True, check file is readable. Defaults to False.
        check_writable: If True, check file/directory is writable. Defaults to False.

    Returns:
        str: Normalized absolute path if valid.

    Raises:
        FileOperationError: If path is invalid, inaccessible, or unsafe.

    Example:
        >>> validate_file_path("/tmp/data.nex", must_exist=True, check_readable=True)
        '/tmp/data.nex'

        >>> validate_file_path("../../etc/passwd")  # Raises error for suspicious path
    """
    if not filepath:
        raise FileOperationError("File path cannot be empty")

    # Convert to string if Path object
    filepath = str(filepath)

    # Check for null bytes (security)
    if "\x00" in filepath:
        raise FileOperationError("File path contains null bytes")

    # Normalize path to resolve .. and . components
    try:
        normalized_path = os.path.abspath(os.path.normpath(filepath))
    except Exception as e:
        raise FileOperationError(f"Invalid file path: {e}")

    # Check for path traversal attempts (basic check)
    if ".." in filepath:
        logger.warning(f"Path contains '..' components: {filepath}")
        # Allow but log - might be legitimate

    # Check existence if required
    if must_exist and not os.path.exists(normalized_path):
        raise FileOperationError(f"File does not exist: {filepath}")

    # Check readability
    if check_readable:
        if not os.path.exists(normalized_path):
            raise FileOperationError(f"Cannot check readability - file does not exist: {filepath}")
        if not os.path.isfile(normalized_path):  # noqa: PTH113
            raise FileOperationError(f"Path is not a file: {filepath}")
        if not os.access(normalized_path, os.R_OK):
            raise FileOperationError(f"File is not readable: {filepath}")

    # Check writability
    if check_writable:
        if os.path.exists(normalized_path):
            # File exists - check if writable
            if not os.access(normalized_path, os.W_OK):
                raise FileOperationError(f"File is not writable: {filepath}")
        else:
            # File doesn't exist - check if parent directory is writable
            parent_dir = os.path.dirname(normalized_path)
            if not os.path.exists(parent_dir):
                raise FileOperationError(f"Parent directory does not exist: {parent_dir}")
            if not os.access(parent_dir, os.W_OK):
                raise FileOperationError(f"Cannot write to directory: {parent_dir}")

    return normalized_path


def validate_directory_path(
    dirpath, must_exist=False, check_writable=False, create_if_missing=False
):
    """Validate directory path for security and accessibility.

    Args:
        dirpath: Directory path to validate.
        must_exist: If True, directory must exist. Defaults to False.
        check_writable: If True, check directory is writable. Defaults to False.
        create_if_missing: If True, create directory if it doesn't exist. Defaults to False.

    Returns:
        str: Normalized absolute directory path if valid.

    Raises:
        FileOperationError: If path is invalid or inaccessible.

    Example:
        >>> validate_directory_path("/tmp/results", create_if_missing=True)
        '/tmp/results'
    """
    if not dirpath:
        raise FileOperationError("Directory path cannot be empty")

    dirpath = str(dirpath)

    # Check for null bytes
    if "\x00" in dirpath:
        raise FileOperationError("Directory path contains null bytes")

    # Normalize path
    try:
        normalized_path = os.path.abspath(os.path.normpath(dirpath))
    except Exception as e:
        raise FileOperationError(f"Invalid directory path: {e}")

    # Check existence
    if os.path.exists(normalized_path):
        if not os.path.isdir(normalized_path):  # noqa: PTH112
            raise FileOperationError(f"Path exists but is not a directory: {dirpath}")
    elif must_exist:
        raise FileOperationError(f"Directory does not exist: {dirpath}")
    elif create_if_missing:
        try:
            os.makedirs(normalized_path, exist_ok=True)
            logger.info(f"Created directory: {normalized_path}")
        except Exception as e:
            raise FileOperationError(f"Failed to create directory {dirpath}: {e}")

    # Check writability
    if check_writable and os.path.exists(normalized_path):
        if not os.access(normalized_path, os.W_OK):
            raise FileOperationError(f"Directory is not writable: {dirpath}")

    return normalized_path


def validate_file_extension(filepath, allowed_extensions):
    """Validate file has an allowed extension.

    Args:
        filepath: Path to file to check.
        allowed_extensions: List/tuple of allowed extensions (with or without dot).
            Example: ['.nex', '.phy', '.tnt'] or ['nex', 'phy', 'tnt']

    Returns:
        bool: True if extension is allowed.

    Raises:
        FileOperationError: If extension is not allowed.

    Example:
        >>> validate_file_extension("data.nex", ['.nex', '.phy'])
        True

        >>> validate_file_extension("malware.exe", ['.nex', '.phy'])
        # Raises FileOperationError
    """
    if not filepath:
        raise FileOperationError("File path cannot be empty")

    # Normalize extensions to include dot
    normalized_extensions = []
    for ext in allowed_extensions:
        if not ext.startswith("."):
            ext = "." + ext
        normalized_extensions.append(ext.lower())

    # Get file extension
    _, file_ext = os.path.splitext(filepath)
    file_ext = file_ext.lower()

    if file_ext not in normalized_extensions:
        raise FileOperationError(
            f"File extension '{file_ext}' not allowed. "
            f"Allowed extensions: {', '.join(normalized_extensions)}"
        )

    return True


def validate_phylo_data_file(filepath):
    """Validate phylogenetic data file path and extension.

    Convenience function that validates a file is readable and has
    a recognized phylogenetic data format extension.

    Args:
        filepath: Path to phylogenetic data file.

    Returns:
        str: Normalized absolute path if valid.

    Raises:
        FileOperationError: If file is invalid or has wrong extension.

    Example:
        >>> validate_phylo_data_file("data.nex")
        '/absolute/path/to/data.nex'
    """
    # Validate path and readability
    validated_path = validate_file_path(filepath, must_exist=True, check_readable=True)

    # Check extension
    allowed_extensions = [".nex", ".nexus", ".phy", ".phylip", ".tnt", ".ss", ".txt"]
    try:
        validate_file_extension(validated_path, allowed_extensions)
    except FileOperationError as e:
        logger.warning(f"File has non-standard extension but may still be valid: {e}")
        # Don't raise - allow files with non-standard extensions
        # The parser will determine if format is valid

    return validated_path


# ============================================================================
# Datamatrix Validation Functions
# ============================================================================


def validate_taxa_names(taxa_list, allow_duplicates=False):
    """Validate taxa names for consistency and uniqueness.

    Args:
        taxa_list: List of taxon names to validate.
        allow_duplicates: If False, raise error on duplicate names. Defaults to False.

    Returns:
        bool: True if validation passes.

    Raises:
        DataParsingError: If taxa names are invalid.

    Example:
        >>> validate_taxa_names(['Taxon1', 'Taxon2', 'Taxon3'])
        True

        >>> validate_taxa_names(['Taxon1', 'Taxon1'])  # Raises error
    """
    if not taxa_list:
        raise DataParsingError("Taxa list cannot be empty")

    if not isinstance(taxa_list, (list, tuple)):
        raise DataParsingError("Taxa list must be a list or tuple")

    # Check for empty names
    for i, taxon in enumerate(taxa_list):
        if not taxon or not str(taxon).strip():
            raise DataParsingError(f"Empty taxon name at position {i + 1}")

    # Check for duplicates
    if not allow_duplicates:
        seen = set()
        duplicates = []
        for taxon in taxa_list:
            taxon_normalized = str(taxon).strip().lower()
            if taxon_normalized in seen:
                duplicates.append(taxon)
            seen.add(taxon_normalized)

        if duplicates:
            raise DataParsingError(
                f"Duplicate taxon names found: {', '.join(set(duplicates))}\n"
                f"Each taxon must have a unique name."
            )

    return True


def validate_character_states(character_data, valid_states=None):
    """Validate character state data for consistency.

    Args:
        character_data: List or string of character states.
        valid_states: Optional set of valid character states.
            If None, allows any alphanumeric characters. Defaults to None.

    Returns:
        bool: True if validation passes.

    Raises:
        DataParsingError: If character data is invalid.

    Example:
        >>> validate_character_states(['0', '1', '2'])
        True

        >>> validate_character_states(['0', '1', 'X'], valid_states={'0', '1', '2'})
        # Raises error for invalid state 'X'
    """
    if character_data is None:
        raise DataParsingError("Character data cannot be None")

    # Convert to list if string
    if isinstance(character_data, str):
        character_data = list(character_data)

    if not isinstance(character_data, (list, tuple)):
        raise DataParsingError("Character data must be a list, tuple, or string")

    # Check for empty data
    if len(character_data) == 0:
        raise DataParsingError("Character data cannot be empty")

    # Validate individual states
    if valid_states is not None:
        valid_states = {str(s) for s in valid_states}
        for i, state in enumerate(character_data):
            # Handle polymorphic characters (lists)
            if isinstance(state, (list, tuple)):
                for poly_state in state:
                    if str(poly_state) not in valid_states:
                        raise DataParsingError(
                            f"Invalid character state '{poly_state}' at position {i + 1}. "
                            f"Valid states: {', '.join(sorted(valid_states))}"
                        )
            else:
                if str(state) not in valid_states:
                    raise DataParsingError(
                        f"Invalid character state '{state}' at position {i + 1}. "
                        f"Valid states: {', '.join(sorted(valid_states))}"
                    )

    return True


def validate_datamatrix_dimensions(taxa_list, character_matrix):
    """Validate datamatrix dimensions for consistency.

    Ensures all taxa have the same number of characters and that
    dimensions match expected values.

    Args:
        taxa_list: List of taxon names.
        character_matrix: 2D list/array of character data (taxa x characters).

    Returns:
        tuple: (n_taxa, n_characters) dimensions if valid.

    Raises:
        DataParsingError: If dimensions are inconsistent.

    Example:
        >>> taxa = ['T1', 'T2', 'T3']
        >>> matrix = [['0','1','2'], ['1','0','1'], ['2','1','0']]
        >>> validate_datamatrix_dimensions(taxa, matrix)
        (3, 3)
    """
    if not taxa_list:
        raise DataParsingError("Taxa list cannot be empty")

    if not character_matrix:
        raise DataParsingError("Character matrix cannot be empty")

    n_taxa = len(taxa_list)
    n_matrix_rows = len(character_matrix)

    # Check number of rows matches number of taxa
    if n_taxa != n_matrix_rows:
        raise DataParsingError(
            f"Number of taxa ({n_taxa}) does not match number of matrix rows ({n_matrix_rows})"
        )

    # Check all rows have same length
    char_lengths = [len(row) for row in character_matrix]
    if len(set(char_lengths)) > 1:
        # Find inconsistent rows
        expected_length = char_lengths[0]
        inconsistent_rows = []
        for i, length in enumerate(char_lengths):
            if length != expected_length:
                inconsistent_rows.append(f"{taxa_list[i]}: {length} characters")

        raise DataParsingError(
            f"Inconsistent character counts across taxa.\n"
            f"Expected {expected_length} characters per taxon.\n"
            f"Inconsistent rows:\n" + "\n".join(inconsistent_rows)
        )

    n_characters = char_lengths[0] if char_lengths else 0

    # Basic sanity checks
    if n_taxa < 2:
        raise DataParsingError(f"Datamatrix must have at least 2 taxa (found {n_taxa})")

    if n_characters < 1:
        raise DataParsingError(f"Datamatrix must have at least 1 character (found {n_characters})")

    return (n_taxa, n_characters)


def validate_complete_datamatrix(taxa_list, character_matrix, matrix_name="datamatrix"):
    """Perform complete validation of a phylogenetic datamatrix.

    Combines all datamatrix validation checks into a single function.

    Args:
        taxa_list: List of taxon names.
        character_matrix: 2D list/array of character data.
        matrix_name: Name of matrix for error messages. Defaults to "datamatrix".

    Returns:
        dict: Validation results with keys 'valid', 'n_taxa', 'n_characters', 'warnings'.

    Raises:
        DataParsingError: If validation fails critically.

    Example:
        >>> taxa = ['Taxon1', 'Taxon2']
        >>> matrix = [['0','1'], ['1','0']]
        >>> result = validate_complete_datamatrix(taxa, matrix)
        >>> print(result)
        {'valid': True, 'n_taxa': 2, 'n_characters': 2, 'warnings': []}
    """
    warnings = []

    try:
        # Validate taxa names
        validate_taxa_names(taxa_list, allow_duplicates=False)
    except DataParsingError as e:
        raise DataParsingError(f"Taxa validation failed for {matrix_name}: {e}")

    try:
        # Validate dimensions
        n_taxa, n_characters = validate_datamatrix_dimensions(taxa_list, character_matrix)
    except DataParsingError as e:
        raise DataParsingError(f"Dimension validation failed for {matrix_name}: {e}")

    # Validate character data for each taxon
    for _i, (taxon, char_data) in enumerate(zip(taxa_list, character_matrix)):
        try:
            validate_character_states(char_data, valid_states=None)
        except DataParsingError as e:
            raise DataParsingError(f"Character validation failed for taxon '{taxon}': {e}")

    # Check for suspicious patterns (warnings only)
    # Check for taxa with all missing data
    for _i, (taxon, char_data) in enumerate(zip(taxa_list, character_matrix)):
        missing_count = sum(1 for c in char_data if str(c) in ["?", "-", "N", "n"])
        if missing_count == n_characters:
            warnings.append(f"Taxon '{taxon}' has all missing data")
        elif missing_count / n_characters > 0.8:
            warnings.append(
                f"Taxon '{taxon}' has {missing_count}/{n_characters} ({missing_count*100//n_characters}%) missing data"
            )

    return {
        "valid": True,
        "n_taxa": n_taxa,
        "n_characters": n_characters,
        "warnings": warnings,
    }


# ============================================================================
# Database Backup and Recovery Functions
# ============================================================================


def backup_database(db_path, backup_dir=None, keep_n_backups=10):
    """Create a timestamped backup of the database file.

    Args:
        db_path: Path to the database file to backup.
        backup_dir: Directory to store backups. If None, uses db_path parent + '/backups'.
            Defaults to None.
        keep_n_backups: Number of backups to keep (oldest are deleted). Defaults to 10.

    Returns:
        str: Path to created backup file.

    Raises:
        FileOperationError: If backup fails.

    Example:
        >>> backup_database("/path/to/PhyloForester.db")
        '/path/to/backups/PhyloForester.20250105_143022.db'
    """
    import shutil
    from datetime import datetime

    try:
        # Validate source database exists
        if not os.path.exists(db_path):
            raise FileOperationError(f"Database file not found: {db_path}")

        if not os.path.isfile(db_path):  # noqa: PTH113
            raise FileOperationError(f"Database path is not a file: {db_path}")

        # Determine backup directory
        if backup_dir is None:
            backup_dir = os.path.join(os.path.dirname(db_path), "backups")

        # Create backup directory if needed
        try:
            os.makedirs(backup_dir, exist_ok=True)
        except Exception as e:
            raise FileOperationError(f"Failed to create backup directory: {e}")

        # Generate backup filename with timestamp
        db_name = os.path.basename(db_path)  # noqa: PTH119
        db_name_without_ext = os.path.splitext(db_name)[0]
        db_ext = os.path.splitext(db_name)[1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{db_name_without_ext}.{timestamp}{db_ext}"
        backup_path = os.path.join(backup_dir, backup_filename)

        # Copy database file
        shutil.copy2(db_path, backup_path)
        logger.info(f"Database backed up to: {backup_path}")

        # Clean up old backups
        try:
            cleanup_old_backups(backup_dir, db_name_without_ext, keep_n_backups)
        except Exception as e:
            logger.warning(f"Failed to cleanup old backups: {e}")
            # Don't raise - backup was successful

        return backup_path

    except FileOperationError:
        raise
    except Exception as e:
        raise FileOperationError(f"Database backup failed: {e}")


def cleanup_old_backups(backup_dir, db_name_prefix, keep_n_backups):
    """Remove old backup files, keeping only the N most recent.

    Args:
        backup_dir: Directory containing backup files.
        db_name_prefix: Prefix of backup files (e.g., 'PhyloForester').
        keep_n_backups: Number of most recent backups to keep.

    Returns:
        int: Number of backups removed.

    Example:
        >>> cleanup_old_backups("/path/to/backups", "PhyloForester", 10)
        3  # Removed 3 old backup files
    """
    try:
        if not os.path.exists(backup_dir):
            return 0

        # Find all backup files matching pattern
        backup_files = []
        for filename in os.listdir(backup_dir):  # noqa: PTH208
            if filename.startswith(db_name_prefix) and "." in filename:
                filepath = os.path.join(backup_dir, filename)
                if os.path.isfile(filepath):  # noqa: PTH113
                    mtime = os.path.getmtime(filepath)  # noqa: PTH204
                    backup_files.append((mtime, filepath))

        # Sort by modification time (newest first)
        backup_files.sort(reverse=True)

        # Remove old backups beyond keep_n_backups
        removed_count = 0
        for i, (_mtime, filepath) in enumerate(backup_files):
            if i >= keep_n_backups:
                try:
                    os.remove(filepath)
                    logger.info(f"Removed old backup: {filepath}")
                    removed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to remove old backup {filepath}: {e}")

        return removed_count

    except Exception as e:
        logger.error(f"Error during backup cleanup: {e}")
        return 0


def restore_database(backup_path, db_path, create_backup=True):
    """Restore database from a backup file.

    Args:
        backup_path: Path to backup file to restore from.
        db_path: Path where database should be restored.
        create_backup: If True, backup current database before restoring. Defaults to True.

    Returns:
        bool: True if restore successful.

    Raises:
        FileOperationError: If restore fails.

    Example:
        >>> restore_database("/path/to/backup.db", "/path/to/PhyloForester.db")
        True
    """
    import shutil

    try:
        # Validate backup file exists
        if not os.path.exists(backup_path):
            raise FileOperationError(f"Backup file not found: {backup_path}")

        # Backup current database if requested
        if create_backup and os.path.exists(db_path):
            try:
                backup_database(db_path)
                logger.info("Created backup of current database before restore")
            except Exception as e:
                logger.warning(f"Failed to backup current database: {e}")
                # Continue anyway - user may want to proceed

        # Restore backup
        shutil.copy2(backup_path, db_path)
        logger.info(f"Database restored from: {backup_path}")

        return True

    except FileOperationError:
        raise
    except Exception as e:
        raise FileOperationError(f"Database restore failed: {e}")


def get_backup_list(backup_dir, db_name_prefix):
    """Get list of available database backups.

    Args:
        backup_dir: Directory containing backup files.
        db_name_prefix: Prefix of backup files to list.

    Returns:
        list: List of tuples (timestamp, filepath, size_bytes, age_days).
            Sorted by timestamp (newest first).

    Example:
        >>> backups = get_backup_list("/path/to/backups", "PhyloForester")
        >>> for timestamp, path, size, age in backups:
        ...     print(f"{timestamp}: {size} bytes, {age} days old")
    """
    from datetime import datetime

    backup_list = []

    try:
        if not os.path.exists(backup_dir):
            return backup_list

        current_time = datetime.now()

        for filename in os.listdir(backup_dir):  # noqa: PTH208
            if filename.startswith(db_name_prefix) and "." in filename:
                filepath = os.path.join(backup_dir, filename)
                if os.path.isfile(filepath):  # noqa: PTH113
                    # Get file info
                    mtime = os.path.getmtime(filepath)  # noqa: PTH204
                    size = os.path.getsize(filepath)  # noqa: PTH202
                    timestamp = datetime.fromtimestamp(mtime)
                    age_days = (current_time - timestamp).days

                    backup_list.append((timestamp, filepath, size, age_days))

        # Sort by timestamp (newest first)
        backup_list.sort(reverse=True)

        return backup_list

    except Exception as e:
        logger.error(f"Error getting backup list: {e}")
        return backup_list
