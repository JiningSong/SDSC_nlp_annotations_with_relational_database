import stanza 

# Download pretrained models in Stanza
stanza.download('en')
stanza_nlp = stanza.Pipeline('en')
