from functools import cached_property
import os
from typing import Any
import spacy
import numpy as np
from numpy.typing import NDArray
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.core.config import settings
import joblib
from src.libs.log import logger


class VectorizerNotFound(Exception):
    """Raised when the vectorizer not found is disk."""


class Vectorizer:
    UNWANTED_PIPES = ["ner", "parser"]

    def __init__(self):
        self.nlp = spacy.load('en_core_web_md')

    def _tokenizer(self, doc) -> list:
        with self.nlp.disable_pipes(*self.UNWANTED_PIPES):
            return [
                t.lemma_ for t in self.nlp(doc) 
                if not t.is_punct and not t.is_space and t.is_alpha
            ]

    def _check_model_directory(self) -> None:
        if not os.path.isdir(f'{settings.MODEL_DIR}'):
            os.makedirs(settings.MODEL_DIR, 0o777, exist_ok=True)

    @cached_property
    def _load_vectorizer(self) -> TfidfVectorizer:
        """Load vectorizer from disk."""
        self._check_model_directory()
        filename = f'{settings.MODEL_DIR}/vectorizer.gz'
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"Vectorizer not found at {filename}")
        return joblib.load(filename)

    @cached_property
    def _load_features(self) -> Any:
        """Load features from disk."""
        self._check_model_directory()
        filename = f'{settings.MODEL_DIR}/features.gz'
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"Features not found at {filename}")
        return joblib.load(filename)
    
    def _save_vectorizer(self, vectorizer: TfidfVectorizer) -> None:
        """Save the vectorizer to disk."""
        self._check_model_directory()
        joblib.dump(vectorizer, filename=f'{settings.MODEL_DIR}/vectorizer.gz')

    def _save_features(self, features: Any) -> None:
        """Save the features to disk."""
        self._check_model_directory()
        joblib.dump(features, filename=f'{settings.MODEL_DIR}/features.gz')

    def train(self, documents: list[str]) -> TfidfVectorizer:
        """Fit transform and store the new vectorizer."""
        vectorizer = TfidfVectorizer(tokenizer=self._tokenizer)
        features = vectorizer.fit_transform(documents)
        self._save_vectorizer(vectorizer)
        self._save_features(features)
        return vectorizer

    def sort_search_result(self, result, limit: int) -> NDArray:
        """Sort the """
        kth_largest = (limit + 1) * -1
        return np.argsort(result)[:kth_largest:-1]

    def search(self, query: str, limit: int = 10) -> NDArray:
        """Search for similar documents to the given query."""
        
        try:
           vectorizer = self._load_vectorizer
           features = self._load_features
        except FileNotFoundError as error:
            logger.error("Vectorizer not found.")
            raise VectorizerNotFound from error

        query_vector = vectorizer.transform([query])
        cosine_similarities = cosine_similarity(features, query_vector).flatten()
        search_result = self.sort_search_result(cosine_similarities, limit)
        
        return search_result
