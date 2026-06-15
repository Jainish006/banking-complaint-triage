
CATEGORY_MODEL_PATH = 'model/lr_category_full.pkl'
CATEGORY_VECTORIZER_PATH = 'model/tfidf_category_full.pkl'


CATEGORIES = [
    'Banking & Accounts',
    'Cards & Transactions', 
    'Credit Reporting',
    'Debt Collection',
    'Loans',
    'Money Transfer & Payments'
]


URGENCY_LEVELS = ['Critical', 'High', 'Medium', 'Low']


TFIDF_MAX_FEATURES = 100000
TFIDF_NGRAM_RANGE = (1, 2)
TFIDF_MIN_DF = 5