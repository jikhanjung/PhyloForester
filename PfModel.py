"""PhyloForester Data Models.

This module defines the Peewee ORM models for the PhyloForester application
database. It provides database schema definitions and data access methods for
phylogenetic analysis projects, datamatrices, analyses, and resulting trees.

The module uses Peewee ORM with SQLite backend, storing all application data
in a single database file. All models use CASCADE delete to maintain referential
integrity across the hierarchy: Project → Datamatrix → Analysis → Tree.

Database Location:
    Default: ~/PaleoBytes/PhyloForester/PhyloForester.db
    Can be customized via setup_database_location()

Main Models:
    PfProject: Top-level project container
    PfDatamatrix: Character matrix data storage
    PfPackage: External analysis software metadata
    PfAnalysis: Analysis configuration and execution tracking
    PfTree: Phylogenetic tree storage and visualization options

Example:
    Creating a new project with datamatrix::

        project = PfProject.create(
            project_name="Cambrian Fauna",
            project_desc="Analysis of early Cambrian organisms"
        )

        datamatrix = PfDatamatrix.create(
            project=project,
            datamatrix_name="Cloudina data",
            n_taxa=20,
            n_chars=45
        )
"""

from __future__ import annotations

import datetime
import json
import logging
import os

# from MdUtils import *
from collections import Counter

from Bio import Phylo
from peewee import *

import PfUtils as pu

# Initialize logger
logger: logging.Logger = logging.getLogger(__name__)

ANALYSIS_TYPE_ML: str = "Maximum Likelihood"
ANALYSIS_TYPE_PARSIMONY: str = "Parsimony"
ANALYSIS_TYPE_BAYESIAN: str = "Bayesian"

ANALYSIS_STATUS_READY: str = "Ready"
ANALYSIS_STATUS_RUNNING: str = "Running"
ANALYSIS_STATUS_FINISHED: str = "Completed"
ANALYSIS_STATUS_STOPPED: str = "Stopped"
ANALYSIS_STATUS_FAILED: str = "Failed"

DATATYPE_DNA: str = "DNA"
DATATYPE_RNA: str = "RNA"
DATATYPE_PROTEIN: str = "Protein"
DATATYPE_STANDARD: str = "Standard"
DATATYPE_MORPHOLOGY: str = "Morphology"
DATATYPE_COMBINED: str = "Combined"

BOOTSTRAP_TYPE_NORMAL: str = "Normal"
BOOTSTRAP_TYPE_ULTRAFAST: str = "Ultrafast"

TREE_TYPE_CONSENSUS: str = "Consensus"
TREE_TYPE_BOOTSTRAP: str = "Bootstrap"
TREE_TYPE_POSTERIOR: str = "Posterior"
TREE_TYPE_MPT: str = "MPT"

LINE_SEPARATOR: str = "\n"

database_path: str = os.path.join(pu.DEFAULT_DB_DIRECTORY, "PhyloForester.db")

gDatabase: SqliteDatabase = SqliteDatabase(database_path, pragmas={"foreign_keys": 1})


def setup_database_location(database_dir: str) -> SqliteDatabase:
    """Set up database location.

    Args:
        database_dir: Directory path for database

    Returns:
        Database handle
    """
    database_handle: SqliteDatabase = SqliteDatabase(database_path, pragmas={"foreign_keys": 1})
    return database_handle


class PfProject(Model):
    """Project model representing a phylogenetic analysis project.

    Stores metadata about a project including name, description, and
    timestamps. Projects are the top-level organizational unit in the
    application and can contain multiple datamatrices.

    Attributes:
        project_name: Name of the project.
        project_desc: Optional detailed description of the project.
        created_at: Timestamp when the project was created.
        modified_at: Timestamp of last modification.

    Relations:
        datamatrices: One-to-many relationship to PfDatamatrix.
            Cascade deletes when project is deleted.

    Example:
        Creating a new project::

            project = PfProject.create(
                project_name="Cambrian Fauna",
                project_desc="Phylogenetic analysis of early Cambrian organisms"
            )
    """

    project_name = CharField()
    project_desc = CharField(null=True)
    # datatype = CharField(null=True)
    # taxa_str = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    modified_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = gDatabase

    def get_taxa_list(self) -> list[str]:
        """Get list of taxa names.

        Returns:
            List of taxon names
        """
        if self.taxa_str:  # type: ignore[attr-defined]
            return self.taxa_str.split(",")  # type: ignore[attr-defined]
        return []


