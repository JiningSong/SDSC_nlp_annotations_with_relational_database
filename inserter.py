from pipelines import database_insertion_pipeline
from configparser import ConfigParser
from db import *

class Inserter:
    def __init__(self, path_to_configfile):
        self.configs = ConfigParser()
        self.configs.read(path_to_configfile)

    def start_insertion(self):
        db_configs = self.configs["DATABASECONFIG"]
        table_names = self.configs["TABLENAMES"]

        # establish db connection
        db = Database(db_configs, table_names)

        # insert new data from inserfile into database
        source_file_path = self.configs["SOURCEFILE"]["PATH"]
        database_insertion_pipeline(source_file_path, db)

        db.close()
