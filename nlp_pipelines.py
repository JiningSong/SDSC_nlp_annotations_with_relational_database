import stanza
import json
import string


SAMPLE_SENTENCE = "This is a test sentence for stanze. "
SAMPLE_SENTENCES = "This is a test sentence for stanze. This is another sentence."
SAMPLE_SENTENCE_NER = "Chris Manning teaches at Stanford University. He lives in the Bay Area."
DATA_FILE = "/Users/jining/Projects/FMP/stanford_core_nlp_demo/newsExample.csv"

def generate_document(text):
    tokeniser = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse, ner', logging_level='WARN')
    return tokeniser(text)


# Generate sent_segmentation result
def annotate_document(document):

    # Store list of segmented sentences
    sent_segmentations = []

    # start character of last sentence
    sentence_start_char = 0

    for sent in document.sentences:
        sent_segmentation = {}
        sent_segmentation['start_char'] = sent.tokens[0].start_char
        sent_segmentation['end_char'] = sent.tokens[-1].end_char
        
        sent_segmentation['sentence_text'] = ""

        #Store token dicts in sent_segmentation dictionary as a list of dicts
        sent_segmentation['tokens'] = []        
        for token in sent.tokens:
            if token.text in string.punctuation:
                sent_segmentation['sentence_text'] += token.text
            else:
                sent_segmentation['sentence_text'] += ' ' + token.text

            # Store token_dict
            token_dict = {}
            token_dict['token_id'] = token.id
            token_dict['token_text'] = token.text
            token_dict['start_char'] = token.start_char - sentence_start_char
            token_dict['end_char'] = token.end_char - sentence_start_char
            token_dict['ner'] = token.ner
         
            token_lemma = ""
            token_upos = ""
            token_xpos = ""
            token_feats = ""
            
            for word in token.words:
                if word.lemma:
                    token_lemma += word.lemma + ' '
                if word.upos:
                    token_upos += word.upos + ' '
                if word.xpos:
                    token_xpos = word.xpos + ' '
                if word.feats:
                    token_feats = word.feats + ' '

            token_dict['token_lemma'] = token_lemma[:-1]
            token_dict['token_upos'] = token_upos[:-1]
            token_dict['token_xpos'] = token_xpos[:-1]
            token_dict['token_feats'] = token_feats[:-1]


            if len(token.words) == 1:
                token_dict["head"] = token.words[0].head
                if token.words[0].head > 0:
                    token_dict["head_text"] = sent.words[word.head-1].text
                else:
                    token_dict["head_text"] = "root"
                token_dict["dependency_relation"] = token.words[0].deprel
            
            sent_segmentation['tokens'].append(token_dict)

        sentence_start_char = sent.tokens[-1].end_char+1

        sent_segmentation['sentence_text'] = sent_segmentation['sentence_text'][1:]
        sent_segmentations.append(sent_segmentation)
        
    return sent_segmentations