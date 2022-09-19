from typing import Optional, Type, TypeVar
from urllib.parse import quote_plus

import pydantic
import requests

from . import schema

S = TypeVar("S", bound=pydantic.BaseModel, covariant=True)


class OlsClient:
    """
    Client for communicating with an OLS instance.
    """

    base_url: str

    def __init__(self, base_url: str):
        """
        :param base_url: Base API URL for the OLS instance
        """
        if not base_url.endswith("/"):
            base_url = base_url + "/"
        self.base_url = base_url
        self._session = requests.Session()
        self._session.headers = {"accept": "application/json"}
        # TODO: do we need to set access-control-allow-origin header?

    def _create_url(self, path: str) -> str:
        # Remove leading /
        path = path.lstrip("/")
        return self.base_url + path

    @staticmethod
    def _quote_iri(iri: str) -> str:
        """
        Quote an IRI as a double URL-encoded URL string, so it can
        be used in a URL path
        :param iri: IRI, e.g. http://purl.obolibrary.org/obo/GO_0043226
        :return: Percent-encoded string, e.g. http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FGO_0043226
        """
        return quote_plus(quote_plus(iri))

    def get(self, path: str, params: Optional[dict] = None) -> dict:
        """
        Perform a GET request to the API.

        :param path: API path (excluding base url)
        :param params: Query parametersgg
        :return: JSON data, as a dict
        """
        url = self._create_url(path)
        resp = self._session.get(url=url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_with_schema(
        self, schema: Type[S], path: str, params: Optional[dict] = None
    ) -> S:
        """
        Get data from ``path`` and parse it with ``schema`` to return
        a pydantic object.

        :param schema: Pydantic class/model inheriting from BaseModel
        :param path: API path (excluding the base API url)
        :param params: Query parameters
        :return: Pydantic model instance created from ``schema``
        :raises: ``pydantic.ValidationError`` if response data fails
           to validate.
        """
        resp = self.get(path=path, params=params)
        obj = schema(**resp)
        return obj

    def get_ontologies(self) -> schema.OntologyList:
        ontology_list = self.get_with_schema(schema.OntologyList, "/ontologies")
        return ontology_list

    def get_ontology(self, ontology_id: str) -> schema.OntologyItem:
        path = f"/ontologies/{ontology_id}/"
        ontology_item = self.get_with_schema(schema.OntologyItem, path)
        return ontology_item
