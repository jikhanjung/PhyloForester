"""Peewee migrations -- 001_20240219.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['table_name']            # Return model in current state by name
    > Model = migrator.ModelClass                   # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.run(func, *args, **kwargs)           # Run python function with the given args
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.add_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)
    > migrator.add_constraint(model, name, sql)
    > migrator.drop_index(model, *col_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.drop_constraints(model, *constraints)

"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your migrations here."""
    
    @migrator.create_model
    class PfProject(pw.Model):
        id = pw.AutoField()
        project_name = pw.CharField(max_length=255)
        project_desc = pw.CharField(max_length=255, null=True)
        created_at = pw.DateTimeField()
        modified_at = pw.DateTimeField()

        class Meta:
            table_name = "pfproject"

    @migrator.create_model
    class PfDatamatrix(pw.Model):
        id = pw.AutoField()
        project = pw.ForeignKeyField(column_name='project_id', field='id', model=migrator.orm['pfproject'], on_delete='CASCADE')
        datamatrix_name = pw.CharField(max_length=255)
        datamatrix_desc = pw.CharField(max_length=255, null=True)
        datamatrix_index = pw.IntegerField(default=1)
        datatype = pw.CharField(default='Morphology', max_length=255)
        n_taxa = pw.IntegerField()
        n_chars = pw.IntegerField()
        taxa_list_json = pw.CharField(max_length=255, null=True)
        taxa_timetable_json = pw.CharField(max_length=255, null=True)
        character_list_json = pw.CharField(max_length=255, null=True)
        datamatrix_json = pw.CharField(max_length=255, null=True)
        whole_text = pw.CharField(max_length=255, null=True)
        created_at = pw.DateTimeField()
        modified_at = pw.DateTimeField()

        class Meta:
            table_name = "pfdatamatrix"

    @migrator.create_model
    class PfPackage(pw.Model):
        id = pw.AutoField()
        package_name = pw.CharField(max_length=255)
        package_version = pw.CharField(max_length=255)
        package_desc = pw.CharField(max_length=255, null=True)
        package_type = pw.CharField(default='Parsimony', max_length=255)
        run_path = pw.CharField(max_length=255, null=True)
        created_at = pw.DateTimeField()
        modified_at = pw.DateTimeField()

        class Meta:
            table_name = "pfpackage"

    @migrator.create_model
    class PfAnalysis(pw.Model):
        id = pw.AutoField()
        datamatrix = pw.ForeignKeyField(column_name='datamatrix_id', field='id', model=migrator.orm['pfdatamatrix'], on_delete='CASCADE')
        package = pw.ForeignKeyField(column_name='package_id', field='id', model=migrator.orm['pfpackage'], null=True)
        analysis_type = pw.CharField(max_length=255)
        analysis_name = pw.CharField(max_length=255)
        analysis_status = pw.CharField(max_length=255, null=True)
        result_directory = pw.CharField(max_length=255, null=True)
        datafile = pw.CharField(max_length=255, null=True)
        taxa_list_json = pw.CharField(max_length=255, null=True)
        character_list_json = pw.CharField(max_length=255, null=True)
        datamatrix_json = pw.CharField(max_length=255, null=True)
        completion_percentage = pw.IntegerField(default=0)
        start_datetime = pw.DateTimeField()
        finish_datetime = pw.DateTimeField(null=True)
        ml_bootstrap = pw.IntegerField(default=100)
        ml_bootstrap_type = pw.CharField(default='Normal', max_length=255)
        ml_substitution_model = pw.CharField(default='GTR', max_length=255)
        mcmc_burnin = pw.IntegerField(default=1000)
        mcmc_relburnin = pw.BooleanField(default=False)
        mcmc_burninfrac = pw.FloatField(default=0.25)
        mcmc_ngen = pw.IntegerField(default=1000000)
        mcmc_nst = pw.IntegerField(default=6)
        mcmc_nrates = pw.CharField(default='gamma', max_length=255)
        mcmc_printfreq = pw.IntegerField(default=1000)
        mcmc_samplefreq = pw.IntegerField(default=100)
        mcmc_nruns = pw.IntegerField(default=1)
        mcmc_nchains = pw.IntegerField(default=1)
        created_at = pw.DateTimeField()
        modified_at = pw.DateTimeField()

        class Meta:
            table_name = "pfanalysis"

    @migrator.create_model
    class PfTree(pw.Model):
        id = pw.AutoField()
        analysis = pw.ForeignKeyField(column_name='analysis_id', field='id', model=migrator.orm['pfanalysis'], on_delete='CASCADE')
        tree_name = pw.CharField(max_length=255)
        tree_type = pw.CharField(max_length=255)
        tree_desc = pw.CharField(max_length=255, null=True)
        newick_text = pw.CharField(max_length=255, null=True)
        tree_options_json = pw.CharField(max_length=255, null=True)
        comment = pw.CharField(max_length=255, null=True)
        created_at = pw.DateTimeField()
        modified_at = pw.DateTimeField()

        class Meta:
            table_name = "pftree"


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""
    
    migrator.remove_model('pftree')

    migrator.remove_model('pfanalysis')

    migrator.remove_model('pfpackage')

    migrator.remove_model('pfdatamatrix')

    migrator.remove_model('pfproject')
