import time
import spacy
from tqdm import tqdm
from configparser import ConfigParser
from utils import read_json, create_documents
from models import Token, Sentence, Document
from nlp_pipelines import annotate_document_corenlp, annotate_document_spacy


def nlp_pipeline(document, db, nlp):
    sentences = []
    tokens = []
    if nlp == -1:
        annotated_document = annotate_document_corenlp(document.text)    
    else:
        annotated_document = annotate_document_spacy(document.text, nlp)

    for sent in annotated_document:

        annotate_sent = Sentence(
            document.doc_id, sent['sentence_text'], sent['start_char'], sent['end_char'])
        sentences.append(annotate_sent)

        for token_dict in sent['tokens']:
            token = Token(annotate_sent, token_dict)
            tokens.append(token)
    
    return (sentences, tokens)       


def database_insertion_pipeline(filepath, db):
    start_time = time.time()

    # read in documents from data file
    documents_list = read_json(filepath)
 
    # generate documents object
    documents = create_documents(documents_list)

    # insert documents to db
    configs = ConfigParser()
    configs.read("config.ini")
    accept_duplicate_doc = configs["DATABASECONFIG"].getboolean('ACCEPT_DUPLICATE_DOCUMENT')
    documents = db.insert_documents(documents, accept_duplicate_doc)

    # Annotate documents, and populate sentences table and annotations table
    t = tqdm(total=len(documents),
             desc="Annotating documents: ")
    annotator = configs["ANNOTATOR"]["NAME"]

    # load spacy model if annotator option is set to spacy
    if annotator == "spacy":
        spacy.prefer_gpu()
        nlp = spacy.load("en_core_web_lg")
    else:
        nlp = -1

    for doc in documents:
        sentences, tokens = nlp_pipeline(doc, db, nlp)

        for sent in sentences:
            db.insert_sentence(sent)
        
        for token in tokens:
            db.insert_annotations(token)
        t.update(1)
    t.close()
    db.close()

    # Close db connection
    print("--- %s seconds ---" % (time.time() - start_time))