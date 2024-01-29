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

LINE_SEPARATOR = "\n"

database_path = os.path.join(pu.DEFAULT_DB_DIRECTORY, 'PhyloForester.db')

gDatabase = SqliteDatabase(database_path,pragmas={'foreign_keys': 1})

def setup_database_location(database_dir):
    database_handle = SqliteDatabase(database_path,pragmas={'foreign_keys': 1})
    return database_handle


class PfDataset(Model):
    dataset_name = CharField()
    dataset_desc = CharField(null=True)
    datatype = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    modified_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        database = gDatabase

class PfTaxon(Model):
    dataset = ForeignKeyField(PfDataset, backref='taxa')
    taxon_name = CharField()
    taxon_desc = CharField(null=True)
    taxon_index = IntegerField()
    created_at = DateTimeField(default=datetime.datetime.now)
    modified_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        database = gDatabase

class PfCharacter(Model):
    dataset = ForeignKeyField(PfDataset, backref='characters')
    character_name = CharField()
    character_desc = CharField(null=True)
    character_index = IntegerField()
    created_at = DateTimeField(default=datetime.datetime.now)
    modified_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        database = gDatabase

class PfDatamatrix(Model):
    dataset = ForeignKeyField(PfDataset, backref='datamatrices')
    datamatrix_name = CharField()
    datamatrix_desc = CharField(null=True)
    datamatrix_index = IntegerField()
    created_at = DateTimeField(default=datetime.datetime.now)
    modified_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        database = gDatabase