import ast
import psycopg2
import json
import hashlib
import pandas as pd
# from utils import uuid_to_bigint
from models import Annotation
from tqdm import tqdm


# DB Configs
HOST_NAME = "localhost"
DATABASE = "stanford_corenlp_results"
REMOTE_HOST_NAME = "awesome-hw.sdsc.edu"
REMOTE_DATABASE = "postgres"
REMOTE_USER = "postgres"
REMOTE_PASSWORD = "Sdsc2018#"

# INSERT Queries
INSERT_CDC_DOCUMENTS = "INSERT INTO cdc_documents VALUES(%s, %s)"
INSERT_CDC_SENTENCES = "INSERT INTO cdc_sentence_segmentation VALUES(%s, %s, %s, %s, %s)"
INSERT_POS_ANNOTATIONS = "INSERT INTO pos_annotations VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
INSERT_LEMMA_ANNOTATIONS = "INSERT INTO lemma_annotations VALUES(%s, %s, %s, %s, %s, %s, %s)"
INSERT_DEPPARSE_ANNOTATIONS = "INSERT INTO depparse_annotations VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
INSERT_NER_ANNOTATIONS = "INSERT INTO ner_annotations VALUES(%s, %s, %s, %s, %s, %s, %s)"
INSERT_VOCABULARY = "INSERT INTO vocabulary VALUES(%s, %s)"
INSERT_HAN_ARCHIVE = "INSERT INTO han_archive VALUES(%s, %s, %s, %s, %s, %s, %s)"
INSERT_HAN_ARCHIVE = "INSERT INTO cdc_annotations VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
INSERT_ANNOTATION_TOKEN_QUERY = "INSERT INTO depparse_annotations_10 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

# SELECT Queries
SELECT_SENT_ID_FROM_CDC_SENTS = "SELECT sent_id FROM cdc_sentence_segmentation WHERE sentence_text=%s"
SELECT_DISTINCT_TOKEN_TEXT_FROM_DEPPARSE_ANNOTATIONS = "SELECT DISTINCT token_text FROM depparse_annotations"
SELECT_VOCABULARY_COUNT = "SELECT COUNT(*) FROM vocabulary"
SELECT_FROM_DEPPARSE_ANNOTATIONS = "SELECT * FROM depparse_annotations"
SELECT_FROM_NER_ANNOTATIONS = "SELECT * FROM ner_annotations WHERE doc_id=%s and sent_id=%s and token_id=%s"
SELECT_FROM_POS_ANNOTATIONS = "SELECT * FROM pos_annotations WHERE doc_id=%s and sent_id=%s and token_id=%s"
SELECT_VOCABULARY_ID = "SELECT vocabulary_id FROM vocabulary WHERE vocabulary=%s"
SELECT_SENT_ID_CONTAINING_DUP_TOKENS = "SELECT depparse_annotations_10.sent_id FROM depparse_annotations_10 WHERE dependency_relation='root' GROUP BY sent_id HAVING count(*) > 1"
SELECT_MAX_TOKEN_ID = "SELECT MAX(token_id) FROM depparse_annotations_10 WHERE sent_id = %s"
SELECT_DISTINCT_DOC_IDS_FOR_DUPLICATE_TOKENS = "SELECT DISTINCT doc_id from depparse_annotations_10 WHERE sent_id = %s and token_id = '1'"
SELECT_ANNOTATION_TOKEN_QUERY = "SELECT * FROM depparse_annotations_10 WHERE sent_id = %s and token_id = %s"

# DELETE Queries
DELETE_DUPLICATE_TOKENS_QUERY = "DELETE FROM depparse_annotations_10 WHERE sent_id=%s and token_id=%s"

# UPDATE Queries
UPDATE_QUERY = """ UPDATE pos_annotations
            SET sent_id = %s 
            WHERE sentence_id = %s"""

