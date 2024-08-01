
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from .qdrant_db import QdrantEndPoint
from .tokenizer import SpacyTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

##### Retrieved Item #####
class RetrievedItem(BaseModel):
    id: Union[int, str]
    score: float
    content: str

class QdrantItem(RetrievedItem):
    payload: Dict[str, Any]
    vector: List[float]

    # Use Pydantic's validator or root_validator if necessary for complex validations

    @property
    def tokens(self) -> int:
        # This assumes you're counting tokens in the "Content" field of the payload
        # If "Content" isn't guaranteed to be a string, ensure conversion or validation
        return len(self.payload.get("Content", "").split())
    
    @property
    def PageNumber(self) -> int:
        return self.payload.get("PageNumber", 0)

    @property
    def FileName(self) -> str:
        return self.payload.get("FileName", "")

    @property
    def FileURL(self) -> str:
        return self.payload.get("FileURL", "")

    # Override the constructor to set the 'content' field from the payload if needed
    def __init__(self, **data):
        if 'payload' in data:
            content = data['payload'].get("Content", "")
            data.update({"content": content})
        super().__init__(**data)
    
##### Retrieval #####
class Retrieval(ABC):
    """
    An abstract class Retrieval is defined here
    it is used to define the interface for retrieval models
    all retrieval models should inherit from this class
    """
    @abstractmethod
    def __init__(self, *args, **kwargs):
        self.MAX_SOURCE_TOKENS = kwargs.get("MAX_SOURCE_TOKENS", 5000 ) # 10_000

    @abstractmethod
    def search(self, query, k=10):
        raise NotImplementedError

    def format_sources(self, items: List[RetrievedItem], num_selected=1) -> str:
        # Sort the results based on match_count in descending order and return the best result;
        # if there are multiple results with the same match_count, randomly select one of them.
        assert num_selected == 1, "Only support formatting one best document"
        sorted_results = self.rank(items)
        return sorted_results[0].content
    
    def filter_documents(self, documents: List[RetrievedItem]) -> List[RetrievedItem]:
        sorted_documents = self.rank(documents)
        filtered_docs = []
        tokens = 0
        for q in sorted_documents:
            if tokens + q.tokens <= self.MAX_SOURCE_TOKENS:
                filtered_docs.append(q)
                tokens += q.tokens
            else:
                break
        return filtered_docs
    
    def rank(self, documents: List[RetrievedItem]) -> List[RetrievedItem]:
        """ Sort in descending order from highest to lowest score"""
        return sorted(documents, key=lambda x: x.score, reverse=True)

##### Qdrant #####
def format_markdown_url( url: str):
    return url.replace(" ", "%20").replace("(", "%28").replace(")", "%29")

def litm_reordering(documents: List[RetrievedItem]) -> List[RetrievedItem]:
    sorted_documents = sorted(documents, key=lambda q: q.score)
    even_docs = sorted_documents[::2]
    odd_docs = sorted_documents[1::2]
    return even_docs[::-1] + odd_docs

class Qdrant(Retrieval):
    def __init__(self):
        """ qdrant is a vector search engine
        """
        super().__init__()

    def search(self, query, k=10) -> List[QdrantItem]:
        """ search for a query in qdrant

        Args:
            query (str): the query to search for
            k (int, optional): the number of results to return. Defaults to 10.

        Returns:
            List[QdrantItem]: a list of QdrantItems
        """
        qdrant_request = QdrantEndPoint(query=query, limit=k)
        response = qdrant_request.get_response()

        # parse a response
        assert not 400 <= response.status_code < 500
        
        # status, response_time, and result in items (each item contains key-value pairs for 'id', 'score', 'payload', 'vector'; ignoring 'version')
        # status=content["status"]
        # response_time=content["time"]
        items = []
        for item in response["result"]:
            item = {key: item[key] for key in ['id', 'score', 'payload', 'vector'] if key in item}
            items.append(QdrantItem(**item))

        return items
    
    def format_sources(self, items: List[QdrantItem]) -> str:
        processed_docs = self.filter_documents(items)
        # processed_docs = litm_reordering(processed_docs)
        for item in processed_docs:
            formatted_source = f"\n[{item.FileName}]({format_markdown_url(item.FileURL)}):\n{item.Content}\n"
            formatted_sources += formatted_source
        return formatted_sources

##### Keyword Matching #####
class KeywordMatching(Retrieval):
    def __init__(self, documents):
        """
        Initializes the KeywordMatching model with an index of documents.
        
        :param index: A dictionary with document IDs as keys and document texts as values.
        """
        super().__init__()
        self.tokenizer = SpacyTokenizer()
        self.documents = documents
        
    def search(self, query, k=None):
        """
        Performs a keyword-based search on the index using the given query.
        
        :param query: The search query as a string.
        :param k: The number of top matching documents to return.
        :return: A list of tuples (doc_id, match_count) sorted by match_count in descending order.
        """
        query_keywords = set(self.tokenizer.tokenize(query))
        items = []
        
        for doc_id, doc_text in self.documents.items():
            doc_words = set(self.tokenizer.tokenize(doc_text))
            match_count = len(query_keywords.intersection(doc_words))
            if match_count > 0:
                items += [RetrievedItem(id=doc_id, score=match_count, content=doc_text)]

        return self.rank(items)[:k]

##### TF-IDF #####
class TfidfRetrieval(Retrieval):
    def __init__(self, documents):
        super().__init__()
        self.documents = documents
        self.vectorizer = TfidfVectorizer()
        self.doc_vectors = self.vectorizer.fit_transform([doc.content for doc in documents])

    def search(self, query, k=None):
        query_vec = self.vectorizer.transform([query])
        cosine_similarities = linear_kernel(query_vec, self.doc_vectors).flatten()
        items = []
        for idx, score in enumerate(cosine_similarities):
            items.append(RetrievedItem(id=self.documents[idx].id, score=score, content=self.documents[idx].content))

        if k is None:
            k = len(items)
        return self.ranked_items[:k]
