from elasticsearch import Elasticsearch

from tool.database import Data_base

import configparser

config = configparser.ConfigParser()
config.read(r"C:\DAT301m\dev_backend\data\example.ini")


class Searched:
    """A class to perform search on Elasticsearch."""

    def __init__(self):
        """Initializes the Elasticsearch connection."""
        self.es = Elasticsearch(
            cloud_id=config["ELASTIC"]["cloud_id"],
            basic_auth=(config["ELASTIC"]["user"],
                        config["ELASTIC"]["password"]),
        )
        self.index_name = "demo"

    def search(self, key_query):
        """Searches for documents in Elasticsearch that are similar
        to the given query.

        Args:
            key_query: The query to search.

        Returns:
            search_results: The search results.
        """
        a = Data_base().vector(key_query)
        nor_vector = Data_base().normalize_vector(a)
        query = {
            "script_score": {
                "query": {
                    "match_all": {}
                    },
                "script": {
                    "source": "dotProduct\
                        (params.query_vector,'vector') + 1.0",
                    "params": {"query_vector": nor_vector}
                        }
                    }
                }
        search_results = self.es.search(
            index=self.index_name, body={
                "size": 20,
                "query": query}, ignore=[400])
        return search_results

    def main(self, key_query, slider_value):
        """Performs a search on Elasticsearch and returns the formatted results.

        Args:
            key_query: The query to search.
            slider_value: The minimum score of the results to return.

        Returns:
            formatted_results: The formatted search results.
        """
        formatted_results = []
        search_results = self.search(key_query)
        search_results["hits"]["hits"].sort(key=lambda x: x["_score"],
                                            reverse=True)
        for hit in search_results["hits"]["hits"]:
            _source = hit['_source']
            _name = _source['name']
            if hit['_score']/2 > float(slider_value) is not None:
                print(f"Name image: {_name}, Score: {hit['_score']/2:.4f} ")
                id = _source['id']
                name = _source['name']
                image = _source['image']

                result = {
                    'id': id,
                    'name': name,
                    'image': image
                }
                formatted_results.append(result)
        return formatted_results
