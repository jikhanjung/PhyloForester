from collections import Counter
from peewee import *
import datetime
import os
import hashlib
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS
import io
from pathlib import Path
import time
import math
import numpy as np
import copy
import PfUtils as pu
#from MdUtils import *
import shutil
import copy
import json
from Bio import Phylo
ANALYSIS_TYPE_ML = 'Maximum Likelihood'
ANALYSIS_TYPE_PARSIMONY = 'Parsimony'
ANALYSIS_TYPE_BAYESIAN = 'Bayesian'

ANALYSIS_STATUS_QUEUED = 'Queued'
ANALYSIS_STATUS_RUNNING = 'Running'
ANALYSIS_STATUS_FINISHED = 'Complete'
ANALYSIS_STATUS_FAILED = 'Failed'

DATATYPE_DNA = 'DNA'
DATATYPE_RNA = 'RNA'
DATATYPE_PROTEIN = 'Protein'
DATATYPE_STANDARD = 'Standard'
DATATYPE_MORPHOLOGY = 'Morphology'
DATATYPE_COMBINED = 'Combined'

BOOTSTRAP_TYPE_NORMAL = 'Normal'
BOOTSTRAP_TYPE_ULTRAFAST = 'Ultrafast'

LINE_SEPARATOR = "\n"

database_path = os.path.join(pu.DEFAULT_DB_DIRECTORY, 'PhyloForester.db')

gDatabase = SqliteDatabase(database_path,pragmas={'foreign_keys': 1})

def setup_database_location(database_dir):
    database_handle = SqliteDatabase(database_path,pragmas={'foreign_keys': 1})
    return database_handle


class PfProject(Model):
    project_name = CharField()
    project_desc = CharField(null=True)
    #datatype = CharField(null=True)
    #taxa_str = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    modified_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        database = gDatabase

    def get_taxa_list(self):
        if self.taxa_str:
            return self.taxa_str.split(',')
        else:
            return []

class PfDatamatrix(Model):
    project = ForeignKeyField(PfProject, backref='datamatrices', on_delete='CASCADE')
    datamatrix_name = CharField()
    datamatrix_desc = CharField(null=True)
    datamatrix_index = IntegerField(default=1)
    datatype = CharField(default=DATATYPE_MORPHOLOGY)
    n_taxa = IntegerField()
    n_chars = IntegerField()
    taxa_list_json = CharField(null=True)
    character_list_json = CharField(null=True)
    datamatrix_json = CharField(null=True)
    whole_text = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    modified_at = DateTimeField(default=datetime.datetime.now)

    datamatrix = []
    taxa_list = []
    characters_list = []
    DEFAULTS = { 'gap': '-', 'missing': '?', 'datatype': 'standard' }
    nexus_command_hash = None

    class Meta:
        database = gDatabase

    def get_character_list(self):
        if self.character_list_json:
            return json.loads(self.character_list_json)
        else:
            return []

    def datamatrix_as_list(self):
        if self.datamatrix_json:
            formatted_data_list = json.loads(self.datamatrix_json)
            return formatted_data_list
        else:
            return ""

    def get_taxa_list(self):
        if self.taxa_list_json:
            #formatted_data_list = json.loads(self.datamatrix_json)
            return json.loads(self.taxa_list_json)
        else:
            return []

    def import_file(self, file_path):
        datafile_obj = pu.PhyloDatafile()
        ret = datafile_obj.loadfile(file_path)

        if ret:
            self.datamatrix_name = datafile_obj.dataset_name
            self.whole_text = datafile_obj.file_text

            self.n_taxa = datafile_obj.n_taxa
            self.n_chars = datafile_obj.n_chars
            self.taxa_list = datafile_obj.taxa_list
            self.datamatrix = datafile_obj.datamatrix
            self.block_hash = datafile_obj.block_hash
            self.whole_text = datafile_obj.file_text
            self.formatted_data_list = datafile_obj.formatted_data_list
            self.nexus_command_hash = datafile_obj.nexus_command_hash
            if len( self.taxa_list ) > 0:
                self.taxa_list_json = json.dumps(self.taxa_list)
            if len( self.datamatrix ) > 0:
                self.datamatrix_json = json.dumps(self.datamatrix,indent=4)
            

            type_count = {DATATYPE_DNA: 0, DATATYPE_RNA: 0, DATATYPE_PROTEIN: 0, DATATYPE_MORPHOLOGY: 0, DATATYPE_COMBINED: 0}
            for char_idx in range(self.n_chars):
                char_str = ''
                for taxon_idx in range(self.n_taxa):
                    char = self.datamatrix[taxon_idx][char_idx]
                    if isinstance(char, list):
                        char_str += ''.join(char)
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
                #print("char idx:",char_idx, "char_str", char_str,"max:",max_datatype,"max_value:",max_value)
                       
            max_datatype = max(type_count, key=type_count.get)
            self.datatype = max_datatype
            #print("datatype:",self.datatype)
        else:
            return False

        return True

    def count_chars(self, char_str, char_list):
        '''
        char_count = 0
        for char in char_list:
            char_count += char_str.count(char)
        return char_count
        '''
        chars = (char.lower() for char in char_str if char.upper() in char_list)
        count_result = Counter(chars)
        count = 0
        # sum dna_count
        for key, value in count_result.items():
            count += value
        return count
    

    def count_dna(self, char_str):
        count = self.count_chars( char_str, [ 'A','T','C','G'])
        return count

    def count_morphology(self, char_str):
        count = self.count_chars( char_str, [ '0','1','2','3','4', '5','6','7','8','9'])
        return count

    def count_rna(self, char_str):
        count = self.count_chars( char_str, [ 'A','U','C','G'])
        return count

    def count_protein(self, char_str):
        count = self.count_chars( char_str, [ 'A','R','N','D','C','Q','E','G','H','I','L','K','M','F','P','S','T','W','Y','V'])
        return count
    


    # when exporting as file
    def matrix_as_string(self,parens=["(",")"],separator=" "):
        matrix_string = ""
        datamatrix = self.datamatrix_as_list()
        taxa_list = json.loads(self.taxa_list_json)
        print("datamatrix:",datamatrix)
        for idx, data in enumerate(datamatrix):
            print("data:",data)
            taxon_string = ""
            taxon_name = taxa_list[idx]
            print("taxon:",taxon_name)
            #print(formatted_data)
            taxon_string += taxon_name + separator
            for char_state in data:
                #print("char:",char_state)
                if type(char_state) is list:
                    taxon_string += parens[0] + separator.join(char_state) + parens[1]
                    #print("poly:",parens[0] + separator.join(char_state) + parens[1])
                else:
                    taxon_string += char_state
            matrix_string += taxon_string + "\n"
        return matrix_string


    def as_phylip_format(self):
        phylip_string = ""
        data_string = self.matrix_as_string()
        phylip_string += str(self.n_taxa) + " " + str(self.n_chars) + "\n"
        phylip_string += data_string
        return phylip_string

    def as_tnt_format(self):
        tnt_string = ""
        data_string = self.matrix_as_string()
        tnt_string += "xread '" + self.dataset_name + "' " + str(self.phylo_matrix.n_chars) + " " + str(self.phylo_matrix.n_taxa) + "\n"
        tnt_string += data_string
        tnt_string += ";\n"
        return tnt_string

    def as_nexus_format(self):
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
        command_string = ""
        if self.nexus_command_hash:
                
            for key1 in self.nexus_command_hash.keys():
                variable_list = []
                for key2 in self.nexus_command_hash[key1].keys():
                    variable_list.append( key2 + "=" + self.nexus_command_hash[key1][key2] )
                command_string += key1 + " " + " ".join(variable_list) + ";\n"
            #print(command_string)
        else:
            command_string += "dimensions ntax={ntax} nchar={nchar};\n".format(ntax=self.n_taxa, nchar=self.n_chars)
            command_string += "format datatype={datatype} gap={gap} missing={missing};\n".format(datatype=self.DEFAULTS['datatype'], gap=self.DEFAULTS['gap'], missing=self.DEFAULTS['missing'])
        return command_string


