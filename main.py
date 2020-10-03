from utils import populate_cdc_dataset, remove_duplicate_tokens
from db import *


if __name__ == "__main__":
    '''
    # Populating nlp database
    db = Database()
    DATA_FILE = "/Users/jining/Projects/FMP/coreNLP_relational/documents/newspaper.sm.json"
    populate_database(DATA_FILE, db)
    db.close()
    '''

    ''' 
    # Populating cdc dataset
    IS_REMOTE = True
    populate_cdc_dataset(IS_REMOTE)
    '''

    # Removing duplicate tokens from annotations table
    IS_REMOTE = False
    remove_duplicate_tokens(IS_REMOTE)
