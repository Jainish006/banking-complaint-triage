import re
import nltk 
from nltk.corpus import stopwords,wordnet
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.stem import WordNetLemmatizer


nltk.download('punkt',quiet=True)
nltk.download('punkt_tab',quiet=True)
nltk.download('stopwords',quiet=True)
nltk.download('wordnet',quiet=True)
nltk.download('omw-1.4',quiet=True)                          
nltk.download('averaged_perceptron_tagger',quiet=True)       
nltk.download('averaged_perceptron_tagger_eng',quiet=True)   


def get_wordnet_pos(tag):
    """Maps Penn Treebank POS tags to WordNet POS tags"""
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN # Default fallback to noun
    


import contractions as ct

stop_words = set(stopwords.words('english'))

negation_words = {'no','not','never','neither','nor','nothing','nowhere','nobody','cannot','without','against'}

stop_words = stop_words - negation_words
lemmatizer = WordNetLemmatizer()

def clean_preprocessed_text(text):

    text = ct.fix(text)

    # text = re.sub(r'\bnt\b', '', text)  
    
    text = re.sub(r'(\d+|X+)/(\d+|X+)/(\d+|X+|year>)','',text)

    text = re.sub(r'\{\$\d+\.\d+\}','',text)

    text = re.sub(r'X{2,}','',text)

    text = text.lower()
    
    text = re.sub(r'[\n\t]+', ' ', text)

    text = re.sub(r'[^\w\s]','',text) 

    text = re.sub(r'\s+', ' ', text).strip()

    tokens = word_tokenize(text)

    pos_tags = pos_tag(tokens)

    cleaned_tokens = []

    for word,tag in pos_tags:

        wn_tag = get_wordnet_pos(tag)

        lemma = lemmatizer.lemmatize(word,pos = wn_tag)

        if lemma not in stop_words and len(lemma) > 1 and not lemma.isnumeric():
            cleaned_tokens.append(lemma)

        
    return " ".join(cleaned_tokens)