from models import *
from db import *
from tqdm import tqdm
import pandas as pd
import json
import multiprocessing as mp
import hashlib
import stanza


# Download specific processors from stanza library
def download_stanza():
    stanza.download('en', processors='depparse')


# Read in documents from csv file
def get_documents_from_csv(filepath):
    documents = []
    data = pd.read_csv(filepath)
    for el in data.iloc[:, 4].tolist():
        if type(el) is str:
            documents.append(el)
    return documents


"""
    Function:       Read_json
    Description:    Read JSON file from disk. Each data record is stored as a dictionary entry with 
                    two fields: id and news in the memory
    Arguments:      filepath[string] - absolute path to JSON file
    Return:         documents_list - list of dictionaries that stores id and news from each record in JSON
"""


def read_json(filepath):
    documents_list = []
    with open(filepath) as f:
        data = json.load(f)
        t = tqdm(total=len(data), desc="Reading JSON File from Disk: ")
        for el in data:
            doc_id = el['id']
            text = el['news']
            text = text.replace('\n', '').replace('\r', '')
            record = [doc_id, text]
            documents_list.append(record)
            t.update(1)
    t.close()
    return documents_list


"""
    Function:       create_documents
    Description:    Convert documents_list (list of document dictionary) to documents (list of document objects)
    Arguments:      documents_list[list of documents] - raw document data stored in list of dictionaries
    Return:         documents - list of document objects
"""


def create_documents(documents_list):
    documents = []
    for doc in documents_list:
        document = Document(doc[1], doc[0])
        documents.append(document)
    return documents


"""
    Function:       perform_nlp_pipeline
    Description:    Main nlp pipeline that seperate doc into sentences followed by tokenization of sentences 
                    and annotating tokens through POS tagger, NER tagger, and depparser. The sentences and annotations are 
                    stored into tables in DB respectively.
    Arguments:      doc[string] - document text 
"""


def perform_nlp_pipeline(doc):
    db = Database()
    tokens = []
    annotated_text = generate_document(doc.text)
    sent_segmentations = annotate_document(annotated_text)

    for el in sent_segmentations:
        annotate_sent = Sentence(
            doc.doc_id, el['sentence_text'], el['start_char'], el['end_char'])

        # insert sentence to db and save generated uuid in sentence object
        uuid = db.insert_sentence(annotate_sent)
        annotate_sent.set_sentence_id(uuid)

        for token_dict in el['tokens']:
            token = Token(annotate_sent, token_dict)
            tokens.append(token)
    for token in tokens:
        db.insert_lemma_annotation(token)
        db.insert_pos_annotation(token)
        db.insert_depparse_annotation(token)
        db.insert_ner_annotation(token)


"""
    Function:       populate_annotation_tables
    Description:    wrapper function that allocates nlp_pipeline work to multiple cores
    Arguments:      documents_list[list of documents]
"""


def populate_annotation_tables(documents):
    t = tqdm(total=len(documents),
             desc="Annotating documents and Populating sentence segmentations table: ")
    pool = mp.Pool(mp.cpu_count())
    for doc in documents:
        pool.apply(perform_nlp_pipeline, args=(doc))
        t.update(1)
    t.close()


"""
    Function:       uuid_to_bigint
    Description:    convert uuid to bigint
    Arguments:      uuid[string]
    Return:         bigint resulting from applying hash function on uuid
"""


def uuid_to_bigint(uuid):
    return int(hashlib.sha256(uuid.encode('utf-8')).hexdigest(), 16) % 100**8


def populate_database(DATA_FILE):
    start_time = time.time()
    # Construct connection to Database
    db = Database()

    # read in documents from data file
    documents_list = read_json(DATA_FILE)

    # generate documents object
    documents = create_documents(documents_list)
    # Insert documents to db
    db.insert_documents(documents)

    # Annotate documents and create tokens
    populate_annotation_tables(documents)

    # Close db connection
    db.close()
    print("--- %s seconds ---" % (time.time() - start_time))