class PfDatamatrix(Model):
    """Datamatrix model storing character matrix data.

    Represents a character matrix (alignment) containing taxa and their
    character states. Stores data as JSON for flexibility with polymorphic
    characters. Supports importing from various file formats (Nexus, Phylip,
    TNT) and exporting to standard phylogenetic formats.

    The datamatrix is the central data structure for phylogenetic analysis,
    containing the character observations for each taxon. Character states
    can be polymorphic (represented as lists) or simple values.

    Attributes:
        project: Foreign key to parent PfProject.
        datamatrix_name: Name of the datamatrix.
        datamatrix_desc: Optional description of the data.
        datamatrix_index: Order index within the project.
        datatype: Data type (DNA, RNA, Protein, Morphology, etc.).
        n_taxa: Number of taxa (rows).
        n_chars: Number of characters (columns).
        taxa_list_json: JSON string of taxon names.
        taxa_timetable_json: JSON string of temporal ranges for taxa.
        character_list_json: JSON string of character names.
        datamatrix_json: JSON string of the character matrix data.
        whole_text: Original file content as text.
        created_at: Timestamp when created.
        modified_at: Timestamp of last modification.

    Class Attributes:
        datamatrix: Temporary storage for matrix data during import.
        taxa_list: Temporary storage for taxon names during import.
        characters_list: Temporary storage for character names during import.
        DEFAULTS: Default values for gap, missing, and datatype symbols.
        nexus_command_hash: Temporary storage for Nexus format commands.

    Relations:
        analyses: One-to-many relationship to PfAnalysis.
            Cascade deletes when datamatrix is deleted.

    Example:
        Creating a datamatrix from a file::

            dm = PfDatamatrix.create(
                project=project,
                datamatrix_name="Cambrian taxa",
                n_taxa=0,
                n_chars=0
            )
            dm.import_file("data.nex")
            dm.save()

            # Access the data
            taxa = dm.get_taxa_list()
            matrix = dm.datamatrix_as_list()

    Note:
        Character states are stored as either strings or lists (for
        polymorphic characters). The JSON encoding handles both cases.
    """

    project = ForeignKeyField(PfProject, backref="datamatrices", on_delete="CASCADE")
    datamatrix_name = CharField()
    datamatrix_desc = CharField(null=True)
    datamatrix_index = IntegerField(default=1)
    datatype = CharField(default=DATATYPE_MORPHOLOGY)
    n_taxa = IntegerField()
    n_chars = IntegerField()
    taxa_list_json = CharField(null=True)
    taxa_timetable_json = CharField(null=True)
    character_list_json = CharField(null=True)
    datamatrix_json = CharField(null=True)
    whole_text = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    modified_at = DateTimeField(default=datetime.datetime.now)

    datamatrix = []
    taxa_list = []
    characters_list = []
    DEFAULTS = {"gap": "-", "missing": "?", "datatype": "standard"}
    nexus_command_hash = None

    class Meta:
        database = gDatabase

    def get_taxa_timetable(self):
        """Get temporal ranges for taxa.

        Parses the taxa timetable from JSON storage. If parsing fails or
        no timetable exists, returns a default timetable with zero ranges.

        Returns:
            List of [start, end] temporal range pairs for each taxon.
            Returns [[0, 0], ...] if no valid timetable exists.
        """
        timetable = []
        if self.taxa_timetable_json is not None:
            try:
                timetable = json.loads(self.taxa_timetable_json)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing taxa timetable JSON for {self.datamatrix_name}: {e}")
                timetable = [[0, 0]] * self.n_taxa
        else:
            timetable = [[0, 0]] * self.n_taxa
        return timetable

    def is_timetable_valid(self):
        """Check if the taxa timetable is valid and non-trivial.

        Validates that the timetable exists, has correct format (pairs of
        numbers), matches the number of taxa, and contains at least one
        non-zero temporal range.

        Returns:
            True if timetable is valid and contains non-zero ranges,
            False otherwise.
        """
        if self.taxa_timetable_json:
            timetable = json.loads(self.taxa_timetable_json)
            all_zero = True
            for row in timetable:
                # print("row:",row)
                if len(row) != 2:
                    # print("row length not matching")
                    return False
                # if not isinstance(row[0], float) and not isinstance(row[0], int) or not isinstance(row[1], float) and isinstance(row[1], int):
                #    return False
                if float(row[0]) != 0.0 or float(row[1]) != 0.0:
                    # print("row not all zero")
                    all_zero = False
            if all_zero:
                # print("all zero")
                return False
            if len(timetable) == self.n_taxa:
                return True
        return False

    def copy(self):
        """Create a copy of this datamatrix.

        Creates a new PfDatamatrix instance with all the same data,
        but as a separate database record. Useful for duplicating
        datamatrices within a project.

        Returns:
            New PfDatamatrix instance with copied data.
        """
        new_datamatrix = PfDatamatrix.create(
            project=self.project,
            datamatrix_name=self.datamatrix_name,
            datamatrix_desc=self.datamatrix_desc,
            datamatrix_index=self.datamatrix_index,
            datatype=self.datatype,
            n_taxa=self.n_taxa,
            n_chars=self.n_chars,
            taxa_list_json=self.taxa_list_json,
            character_list_json=self.character_list_json,
            datamatrix_json=self.datamatrix_json,
            whole_text=self.whole_text,
        )
        return new_datamatrix

    def get_character_list(self) -> list[str]:
        """Get list of character names.

        Returns:
            List of character names
        """
        self.character_list = []
        if self.character_list_json:
            try:
                self.character_list = json.loads(self.character_list_json)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing character list JSON for {self.datamatrix_name}: {e}")
                self.character_list = []

        if len(self.character_list) == 0:
            if self.n_chars is not None:
                self.character_list = [""] * self.n_chars

        return self.character_list

    def datamatrix_as_list(self) -> list[list[str]]:
        """Get datamatrix as list of lists.

        Returns:
            Datamatrix as nested list
        """
        if self.datamatrix_json:
            try:
                formatted_data_list: list[list[str]] = json.loads(self.datamatrix_json)
                return formatted_data_list
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing datamatrix JSON for {self.datamatrix_name}: {e}")
                return []
        else:
            return []

    def get_taxa_list(self) -> list[str]:
        """Get list of taxa names.

        Returns:
            List of taxon names
        """
        if self.taxa_list_json:
            try:
                return json.loads(self.taxa_list_json)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing taxa list JSON for {self.datamatrix_name}: {e}")
                return []
        else:
            return []

    def import_file(self, file_path):
        """Import phylogenetic data from a file.

        Loads and parses data from various phylogenetic file formats
        (Nexus, Phylip, TNT). Automatically detects data type (DNA, RNA,
        protein, morphology) by analyzing character composition.

        Args:
            file_path: Path to the data file to import.

        Returns:
            True if import succeeded, False if parsing failed.

        Raises:
            FileOperationError: If file cannot be read.
            DataParsingError: If file format is invalid or unsupported.
        """
        try:
            datafile_obj = pu.PhyloDatafile()
            ret = datafile_obj.loadfile(file_path)

            if not ret:
                raise pu.DataParsingError(f"Failed to parse file: {file_path}")
        except (pu.FileOperationError, pu.DataParsingError) as e:
            logger.error(f"Data matrix import failed for {file_path}: {e}")
            return False

        if ret:
            self.datamatrix_name = datafile_obj.dataset_name
            self.whole_text = datafile_obj.file_text

            self.n_taxa = int(datafile_obj.n_taxa)
            self.n_chars = int(datafile_obj.n_chars)
            self.taxa_list = datafile_obj.taxa_list
            self.datamatrix = datafile_obj.datamatrix
            self.block_hash = datafile_obj.block_hash
            self.whole_text = datafile_obj.file_text
            self.formatted_data_list = datafile_obj.formatted_data_list
            self.nexus_command_hash = datafile_obj.nexus_command_hash
            if len(self.taxa_list) > 0:
                self.taxa_list_json = json.dumps(self.taxa_list)
            if len(self.datamatrix) > 0:
                self.datamatrix_json = json.dumps(self.datamatrix, indent=4)

            type_count = {
                DATATYPE_DNA: 0,
                DATATYPE_RNA: 0,
                DATATYPE_PROTEIN: 0,
                DATATYPE_MORPHOLOGY: 0,
                DATATYPE_COMBINED: 0,
            }
            for char_idx in range(self.n_chars):
                char_str = ""
                for taxon_idx in range(self.n_taxa):
                    char = self.datamatrix[taxon_idx][char_idx]
                    if isinstance(char, list):
                        char_str += "".join(char)
                    else:
                        char_str += char

                count = {}
                count[DATATYPE_DNA] = self.count_dna(char_str)
                count[DATATYPE_RNA] = self.count_rna(char_str)
                count[DATATYPE_PROTEIN] = self.count_protein(char_str)
                count[DATATYPE_MORPHOLOGY] = self.count_morphology(char_str)
                max_datatype = max(count, key=count.get)
                max_value = count[max_datatype]
                type_count[max_datatype] += 1
                # print("char idx:",char_idx, "char_str", char_str,"max:",max_datatype,"max_value:",max_value)

            max_datatype = max(type_count, key=type_count.get)
            self.datatype = max_datatype
            # print("datatype:",self.datatype)
        else:
            return False

        return True

    def count_chars(self, char_str, char_list):
        """Count occurrences of specific characters in a string.

        Helper method used by data type detection to count how many
        characters from a given alphabet appear in a character column.

        Args:
            char_str: String containing character states to count.
            char_list: List of valid characters to count (case-insensitive).

        Returns:
            Total count of characters from char_list found in char_str.
        """
        chars = (char.lower() for char in char_str if char.upper() in char_list)
        count_result = Counter(chars)
        count = 0
        # sum dna_count
        for key, value in count_result.items():
            count += value
        return count

    def count_dna(self, char_str):
        """Count DNA bases (A, T, C, G) in a character string.

        Args:
            char_str: String to analyze.

        Returns:
            Count of DNA bases found.
        """
        count = self.count_chars(char_str, ["A", "T", "C", "G"])
        return count

    def count_morphology(self, char_str):
        """Count morphological character states (0-9) in a string.

        Args:
            char_str: String to analyze.

        Returns:
            Count of numeric characters found.
        """
        count = self.count_chars(char_str, ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
        return count

    def count_rna(self, char_str):
        """Count RNA bases (A, U, C, G) in a character string.

        Args:
            char_str: String to analyze.

        Returns:
            Count of RNA bases found.
        """
        count = self.count_chars(char_str, ["A", "U", "C", "G"])
        return count

    def count_protein(self, char_str):
        """Count protein amino acid characters in a string.

        Args:
            char_str: String to analyze.

        Returns:
            Count of standard amino acid codes found.
        """
        count = self.count_chars(
            char_str,
            [
                "A",
                "R",
                "N",
                "D",
                "C",
                "Q",
                "E",
                "G",
                "H",
                "I",
                "L",
                "K",
                "M",
                "F",
                "P",
                "S",
                "T",
                "W",
                "Y",
                "V",
            ],
        )
        return count

    # when exporting as file
    def matrix_as_string(self, parens=["(", ")"], separator=" "):
        """Convert datamatrix to string format for export.

        Formats the character matrix as a multi-line string with taxon
        names and character states. Handles polymorphic characters
        (represented as lists) by wrapping them in parentheses.

        Args:
            parens: Opening and closing characters for polymorphic states.
                Defaults to ["(", ")"].
            separator: Character to separate taxon name from data and
                polymorphic character states. Defaults to " ".

        Returns:
            Multi-line string with one taxon per line.
        """
        matrix_string = ""
        datamatrix = self.datamatrix_as_list()
        taxa_list = json.loads(self.taxa_list_json)
        # print("datamatrix:",datamatrix)
        for idx, data in enumerate(datamatrix):
            # print("data:",data)
            taxon_string = ""
            taxon_name = taxa_list[idx]
            # print("taxon:",taxon_name)
            # print(formatted_data)
            taxon_string += taxon_name + separator
            for char_state in data:
                # print("char:",char_state)
                if type(char_state) is list:
                    taxon_string += parens[0] + separator.join(char_state) + parens[1]
                    # print("poly:",parens[0] + separator.join(char_state) + parens[1])
                else:
                    taxon_string += char_state
            matrix_string += taxon_string + "\n"
        return matrix_string

    def as_phylip_format(self):
        """Export datamatrix as Phylip format string.

        Returns:
            String in Phylip sequential format with dimensions header
            and matrix data.
        """
        phylip_string = ""
        data_string = self.matrix_as_string()
        phylip_string += str(self.n_taxa) + " " + str(self.n_chars) + "\n"
        phylip_string += data_string
        return phylip_string

    def as_tnt_format(self):
        """Export datamatrix as TNT format string.

        Returns:
            String in TNT xread format with dataset name and matrix data.
        """
        tnt_string = ""
        data_string = self.matrix_as_string()
        tnt_string += (
            "xread '"
            + self.dataset_name
            + "' "
            + str(self.phylo_matrix.n_chars)
            + " "
            + str(self.phylo_matrix.n_taxa)
            + "\n"
        )
        tnt_string += data_string
        tnt_string += ";\n"
        return tnt_string

    def as_nexus_format(self):
        """Export datamatrix as Nexus format string.

        Returns:
            String in Nexus format with data block including dimensions,
            format commands, and matrix data.
        """
        nexus_string = ""
        data_string = self.matrix_as_string()
        command_string = self.command_as_string()
        nexus_string += "#NEXUS\n\n"
        nexus_string += "begin data;\n"
        nexus_string += command_string
        nexus_string += "matrix\n"
        nexus_string += data_string
        nexus_string += ";\n"
        nexus_string += "end;\n"
        return nexus_string

    def command_as_string(self):
        """Generate Nexus format command strings.

        Creates the dimensions and format commands for Nexus export,
        either from stored nexus_command_hash or from defaults.

        Returns:
            Multi-line string of Nexus commands (dimensions, format, etc.).
        """
        command_string = ""
        if self.nexus_command_hash:
            for key1 in self.nexus_command_hash.keys():
                variable_list = []
                for key2 in self.nexus_command_hash[key1].keys():
                    variable_list.append(key2 + "=" + self.nexus_command_hash[key1][key2])
                command_string += key1 + " " + " ".join(variable_list) + ";\n"
            # print(command_string)
        else:
            command_string += f"dimensions ntax={self.n_taxa} nchar={self.n_chars};\n"
            command_string += "format datatype={datatype} gap={gap} missing={missing};\n".format(
                datatype=self.DEFAULTS["datatype"],
                gap=self.DEFAULTS["gap"],
                missing=self.DEFAULTS["missing"],
            )
        return command_string


class PfPackage(Model):
    """External analysis software package metadata.

    Stores information about external phylogenetic analysis software
    (TNT, IQTree, MrBayes) including version, paths, and capabilities.
    Used to track which software is available and configured.

    Attributes:
        package_name: Name of the software package (e.g., "TNT", "IQTree").
        package_version: Version string of the installed software.
        package_desc: Optional description of the package.
        package_type: Type of analysis supported (Parsimony, ML, Bayesian).
        run_path: File system path to the executable.
        created_at: Timestamp when the package was registered.
        modified_at: Timestamp of last modification.

    Relations:
        analyses: One-to-many relationship to PfAnalysis that use this package.

    Example:
        Registering TNT software::

            tnt = PfPackage.create(
                package_name="TNT",
                package_version="1.5",
                package_type=ANALYSIS_TYPE_PARSIMONY,
                run_path="/usr/local/bin/tnt"
            )
    """

    package_name = CharField()
    package_version = CharField()
    package_desc = CharField(null=True)
    package_type = CharField(default=ANALYSIS_TYPE_PARSIMONY)
    run_path = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    modified_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = gDatabase


class PfAnalysis(Model):
    """Analysis configuration and execution tracking model.

    Stores configuration parameters and runtime state for phylogenetic
    analyses. Supports three analysis types: Parsimony (TNT), Maximum
    Likelihood (IQTree), and Bayesian (MrBayes). Tracks analysis status
    from creation through execution to completion.

    The analysis model stores both the input configuration and the
    execution state. It maintains copies of the datamatrix at analysis
    time to preserve reproducibility even if the source data changes.

    Attributes:
        datamatrix: Foreign key to source PfDatamatrix.
        package: Foreign key to PfPackage software used (optional).
        analysis_type: Type of analysis (Parsimony, ML, or Bayesian).
        analysis_name: User-specified name for this analysis.
        analysis_status: Current status (Ready, Running, Completed, etc.).
        result_directory: File system path where results are stored.
        datafile: Path to exported data file used as input.
        taxa_list_json: Snapshot of taxa at analysis time.
        character_list_json: Snapshot of character names at analysis time.
        datamatrix_json: Snapshot of matrix data at analysis time.
        completion_percentage: Progress indicator (0-100).
        start_datetime: When analysis execution began.
        finish_datetime: When analysis execution completed.

        ml_bootstrap: Number of bootstrap replicates (ML analyses).
        ml_bootstrap_type: Bootstrap type (Normal or Ultrafast).
        ml_substitution_model: Substitution model code (e.g., "GTR").
        mcmc_burnin: MCMC burn-in iterations (Bayesian analyses).
        mcmc_relburnin: Use relative burn-in (Bayesian).
        mcmc_burninfrac: Burn-in fraction (Bayesian).
        mcmc_ngen: Number of MCMC generations (Bayesian).
        mcmc_nst: Number of substitution types (Bayesian).
        mcmc_nrates: Rate variation model (Bayesian).
        mcmc_printfreq: Print frequency for MCMC (Bayesian).
        mcmc_samplefreq: Sampling frequency for MCMC (Bayesian).
        mcmc_nruns: Number of independent runs (Bayesian).
        mcmc_nchains: Number of chains per run (Bayesian).

        created_at: Timestamp when analysis was created.
        modified_at: Timestamp of last modification.

    Relations:
        trees: One-to-many relationship to PfTree results.
            Cascade deletes when analysis is deleted.

    Example:
        Creating a parsimony analysis::

            analysis = PfAnalysis.create(
                datamatrix=my_datamatrix,
                analysis_type=ANALYSIS_TYPE_PARSIMONY,
                analysis_name="TNT parsimony run 1",
                analysis_status=ANALYSIS_STATUS_READY
            )

    Note:
        Analysis status lifecycle: Ready → Running → Completed/Failed/Stopped
    """

    datamatrix = ForeignKeyField(PfDatamatrix, backref="analyses", on_delete="CASCADE")
    package = ForeignKeyField(PfPackage, backref="analyses", null=True)
    analysis_type = CharField()
    analysis_name = CharField()
    analysis_status = CharField(null=True)
    result_directory = CharField(null=True)
    datafile = CharField(null=True)
    taxa_list_json = CharField(null=True)
    character_list_json = CharField(null=True)
    datamatrix_json = CharField(null=True)
    completion_percentage = IntegerField(default=0)
    start_datetime = DateTimeField(default=datetime.datetime.now)
    finish_datetime = DateTimeField(null=True)

    ml_bootstrap = IntegerField(default=100)
    ml_bootstrap_type = CharField(default=BOOTSTRAP_TYPE_NORMAL)
    ml_substitution_model = CharField(default="GTR")
    mcmc_burnin = IntegerField(default=1000)
    mcmc_relburnin = BooleanField(default=False)
    mcmc_burninfrac = FloatField(default=0.25)
    mcmc_ngen = IntegerField(default=1000000)
    mcmc_nst = IntegerField(default=6)
    mcmc_nrates = CharField(default="gamma")
    mcmc_printfreq = IntegerField(default=1000)
    mcmc_samplefreq = IntegerField(default=100)
    mcmc_nruns = IntegerField(default=1)
    mcmc_nchains = IntegerField(default=1)

    created_at = DateTimeField(default=datetime.datetime.now)
    modified_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = gDatabase

    def has_tree(self):
        """Check if analysis has produced a tree file.

        Checks for the expected tree file location based on analysis type.
        Different analysis types produce trees in different file formats
        and locations.

        Note:
            This method appears incomplete in the current implementation.
        """
        run = self.run
        data_filename = os.path.split(str(self.datafile))[-1]
        filename, fileext = os.path.splitext(data_filename.upper())
        if self.analysis_type == ANALYSIS_TYPE_ML:
            tree_filename = os.path.join(self.result_directory, filename + ".phy.treefile")
        elif self.analysis_type == ANALYSIS_TYPE_BAYESIAN:
            tree_filename = os.path.join(self.result_directory, filename + ".nex1.con.tre")
        elif self.analysis_type == ANALYSIS_TYPE_PARSIMONY:
            tree_filename = os.path.join(self.result_directory, "aquickie.tre")

    def get_tree(self):
        """Get tree from analysis results.

        Reads the tree file produced by Maximum Likelihood analysis
        and returns an ASCII representation.

        Returns:
            ASCII art tree string if tree file exists and is readable,
            otherwise returns the expected tree filename.

        Note:
            Currently only implemented for ML analyses. Returns filename
            if file doesn't exist.
        """
        if self.analysis_type == ANALYSIS_TYPE_ML:
            data_filename = os.path.split(str(self.datafile))[-1]
            filename, fileext = os.path.splitext(data_filename.upper())
            tree_filename = os.path.join(self.result_directory, filename + ".phy.treefile")
            if os.path.exists(tree_filename):
                tree = Phylo.read(tree_filename, "newick")
                return Phylo.draw_ascii(tree)
            return tree_filename


class PfTree(Model):
    """Phylogenetic tree storage and visualization options.

    Stores phylogenetic trees in Newick format along with visualization
    preferences. Trees are the final output of analyses and can be
    visualized in various styles with character state mapping.

    Supports multiple tree types including consensus trees, bootstrap
    trees, posterior probability trees, and most-parsimonious trees (MPT).

    Attributes:
        analysis: Foreign key to parent PfAnalysis.
        tree_name: User-specified name for the tree.
        tree_type: Type of tree (Consensus, Bootstrap, Posterior, MPT).
        tree_desc: Optional description of the tree.
        newick_text: Tree topology in Newick format.
        tree_options_json: JSON string of visualization options.
        comment: Optional comments or notes about the tree.
        created_at: Timestamp when tree was created.
        modified_at: Timestamp of last modification.

    Example:
        Creating and configuring a tree::

            tree = PfTree.create(
                analysis=my_analysis,
                tree_name="Consensus tree",
                tree_type=TREE_TYPE_CONSENSUS,
                newick_text="((A,B),C);"
            )

            options = tree.get_tree_options()
            options["char_mapping"] = True
            options["font_size"] = 12
            tree.pack_tree_options(options)
            tree.save()
    """

    analysis = ForeignKeyField(PfAnalysis, backref="trees", on_delete="CASCADE")
    tree_name = CharField()
    tree_type = CharField()
    tree_desc = CharField(null=True)
    newick_text = CharField(null=True)
    tree_options_json = CharField(null=True)
    comment = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    modified_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = gDatabase

    def get_tree_options(self):
        """Get tree visualization options.

        Retrieves visualization options from JSON storage, filling in
        any missing options with defaults. Options control how the tree
        is rendered including style, character mapping, and formatting.

        Returns:
            Dictionary of tree visualization options with keys:
                - tree_style: Rendering style (topology, phylogram, etc.)
                - char_mapping: Whether to show character state changes
                - align_taxa: Whether to align terminal taxa names
                - italic_taxa_name: Whether to italicize taxon names
                - font_size: Font size for rendering
                - timetree: Whether to scale by time
                - node_minimum_offset: Minimum spacing for nodes
        """
        default_options = {
            "tree_style": pu.TREE_STYLE_TOPOLOGY,
            "char_mapping": False,
            "align_taxa": False,
            "italic_taxa_name": False,
            "font_size": 10,
            "timetree": False,
            "node_minimum_offset": 0.1,
        }
        if self.tree_options_json:
            try:
                tree_options = json.loads(self.tree_options_json)
                for key in default_options:
                    if key not in tree_options:
                        tree_options[key] = default_options[key]
                return tree_options
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing tree options JSON for {self.tree_name}: {e}")
                return default_options
        else:
            return default_options

    def pack_tree_options(self, options_dict):
        """Store tree visualization options as JSON.

        Args:
            options_dict: Dictionary of visualization options to store.
        """
        self.tree_options_json = json.dumps(options_dict)
