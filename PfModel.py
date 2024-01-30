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
LINE_SEPARATOR = "\n"

database_path = os.path.join(pu.DEFAULT_DB_DIRECTORY, 'PhyloForester.db')

gDatabase = SqliteDatabase(database_path,pragmas={'foreign_keys': 1})

def setup_database_location(database_dir):
    database_handle = SqliteDatabase(database_path,pragmas={'foreign_keys': 1})
    return database_handle


class PfProject(Model):
    project_name = CharField()
    project_desc = CharField(null=True)
    datatype = CharField(null=True)
    taxa_str = CharField(null=True)
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
    characters_str = CharField(null=True)
    n_taxa = IntegerField()
    n_chars = IntegerField()
    datamatrix_json = CharField(null=True)
    whole_text = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    modified_at = DateTimeField(default=datetime.datetime.now)

    datamatrix = []
    taxa_list = []
    characters_list = []
    DEFAULTS = { 'gap': '-', 'missing': '?', 'datatype': 'standard' }

    class Meta:
        database = gDatabase

    def datamatrix_as_list(self):
        if self.datamatrix_json:
            formatted_data_list = json.loads(self.datamatrix_json)
            return formatted_data_list
        else:
            return ""

    def import_file(self, file_path):
        datafile_obj = pu.PhyloDatafile()
        ret = datafile_obj.loadfile(file_path)

        if ret:
            self.datamatrix_name = datafile_obj.dataset_name
            self.whole_text = datafile_obj.file_text

            self.n_taxa = datafile_obj.n_taxa
            self.n_chars = datafile_obj.n_chars
            self.taxa_list = datafile_obj.taxa_list
            self.block_hash = datafile_obj.block_hash
            self.whole_text = datafile_obj.file_text
            self.formatted_data_list = datafile_obj.formatted_data_list
            if len(self.formatted_data_list) > 0:
                self.datamatrix_json = json.dumps(self.formatted_data_list,indent=4)

            #print("post load",self.formatted_data_list)
            
            #if datafile_obj.file_type == 'Nexus':
            #    if datafile_obj.block_hash['MRBAYES']:
            #        self.mrbayes_block = datafile_obj.block_as_json('MRBAYES')
            #    if datafile_obj.command_hash:
            #        self.nexus_command_json = datafile_obj.command_hash_as_json()
        else:
            return False

        return True

class PfPackage(Model):
    package_name = CharField()
    package_version = CharField()
    package_desc = CharField(null=True)
    run_path = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    modified_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        database = gDatabase


class PfAnalysis(Model):
    project = ForeignKeyField(PfProject, backref='analyses', on_delete='CASCADE')
    package = ForeignKeyField(PfPackage, backref='analyses')
    analysis_type = CharField()
    analysis_name = CharField()

    created_at = DateTimeField(default=datetime.datetime.now)
    modified_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = gDatabase