class Database:
    """
    Database object 

    This database object create connection and cursor instances 
    and handles database queries

    Constructor:
    hostname (string)
    databse (string)

    """

    def __init__(self, remote=False):
        if remote:
            self.conn = psycopg2.connect(dbname=REMOTE_DATABASE, user=REMOTE_USER, password=REMOTE_PASSWORD, host=REMOTE_HOST_NAME)
            self.cursor = self.conn.cursor()
        else:
            self.conn = conn = psycopg2.connect(
                host=HOST_NAME,
                database=DATABASE
            )

            self.cursor = conn.cursor()
    

    def test(self):
        self.cursor.execute(test)
        result = self.cursor.fetchall()
        print(result)

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

            self.cursor.execute(INSERT_HAN_ARCHIVE, (message_id,
                                                   title, url, message_type, publish_date, text, links))
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
            self.cursor.execute(INSERT_CDC_DOCUMENTS, doc.to_db_data())
            self.conn.commit()
            t.update(1)

        t.close()

    def insert_sentence(self, sentence):
        data = sentence.to_db_data()

        self.cursor.execute(INSERT_CDC_SENTENCES, data)
        self.conn.commit()

    def insert_lemma_annotation(self, token):
        self.cursor.execute(INSERT_LEMMA_ANNOTATIONS, token.to_lemma_data())
        self.conn.commit()

    def insert_pos_annotation(self, token):
        self.cursor.execute(INSERT_POS_ANNOTATIONS, token.to_pos_data())
        self.conn.commit()

    def insert_depparse_annotation(self, token):
        self.cursor.execute(INSERT_DEPPARSE_ANNOTATIONS, token.to_depparse_data())
        self.conn.commit()

    def insert_ner_annotation(self, token):
        self.cursor.execute(INSERT_NER_ANNOTATIONS, token.to_ner_data())
        self.conn.commit()


    def insert_annotations(self, annotation):
        self.cursor.execute(INSERT_HAN_ARCHIVE, annotation.to_db_data())
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
            self.cursor.execute(INSERT_NER_ANNOTATIONS, (row[0], self.uuid_to_bigint(
                row[1]), row[2], row[3], row[4], row[5], row[6]))
            self.conn.commit()
            t.update(1)

        t.close()

    def populate_vocabulary_table(self):
        self.cursor.execute(SELECT_DISTINCT_TOKEN_TEXT_FROM_DEPPARSE_ANNOTATIONS)
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
        self.cursor.execute(SELECT_FROM_DEPPARSE_ANNOTATIONS)
        depparse_annotations = self.cursor.fetchall()
        t = tqdm(total=len(depparse_annotations),
                 desc="Populating vocabulary Table: ")
        for depparse_annotation in depparse_annotations:
            doc_id = depparse_annotation[0]
            sent_id = depparse_annotation[1]
            token_id = depparse_annotation[2]
            token_text = depparse_annotation[3]

            data = (doc_id, sent_id, token_id)
            self.cursor.execute(SELECT_FROM_NER_ANNOTATIONS, data)
            ner_annotation = self.cursor.fetchall()[0]

            self.cursor.execute(SELECT_FROM_POS_ANNOTATIONS, data)
            pos_annotation = self.cursor.fetchall()[0]

            self.cursor.execute(SELECT_VOCABULARY_ID, (token_text, ))
            vocabulary_id = self.cursor.fetchall()[0][0]
            annotation = Annotation(
                depparse_annotation, ner_annotation, pos_annotation, vocabulary_id)
            data = annotation.to_db_data()
            self.cursor.execute(INSERT_HAN_ARCHIVE, data)
            self.conn.commit()
            t.update(1)
        t.close()

    def token_text_to_id(self, text):
        # Look up if text exists in vocabulary
        self.cursor.execute(SELECT_VOCABULARY_ID, (text, ))
        vocabulary_id = self.cursor.fetchall()
        if len(vocabulary_id) != 0:
            return vocabulary_id[0][0]
        else:
            self.cursor.execute(SELECT_VOCABULARY_COUNT)
            count = self.cursor.fetchall()[0][0]
            self.cursor.execute(INSERT_VOCABULARY, (text, count+1))
            self.conn.commit()
            return count+1

    """ 
        DB manipulations for removing duplicate tokens from annotations tbl
    """
    def find_duplicative_sentences(self):
        duplicative_sentences = []
        self.cursor.execute(SELECT_SENT_ID_CONTAINING_DUP_TOKENS)
        duplicative_sentenses_tuples = self.cursor.fetchall()
        for el in duplicative_sentenses_tuples:
            duplicative_sentences.append(el[0])
        return duplicative_sentences

    def count_distinct_tokens(self, sent_id):
        self.cursor.execute(SELECT_MAX_TOKEN_ID, (sent_id, ))
        return self.cursor.fetchall()[0][0]

    def generate_consice_doc_id(self, sent_id):
        self.cursor.execute(SELECT_DISTINCT_DOC_IDS_FOR_DUPLICATE_TOKENS, (sent_id, ))
        new_doc_id = ""
        for el in self.cursor.fetchall():
            new_doc_id += str(el[0]) + '|'
        return new_doc_id[:-1]

    def update_token(self, new_doc_id, sent_id, token_id):
        try:
            self.cursor.execute(SELECT_ANNOTATION_TOKEN_QUERY, (sent_id, token_id))
            old_token = list(self.cursor.fetchall()[0])
            old_token[0] = new_doc_id
            new_token = tuple(old_token)

            self.cursor.execute(DELETE_DUPLICATE_TOKENS_QUERY, (sent_id, token_id))
            self.conn.commit()

            self.cursor.execute(INSERT_ANNOTATION_TOKEN_QUERY, new_token)
            self.conn.commit()
        except:
            pass



    def augment_gpe_entity(self, token):
        # check fo entity type:
        if token.ner == "S-GPE":
            pass
            # case: B-GPE
                # check adjacent tokens until find E-GPE
                    # concatenate token_texts and search up city/country name in cities/countries table
                    # add table pointer to each row
            # case: S-GPE
                    # search up city/country
                    # add pointer to row
        return ""

    """
        Function:       uuid_to_bigint
        Description:    convert uuid to bigint
        Arguments:      uuid[string]
        Return:         bigint resulting from applying hash function on uuid
    """
    def uuid_to_bigint(self, uuid):
        return int(hashlib.sha256(uuid.encode('utf-8')).hexdigest(), 16) % 100**8

    def close(self):
        self.cursor.close()
        self.conn.close()
