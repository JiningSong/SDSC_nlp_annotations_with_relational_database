import psycopg2
import random

class Document:
    def __init__(self, text, doc_id=0):
        self.doc_id = doc_id
        self.text = text
    
    def to_db_data(self):
        return (
            self.doc_id, 
            self.text
        )


class Sentence:
    def __init__(self, doc_id, sentence_text, start_char, end_char):
        self.doc_id = doc_id
        self.sentence_id = random.randint(0,10**16) 
        self.sentence_text = sentence_text
        self.start_char = start_char
        self.end_char = end_char
    
    def set_sentence_id(self, sentence_id):
        self.sentence_id = sentence_id

    def to_db_data(self):
        return (
            self.doc_id,
            self.sentence_id,
            self.sentence_text,
            self.start_char,
            self.end_char
        )


class Token:
    def __init__(self, sentence, annotation_dict):
        # Common member fields (from sentence)
        self.doc_id = sentence.doc_id
        self.sentence_id = sentence.sentence_id

        # Common member fields (coreNLP pipeline on sentence)
        self.token_id = annotation_dict['token_id']
        self.token_text = annotation_dict['token_text']
        self.start_char = annotation_dict['start_char']
        self.end_char = annotation_dict['end_char']
        
        # Member fields for depparse
        self.head_id = annotation_dict['head']
        self.head_text = annotation_dict['head_text']
        self.dependency_relation = annotation_dict['dependency_relation']
        
        # Memebr fields for lemma
        self.lemma = annotation_dict['token_lemma']
        
        # Member fields for POS
        self.upos = annotation_dict['token_upos']
        self.xpos = annotation_dict['token_xpos']
        self.feats = annotation_dict['token_feats']

        # Memebr fields for NER
        self.ner = annotation_dict['ner']

    
    def to_lemma_data(self):
        return (self.doc_id, self.sentence_id, self.token_id, self.token_text, self.start_char, self.end_char, self.lemma)

    def to_pos_data(self):
        return (self.doc_id, self.sentence_id, self.token_id, self.token_text, self.start_char, self.end_char, self.upos, self.xpos, self.feats)
    
    def to_depparse_data(self):
        return (self.doc_id, self.sentence_id, self.token_id, self.token_text, self.start_char, self.end_char, self.head_id, self.head_text, self.dependency_relation)

    def to_ner_data(self):
        return (self.doc_id, self.sentence_id, self.token_id, self.token_text, self.ner, self.start_char, self.end_char)

    def to_annotations_data(self):
        return (self.doc_id, self.sentence_id, self.token_id, self.token_text, self.start_char, self.end_char, self.head_id, self.head_text, self.dependency_relation, self.ner, self.upos, self.xpos, self.feats)

    def to_annotation(self, db):
        return Annotation(self, db)
        
class Annotation:
    def __init__(self, depparse_annotation, ner_annotation, pos_annotation, vocabulary_id):

        self.doc_id = depparse_annotation[0]
        self.sentence_id = depparse_annotation[1]
        self.token_id = depparse_annotation[2]
        self.token_text_id = vocabulary_id
        self.start_char = depparse_annotation[4]
        self.end_char = depparse_annotation[5]
        self.head_id = depparse_annotation[6]
        self.head_text = depparse_annotation[7]
        self.dependency_relation = depparse_annotation[8]
        self.entity_type = ner_annotation[4]
        self.upos = pos_annotation[6]
        self.xpos = pos_annotation[7]
        self.feats = pos_annotation[8]

    def __init__(self, token, db):
        self.doc_id = token.doc_id
        self.sentence_id = token.sentence_id
        self.token_id = token.token_id
        self.token_text_id = db.token_text_to_id(token.token_text)
        self.start_char = token.start_char
        self.end_char = token.end_char
        self.head_id = token.head_id
        self.head_text = token.head_text
        self.dependency_relation = token.dependency_relation
        self.entity_type = token.ner
        self.upos = token.upos
        self.xpos = token.xpos
        self.feats = token.feats
        self.appendix = db.augment_gpe_entity(token)


    def to_db_data(self):
        return (
            self.doc_id,
            self.sentence_id,
            self.token_id,
            self.token_text_id,
            self.start_char,
            self.end_char,
            self.head_id,
            self.head_text,
            self.dependency_relation,
            self.entity_type,
            self.upos,
            self.xpos,
            self.feats,
            self.appendix
        )