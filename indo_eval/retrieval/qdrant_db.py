from typing import Any, Dict, List, Optional
import requests
from indo_eval.retrieval.embed import get_query_embedding
from typing import Any, Dict, List, Optional
import requests
import json
import os

class QdrantEndPoint:
    collection_name = ""
    QDRANT_API_BASE = os.environ.get('QDRANT_API_BASE') 
    WITH_PAYLOAD = True
    QDRANT_TIMEOUT_SECONDS = 30
    HEADERS = {
        "Content-Type": "application/json",
        "api-key": os.environ.get('QDRANT_API_KEY') 
    }

    def __init__(self, query: Optional[str] = None, limit: int = None):
    
        self.vector = get_query_embedding(query) if query else None
        self.limit = limit
        self.must = []
        self.should = []
        self.must_not = []
        self.grouped = False
        self.group_by_field = None
        self.group_size = None

    def group_by(self, field: str, group_size: int = 1) -> 'QdrantRequest':
        self.group_by_field = field
        self.group_size = group_size
        self.grouped = True
        return self
    
    @property
    def endpoint(self) -> str:
        """
        change endpoint based on whether or not its grouped
        """
        # Note: not sure how to use index just yet
        if self.grouped:
            return self.QDRANT_API_BASE + "points/search/groups"
        else:
            return self.QDRANT_API_BASE + "points/search"

    def match(self, key: str, must=None, should=None, must_not=None) -> 'QdrantRequest':
        if must:
            self.must.append({"key": key, "match": {"value": must}})
        if should:
            self.should.append({"key": key, "match": {"value": should}})
        if must_not:
            self.must_not.append({"key": key, "match": {"value": should}})
        return self

    def _format_data(self) -> dict:
        data = {
            "vector": self.vector, # the query vector
            "limit": self.limit, # the number of matches to return
            "with_payload": self.WITH_PAYLOAD # payload: the data associated with the vector
        }
        if self.grouped:
            data["group_by"] = self.group_by_field
            data["group_size"] = self.group_size
        return data

    def get_response(self) -> dict:
        # send a post request to the endpoint
        response = requests.post(
            self.endpoint,
            headers=self.HEADERS,
            json=self._format_data(),
            timeout=self.QDRANT_TIMEOUT_SECONDS
        )
        return response.json()

    
   
        


if __name__ == "__main__":
    query = "Display the name, location, and status for a project that has the same name as Carlton Innovation Precinct"
    response = qdrant_search_items(query)
    print(response.top_urls(3))
    # save to json
    import json
    with open('data.json', 'w') as fp:
        json.dump(response, fp)
