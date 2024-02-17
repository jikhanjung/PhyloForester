import datetime
from peewee_migrate import Router
from peewee import *
from PfModel import *
import PfUtils as pu
import os
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

database_path = os.path.join(pu.DEFAULT_DB_DIRECTORY, 'PhyloForester.db')
gDatabase = SqliteDatabase(database_path,pragmas={'foreign_keys': 1})

def get_timestamp():
    import datetime
    now = datetime.datetime.now()
    return now.strftime("%Y%m%d")
migrations_path = pu.resource_path('migrations')
#migrations_path = "migrations"
print("migrations_path: ", migrations_path)
print("database path: ", database_path)
gDatabase.connect()
tables = gDatabase.get_tables()

print("tables: ", tables)
router = Router(gDatabase, migrate_dir=migrations_path)
print("router: ", router)
# set migration_name to YYYYMMDD_HHMMSS
migration_name = get_timestamp()
print("migration_name: ", migration_name)
ret = router.create(auto=[PfProject,PfDatamatrix,PfPackage,PfAnalysis,PfTree], name=migration_name)
print("ret: ", ret)


