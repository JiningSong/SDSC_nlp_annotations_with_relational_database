from nlp_pipelines import *
from models import *
from utils import *
from db import *
import time


# path to sample data file
DATA_FILE = "/Users/jining/Projects/FMP/coreNLP_relational/documents/newspaper.lg.json"


if __name__ == "__main__":
    start_time = time.time()
    # Connect to db
    HOST_NAME = "localhost"
    DATABASE = "stanford_corenlp_results"
    db = Database(HOST_NAME, DATABASE)

    # read in documents from data file
    documents_list = read_json(DATA_FILE)

    # generate documents object
    documents = create_documents(documents_list)
    # Insert documents to db
    db.insert_documents(documents)

    # Annotate documents and create tokens
    tokens = segment_and_upload_sents(db, documents)

    # Close db connection
    db.close()
    print("--- %s seconds ---" % (time.time() - start_time))

