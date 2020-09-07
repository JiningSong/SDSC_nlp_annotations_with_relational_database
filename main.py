from nlp_pipelines import *
from models import *
from utils import *
from db import *
import time


if __name__ == "__main__":
    # #Populating nlp database
    # DATA_FILE = "/Users/jining/Projects/FMP/coreNLP_relational/documents/newspaper.sm.json"
    # populate_database(DATA_FILE)

    # db = Database()
    # db.populate_han_archive_tbl('HAN_Archive.csv')
    # db.close()

    documents = get_documents_from_csv(
        '/Users/jining/Projects/FMP/coreNLP_relational/CDC_search_results.csv')
    