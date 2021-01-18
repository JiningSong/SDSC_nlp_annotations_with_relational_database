import psycopg2
import pandas as pd
from tqdm import tqdm

# DB Queries:
COUNT_DUP_DOC = "SELECT COUNT(*) FROM {doc_tbl_name} WHERE text=%s"
INSERT_DOCUMENTS = "INSERT INTO {doc_tbl_name} VALUES(%s, %s)"
INSERT_SENTENCES = "INSERT INTO {sent_tbl_name} VALUES(%s, %s, %s, %s, %s)"
INSERT_ANNOTATIONS = "INSERT INTO {annotation_tbl_name} VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

class Database:
    """
    Database object 

    This database object create connection and cursor instances 
    and handles database queries

    """
    def __init__(self, db_configs, table_names):
        self.conn = psycopg2.connect(
            host=db_configs["HOST_NAME"],
            dbname=db_configs["DB_NAME"], 
            user=db_configs["USER"],
            password=db_configs["PASSWORD"])

        self.cursor = self.conn.cursor()
        self.doc_tbl = table_names["DOC_TBL"]
        self.sent_tbl = table_names["SENT_TBL"]
        self.annotation_tbl = table_names["ANNOTATION_TBL"]


    def insert_documents(self, documents, accept_duplicate_doc):
        documents_count = len(documents)
        t = tqdm(total=documents_count, desc="Populating Documents Table: ")

        i = 0
        while (i < len(documents)):
            if accept_duplicate_doc == False:
                self.cursor.execute(COUNT_DUP_DOC.format(doc_tbl_name = self.doc_tbl), (documents[i].text, ))
                dup_count = self.cursor.fetchall()[0][0]

                # skip current document if same document exists in db already
                if dup_count:
                    documents.remove(documents[i])
                    t.update(1)
                    continue

            # insert otherwise
            self.cursor.execute(INSERT_DOCUMENTS.format(doc_tbl_name = self.doc_tbl), documents[i].to_db_data())
            self.conn.commit()
            i += 1
            t.update(1)
        t.close()
        return documents

    def insert_sentence(self, sentence):
        data = sentence.to_db_data()
        self.cursor.execute(INSERT_SENTENCES.format(sent_tbl_name = self.sent_tbl), data)
        self.conn.commit()


    def insert_annotations(self, token):
        self.cursor.execute(INSERT_ANNOTATIONS.format(annotation_tbl_name = self.annotation_tbl), token.to_db_data())
        self.conn.commit()


    def close(self):
        self.cursor.close()
        self.conn.close()
