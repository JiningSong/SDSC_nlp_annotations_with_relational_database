import stanza
import string
import spacy


DATA_FILE = "/Users/jining/Projects/FMP/stanford_core_nlp_demo/newsExample.csv"


def annotate_document_spacy(text, nlp):
    doc = nlp(text)

    annotated_sentences = []
    for sent in doc.sents:
        annotated_sentence = {}
        annotated_sentence['start_char'] = sent.start_char
        annotated_sentence['end_char'] = sent.end_char
        annotated_sentence['sentence_text'] = sent.text
        annotated_sentence['tokens'] = [] 

        tokens = doc[sent.start:sent.end]
        for token in tokens:
            token_dict = {}
            token_dict['token_id'] = token.i - sent.start
            token_dict['doc_token_id'] = token.i
            token_dict['token_text'] = token.text
            token_dict['start_char'] = token.idx - sent.start_char
            token_dict['end_char'] = token.idx + len(token.text) - sent.start_char
            token_dict['ner'] = token.ent_type_
            if token_dict['ner'] == '':
                token_dict['ner'] = 'O'
            token_dict['token_upos'] = token.pos_
            token_dict['token_xpos'] = token.tag_

            head = token.head

            token_dict['head'] = head.i - sent.start
            token_dict['head_text'] = head.text
            token_dict['dependency_relation'] = token.dep_

            if token_dict['dependency_relation'] == 'ROOT' and token_dict['head_text'] == token_dict['token_text']:
                token_dict['head-text'] = "root"
            annotated_sentence['tokens'].append(token_dict)
        annotated_sentences.append(annotated_sentence)

    return annotated_sentences
# Generate annotated_sentence result
def annotate_document_corenlp(text):
    tokeniser = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse, ner', logging_level='WARN')
    document = tokeniser(text)

    # Store list of segmented sentences
    annotated_sentences = []

    # start character of last sentence
    sentence_start_char = 0

    # keep track of doc-wise token_id by recording token_id at end of (last) sentence + token_id in current sentence
    eos_doc_token_id = 0

    for sent in document.sentences:

        # store info about sentence into annotated_sentence dict
        annotated_sentence = {}
        annotated_sentence['start_char'] = sent.tokens[0].start_char
        annotated_sentence['end_char'] = sent.tokens[-1].end_char
        
        # sentence_text is obtained by concatenating tokens text within the sentence
        annotated_sentence['sentence_text'] = ""

        #Store list of token dicts (containing info about each token) in annotated_sentence dictionary 
        annotated_sentence['tokens'] = []        
        for token in sent.tokens:
            if token.text in string.punctuation:
                annotated_sentence['sentence_text'] += token.text
            else:
                annotated_sentence['sentence_text'] += ' ' + token.text

            # token_id, text, start_char, end_char, ner are obtained directly from token's member field
            token_dict = {}
            token_dict['token_id'] = token.id[0] 
            token_dict['doc_token_id'] = token.id[0] + eos_doc_token_id
            token_dict['token_text'] = token.text
            token_dict['start_char'] = token.start_char - sentence_start_char
            token_dict['end_char'] = token.end_char - sentence_start_char
            token_dict['ner'] = token.ner
         

            # lemma, upos, xpos, feats are stored under the words field in token; needs an additional loop to grab them
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

            # store lemma, upos, xpos, feats in the same token dict for each token
            token_dict['token_lemma'] = token_lemma[:-1]
            token_dict['token_upos'] = token_upos[:-1]
            token_dict['token_xpos'] = token_xpos[:-1]

            # head_text and dependency_relation of token in in dependency_relation tree are obtained by tracing back through head_id 
            if len(token.words) == 1:
                token_dict["head"] = token.words[0].head
                if token.words[0].head > 0:
                    token_dict["head_text"] = sent.words[word.head-1].text
                else:
                    token_dict["head_text"] = "root"
                token_dict["dependency_relation"] = token.words[0].deprel
            
            annotated_sentence['tokens'].append(token_dict)

        # update sentence_start_char for next sentence
        sentence_start_char = sent.tokens[-1].end_char+1

        # trim out last char (extra space) for concatenated sentence_text
        annotated_sentence['sentence_text'] = annotated_sentence['sentence_text'][1:]
        annotated_sentences.append(annotated_sentence)
        eos_doc_token_id = annotated_sentence['tokens'][-1]['doc_token_id']
    return annotated_sentences