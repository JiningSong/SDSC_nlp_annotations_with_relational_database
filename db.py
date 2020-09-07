import ast
import psycopg2
import json
import pandas as pd
from nlp_pipelines import *
from models import *
from utils import *
from tqdm import tqdm


# DB Configs
HOST_NAME = "localhost"
DATABASE = "stanford_corenlp_results"


# Global Insert query strings
DOCUMENTS_QUERY = "INSERT INTO documents VALUES(%s, %s)"
SENT_SEGMENTATION_QUERY = "INSERT INTO sentence_segmentation(doc_id, sentence_text, start_char, end_char) VALUES(%s, %s, %s, %s)"
POS_QUERY = "INSERT INTO pos_annotations VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
LEMMA_QUERY = "INSERT INTO lemma_annotations VALUES(%s, %s, %s, %s, %s, %s, %s)"
DEPPARSE_QUERY = "INSERT INTO depparse_annotations VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
NER_QUERY = "INSERT INTO ner_annotations VALUES(%s, %s, %s, %s, %s, %s, %s)"

UUID_QUERY = "SELECT sentence_id FROM sentence_segmentation WHERE sentence_text=%s"
UPDATE_QUERY = """ UPDATE pos_annotations
            SET sent_id = %s 
            WHERE sentence_id = %s"""
INSERT_QUERY = "INSERT INTO ner_annotations_new VALUES (%s, %s, %s, %s, %s, %s, %s)"    

DISTINCT_TEXT_QUERY = "select distinct token_text from depparse_annotations"
INSERT_VOCABULARY = "INSERT INTO vocabulary VALUES(%s, %s)"

DEPPARSE_TOKEN_QUERY = "SELECT * FROM depparse_annotations"
NER_TOKEN_QUERY = "SELECT * FROM ner_annotations WHERE doc_id=%s and sent_id=%s and token_id=%s"
POS_TOKEN_QUERY = "SELECT * FROM pos_annotations WHERE doc_id=%s and sent_id=%s and token_id=%s"
VOCABULARY_QUERY = "SELECT vocabulary_id FROM vocabulary WHERE vocabulary=%s"
CONSOLIDATED_TBL_INSERT_QUERY = "INSERT INTO ANNOTATIONS VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

HAN_INSERT_QUERY = "INSERT INTO han_archive VALUES(%s, %s, %s, %s, %s, %s, %s)"


class Database:
    """
    Database object 

    This database object create connection and cursor instances 
    and handles database queries

    Constructor:
    hostname (string)
    databse (string)

    """

    def __init__(self):
         # Connect to db
        self.conn = conn = psycopg2.connect(
            host = HOST_NAME,
            database = DATABASE
        )

        # Declare cursor
        self.cursor = conn.cursor()

    def populate_han_archive_tbl(self, csv_path):
        df = pd.read_csv(csv_path)
        t = tqdm(total=df.shape[0], desc="Populating Han Archive Table: ")

        for index, row in df.iterrows():
            message_id = row[0]
            title = row[1]
            url = row[2]
            message_type = row[3]
            publish_date = row[4]
            text = row[5]
            links = ast.literal_eval(row[6])

            self.cursor.execute(HAN_INSERT_QUERY, (message_id, title, url, message_type, publish_date, text, links))
            self.conn.commit()
            t.update(1)
        t.close()


    """
        Function:       insert_documents
        Description:    Insert list of documents objects into DB (documents table)
        Arguments:      documents[list of document objects]
    """
    def insert_documents(self, documents):
        t = tqdm(total=len(documents), desc="Populating Documents Table: ")
        for doc in documents:
            self.cursor.execute(DOCUMENTS_QUERY, doc.to_db_data())
            self.conn.commit()
            t.update(1)

        t.close()
        
    def insert_sentence(self, sentence):
        data = sentence.to_db_data()
        self.cursor.execute(SENT_SEGMENTATION_QUERY, data)
        self.conn.commit()

        # Get UUID of the recent entry
        data = (sentence.sentence_text, )
        self.cursor.execute(UUID_QUERY, data)
        result = self.cursor.fetchall()
        uuid = result[0][0]
        return uuid

    def insert_lemma_annotation(self, token):
        self.cursor.execute(LEMMA_QUERY, token.to_lemma_data())
        self.conn.commit()

    def insert_pos_annotation(self, token):
        self.cursor.execute(POS_QUERY, token.to_pos_data())
        self.conn.commit()

    def insert_depparse_annotation(self, token):
        self.cursor.execute(DEPPARSE_QUERY, token.to_depparse_data())
        self.conn.commit()
    
    def insert_ner_annotation(self, token):
        self.cursor.execute(NER_QUERY, token.to_ner_data())
        self.conn.commit()

    """
        Function:       update_uuid_to_bigint
        Description:    populating a copy of the annotation table with token_id replaced from uuid to bigint
    """
    def update_uuid_to_bigint(self):

        self.cursor.execute("""SELECT * FROM ner_annotations""")
        rows = self.cursor.fetchall()

        t = tqdm(total=len(rows), desc="Updating sent_id: ")

        for row in rows:
            self.cursor.execute(INSERT_QUERY, (row[0], uuid_to_bigint(row[1]), row[2], row[3],row[4],row[5],row[6]))
            self.conn.commit()
            t.update(1)

        t.close()

    def populate_vocabulary_table(self):
        self.cursor.execute(DISTINCT_TEXT_QUERY)
        vocabulary = self.cursor.fetchall()
        
        id = 0

        t = tqdm(total=len(vocabulary), desc="Populating vocabulary Table: ")

        for token in vocabulary:
            self.cursor.execute(INSERT_VOCABULARY, (token[0], id))
            self.conn.commit()
            id += 1
            t.update(1)
        t.close()

    def consolidate_annotation_tables(self):
        self.cursor.execute(DEPPARSE_TOKEN_QUERY)
        depparse_annotations = self.cursor.fetchall()
        t = tqdm(total=len(depparse_annotations), desc="Populating vocabulary Table: ")
        for depparse_annotation in depparse_annotations:
            doc_id = depparse_annotation[0]
            sent_id = depparse_annotation[1]
            token_id = depparse_annotation[2]
            token_text = depparse_annotation[3]

            data = (doc_id, sent_id, token_id)
            self.cursor.execute(NER_TOKEN_QUERY, data)
            ner_annotation = self.cursor.fetchall()[0]

            self.cursor.execute(POS_TOKEN_QUERY, data)
            pos_annotation = self.cursor.fetchall()[0]

            self.cursor.execute(VOCABULARY_QUERY, (token_text, ))
            vocabulary_id = self.cursor.fetchall()[0][0]
            annotation = Annotation(depparse_annotation, ner_annotation, pos_annotation, vocabulary_id)
            data = annotation.to_db_data()
            self.cursor.execute(CONSOLIDATED_TBL_INSERT_QUERY, data)
            self.conn.commit()
            t.update(1)
        t.close()

    def close(self):
        self.cursor.close()
        self.conn.close()