class PfPackage(Model):
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
    project = ForeignKeyField(PfProject, backref='analyses', on_delete='CASCADE')
    datamatrix = ForeignKeyField(PfDatamatrix, backref='analyses', on_delete='CASCADE')
    package = ForeignKeyField(PfPackage, backref='analyses', null=True)
    analysis_type = CharField()
    analysis_name = CharField()
    analysis_status = CharField(null=True)
    result_directory = CharField(null=True)
    datafile = CharField(null=True)
    completion_percentage = IntegerField(default=0)
    start_datetime = DateTimeField(default=datetime.datetime.now)
    finish_datetime = DateTimeField(null=True)

    ml_bootstrap = IntegerField(default=100)
    ml_bootstrap_type = CharField(default=BOOTSTRAP_TYPE_NORMAL)
    ml_substitution_model = CharField(default='GTR')
    mcmc_burnin = IntegerField(default=1000)
    mcmc_relburnin = BooleanField(default=False)
    mcmc_burninfrac = FloatField(default=0.25)
    mcmc_ngen = IntegerField(default=1000000)
    mcmc_nst = IntegerField(default=6)
    mcmc_nrates = CharField(default='gamma')
    mcmc_printfreq = IntegerField(default=1000)
    mcmc_samplefreq = IntegerField(default=100)
    mcmc_nruns = IntegerField(default=1)
    mcmc_nchains = IntegerField(default=1)

    created_at = DateTimeField(default=datetime.datetime.now)
    modified_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = gDatabase

    def has_tree(self):
        run = self.run
        data_filename = os.path.split( str(self.datafile) )[-1]
        filename, fileext = os.path.splitext(data_filename.upper())
        if self.analysis_type == ANALYSIS_TYPE_ML:
            tree_filename = os.path.join( self.result_directory, filename + ".phy.treefile" )
        elif self.analysis_type == ANALYSIS_TYPE_BAYESIAN:
            tree_filename = os.path.join( self.result_directory, filename + ".nex1.con.tre" )
        elif self.analysis_type == ANALYSIS_TYPE_PARSIMONY:
            tree_filename = os.path.join( self.result_directory, "aquickie.tre" )

    def get_tree(self):
        if self.analysis_type == ANALYSIS_TYPE_ML:
            data_filename = os.path.split( str(self.datafile) )[-1]
            filename, fileext = os.path.splitext(data_filename.upper())
            tree_filename = os.path.join( self.result_directory, filename + ".phy.treefile" )
            if os.path.exists( tree_filename ):
                tree = Phylo.read( tree_filename, "newick" )
                return Phylo.draw_ascii(tree)
            else:
                return tree_filename
