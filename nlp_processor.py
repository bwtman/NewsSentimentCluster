import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')

stop_words = set(stopwords.words('english'))
sia = SentimentIntensityAnalyzer()

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    return [t for t in tokens if t.isalnum() and t not in stop_words]

def get_sentiment(text):
    preprocessed_text = ' '.join(preprocess_text(text))
    return sia.polarity_scores(preprocessed_text)