from pipelines import database_insertion_pipeline
from configparser import ConfigParser
from db import *


if __name__ == "__main__":

    # read db_configs (configs for establishing db connection) from config.ini
    configs = ConfigParser()
    configs.read("config.ini")
    db_configs = configs["DATABASECONFIG"]
    table_names = configs["TABLENAMES"]

    # establish db connection
    db = Database(db_configs, table_names)

    # insert new data from inserfile into database
    source_file_path = configs["SOURCEFILE"]["PATH"]
    database_insertion_pipeline(source_file_path, db)

    db.close()
