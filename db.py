import psycopg2
import json
from nlp_pipelines import *


def insert_docs_to_db(conn, cursor, documents):
    """
    Insert documents to database 

    Raw document texts are inserted to raw_text table. coreNLP tools are executed
    on these texts and the corresponding results are stored in seperate Annotation
    databases.Uuid is generatated autamatically for each document and used as 
    foreign key for each annotation table.

    Parameters:
    cursor (psycopg2 Cursor): pointer to db 
    documents (list): list of documents to be inserted to db


    """
    # Insert query strings
    raw_table_insert_query = "INSERT INTO raw_text(text) VALUES(%s)"
    sentence_segmentation_query = "INSERT INTO sentence_segmentation VALUES(%s, %s)"
    pos_query = "INSERT INTO pos_and_morphological_annotations VALUES(%s, %s)"
    lemma_query = "INSERT INTO lemma_annotations VALUES(%s, %s)"
    depparse_query = "INSERT INTO syntactic_dependency_annotations VALUES(%s, %s)"
    ner_query = "INSERT INTO ner_annotations VALUES(%s, %s)"

    for document in documents:
        # Insert original text to raw_text table
        raw_table_insert_data = (document, )
        cursor.execute(raw_table_insert_query, raw_table_insert_data)
        conn.commit()

        # Get UUID of the recent entry
        uuid_select_query = "SELECT text_id FROM raw_text WHERE text=%s"
        uuid_select_data = raw_table_insert_data
        cursor.execute(uuid_select_query, uuid_select_data)
        result = cursor.fetchall()
        uuid = result[0][0]

        # Get nlp annotations from stanford coreNLP pipeline
        sent_segmentations, pos_annotations, lemma_annotations, depparse_annotations, ner_annotations = annotate_document(document)

        # Create data for each insert query
        sent_segmentation_data = (uuid, sent_segmentations)
        pos_annotations_data = (uuid, pos_annotations)
        lemma_annotations_data = (uuid, lemma_annotations)
        depparse_annotations_data = (uuid, depparse_annotations)
        ner_annotations_data = (uuid, ner_annotations)

        # Insert each annotations to coresponding tables
        cursor.execute(sentence_segmentation_query, sent_segmentation_data)
        cursor.execute(pos_query, pos_annotations_data)
        cursor.execute(lemma_query, lemma_annotations_data)
        cursor.execute(depparse_query, depparse_annotations_data)
        cursor.execute(ner_query, ner_annotations_data)
        conn.commit()

 

        



if __name__ == "__main__":
    SAMPLE_Document_1 = "This\'s a \"test\" sentence for stanze. This is another sentence."
    SAMPLE_Document_2 = "Barack Hussein Obama II is an American politician and attorney who served as the 44th president of the United States from 2009 to 2017. "
    SAMPLE_Document_3 = "5G is the fifth generation of wireless communications technologies supporting cellular data networks."
    documents = [SAMPLE_Document_1, SAMPLE_Document_2, SAMPLE_Document_3]
    
    # Connect to db
    HOST_NAME = "localhost"
    DATABASE = "stanford_corenlp_results"
    conn = psycopg2.connect(
        host = HOST_NAME,
        database = DATABASE
    )

    # Declare cursor
    cursor = conn.cursor()

    # Insert documents to db
    insert_docs_to_db(conn, cursor, documents)
    
    # Close cursor and db connection
    cursor.close()
    conn.close()


