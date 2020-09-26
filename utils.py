from nlp_pipelines import tokenize_document, annotate_document
from models import Token, Sentence, Document
from db import Database
from tqdm import tqdm
import pandas as pd
import json
import multiprocessing as mp
import stanza
import time


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
    doc_id = 0
    for doc in documents_list:
        document = Document(doc, doc_id)
        documents.append(document)
        doc_id += 1
    return documents


"""
    Function:       perform_nlp_pipeline
    Description:    Main nlp pipeline that seperate doc into sentences followed by tokenization of sentences
                    and annotating tokens through POS tagger, NER tagger, and depparser. The sentences and annotations are
                    stored into tables in DB respectively.
    Arguments:      doc[string] - document text
"""
def perform_nlp_pipeline(doc, is_remote):
    db = Database(is_remote)
    tokens = []
    start_time = time.time()
    tokenized_document = tokenize_document(doc.text)
    annotated_document = annotate_document(tokenized_document)
    print("--- %s seconds ---" % (time.time() - start_time))
    return
    for el in annotated_document:
        annotate_sent = Sentence(
            doc.doc_id, el['sentence_text'], el['start_char'], el['end_char'])

        # insert sentence to db and save generated uuid in sentence object
        # db.insert_sentence(annotate_sent)

        for token_dict in el['tokens']:
            token = Token(annotate_sent, token_dict)
            tokens.append(token)
    for token in tokens:
        # db.insert_lemma_annotation(token)
        # db.insert_pos_annotation(token)
        # db.insert_depparse_annotation(token)
        # db.insert_ner_annotation(token)
        db.insert_annotations(token.to_annotation(db))
    db.close()

"""
    Function:       populate_annotation_tables
    Description:    wrapper function that allocates nlp_pipeline work to multiple cores
    Arguments:      documents_list[list of documents]
"""
def populate_annotation_tables(documents, is_remote):
    t = tqdm(total=len(documents),
             desc="Annotating documents: ")
    for doc in documents:
        perform_nlp_pipeline(doc, is_remote)
        t.update(1)
    t.close()


def populate_database(DATA_FILE, db):
    start_time = time.time()
    # Construct connection to Database

    # read in documents from data file
    documents_list = read_json(DATA_FILE)

    # generate documents object
    documents = create_documents(documents_list)
    # Insert documents to db
    db.insert_documents(documents)

    # Annotate documents and create tokens
    populate_annotation_tables(documents)

    # Close db connection
    print("--- %s seconds ---" % (time.time() - start_time))


def populate_cdc_dataset(is_remote):
    db = Database(is_remote)
    documents = get_documents_from_csv(
        '/Users/jining/Projects/FMP/coreNLP_relational/CDC_search_results.csv')[:1]
    documents = create_documents(documents)
    # db.insert_documents(documents)
    db.close()

    populate_annotation_tables(documents, is_remote)


def remove_duplicate_tokens(is_remote):

    db = Database(is_remote)
    duplicative_sentences = db.find_duplicative_sentences()
   
    t = tqdm(total=len(duplicative_sentences), desc="Deleting and Updating duplicate tokens from same sentences in different docs: ")
   
    for sent_id in duplicative_sentences:

        token_count = db.count_distinct_tokens(sent_id)
        new_doc_id = db.generate_consice_doc_id(sent_id)

        for i in range(1, token_count+ 1):
            db.update_token(new_doc_id, sent_id, i)
        t.update(1)
    t.close()
