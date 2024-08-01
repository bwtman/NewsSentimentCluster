from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter
import spacy

nlp = spacy.load("en_core_web_sm")