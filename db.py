import psycopg2
import json
from nlp_pipelines import *
from models import *
from utils import *

# Global Insert query strings
DOCUMENTS_QUERY = "INSERT INTO documents VALUES(%s, %s)"
SENT_SEGMENTATION_QUERY = "INSERT INTO sentence_segmentation(doc_id, sentence_text, start_char, end_char) VALUES(%s, %s, %s, %s)"
POS_QUERY = "INSERT INTO pos_annotations VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
LEMMA_QUERY = "INSERT INTO lemma_annotations VALUES(%s, %s, %s, %s, %s, %s, %s)"
DEPPARSE_QUERY = "INSERT INTO depparse_annotations VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
NER_QUERY = "INSERT INTO ner_annotations VALUES(%s, %s, %s, %s, %s, %s, %s)"
UUID_QUERY = "SELECT sentence_id FROM sentence_segmentation WHERE sentence_text=%s"

class Database:
    """
    Database object 

    This database object create connection and cursor instances 
    and handles database queries

    Constructor:
    hostname (string)
    databse (string)

    """

    def __init__(self, hostname, database):
         # Connect to db
        self.conn = conn = psycopg2.connect(
            host = hostname,
            database = database
        )

        # Declare cursor
        self.cursor = conn.cursor()
    
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

    def close(self):
        self.cursor.close()
        self.conn.close()
