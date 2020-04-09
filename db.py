import psycopg2
import json
from nlp_pipelines import *
from models import *
from utils import *


# path to sample data file
DATA_FILE = "/Users/jining/Projects/FMP/stanford_core_nlp_demo/newsExample.sm.csv"

# Insert query strings
DOCUMENTS_QUERY = "INSERT INTO documents VALUES(%s, %s)"
SENT_SEGMENTATION_QUERY = "INSERT INTO sentence_segmentation(doc_id, sentence_text, start_char, end_char) VALUES(%s, %s, %s, %s)"
POS_QUERY = "INSERT INTO pos_and_morphological_annotations VALUES(%s, %s)"
LEMMA_QUERY = "INSERT INTO lemma_annotations VALUES(%s, %s)"
DEPPARSE_QUERY = "INSERT INTO syntactic_dependency_annotations VALUES(%s, %s)"
NER_QUERY = "INSERT INTO ner_annotations VALUES(%s, %s)"
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
        for doc in documents:
            self.cursor.execute(DOCUMENTS_QUERY, doc.to_db_data())
            self.conn.commit()

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

    def close(self):
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":

    # Connect to db
    HOST_NAME = "localhost"
    DATABASE = "stanford_corenlp_results"
    db = Database(HOST_NAME, DATABASE)

    # read in documents from data file
    documents_list = read_csv(DATA_FILE)

    # generate documents object
    documents = create_documents(documents_list)
    # Insert documents to db
    db.insert_documents(documents)

    # Annotate documents and create sentence objects
    annotated_sents = []
    for doc in documents:
        annotated_text = annotate_text(doc.text)
        sent_segmentations = generate_sent_segmentations(annotated_text)
        
        for el in sent_segmentations:
            annotate_sent = Sentence(doc.doc_id, el['sentence_text'], el['start_char'], el['end_char'])
            
            #insert sentence to db and save generated uuid in sentence object
            uuid = db.insert_sentence(annotate_sent)
            annotate_sent.set_sentence_id(uuid)

            annotated_sents.append(annotate_sent)
    for sent in annotated_sents:
        print(sent.sentence_id)
    # Close db connection
    db.close()



# def insert_docs_to_db(conn, cursor, DATA_FILE):
#     """
#     Insert documents to database 

#     Raw document texts are inserted to raw_text table. coreNLP tools are executed
#     on these texts and the corresponding results are stored in seperate Annotation
#     databases.Uuid is generatated autamatically for each document and used as 
#     foreign key for each annotation table.

#     Parameters:
#     cursor (psycopg2 Cursor): pointer to db 
#     documents (list): list of documents to be inserted to db


#     """

#     # Insert query strings
#     documents_query = "INSERT INTO documents VALUES(%s, %s)"
#     sentence_segmentation_query = "INSERT INTO sentence_segmentation VALUES(%s, %s)"
#     pos_query = "INSERT INTO pos_and_morphological_annotations VALUES(%s, %s)"
#     lemma_query = "INSERT INTO lemma_annotations VALUES(%s, %s)"
#     depparse_query = "INSERT INTO syntactic_dependency_annotations VALUES(%s, %s)"
#     ner_query = "INSERT INTO ner_annotations VALUES(%s, %s)"


#     for doc in documents:
#         document = Document(doc[0], doc[1])
#         cursor.execute(documents_query, document.to_db_data())
#         conn.commit()
#         # data = (doc[1], doc[0])
#         # cursor.execute(documents_query, data)
#         # conn.commit()
        

    # for document in documents:
    #     # Insert original text to raw_text table
    #     raw_table_insert_data = (document, )
    #     cursor.execute(raw_table_insert_query, raw_table_insert_data)
    #     conn.commit()

    #     # Get UUID of the recent entry
    #     uuid_select_query = "SELECT text_id FROM raw_text WHERE text=%s"
    #     uuid_select_data = raw_table_insert_data
    #     cursor.execute(uuid_select_query, uuid_select_data)
    #     result = cursor.fetchall()
    #     uuid = result[0][0]

    #     # Get nlp annotations from stanford coreNLP pipeline
    #     sent_segmentations, pos_annotations, lemma_annotations, depparse_annotations, ner_annotations = annotate_document(document)

    #     # Create data for each insert query
    #     sent_segmentation_data = (uuid, sent_segmentations)
    #     pos_annotations_data = (uuid, pos_annotations)
    #     lemma_annotations_data = (uuid, lemma_annotations)
    #     depparse_annotations_data = (uuid, depparse_annotations)
    #     ner_annotations_data = (uuid, ner_annotations)

    #     # Insert each annotations to coresponding tables
    #     cursor.execute(sentence_segmentation_query, sent_segmentation_data)
    #     cursor.execute(pos_query, pos_annotations_data)
    #     cursor.execute(lemma_query, lemma_annotations_data)
    #     cursor.execute(depparse_query, depparse_annotations_data)
    #     cursor.execute(ner_query, ner_annotations_data)
    #     conn.commit()

 
