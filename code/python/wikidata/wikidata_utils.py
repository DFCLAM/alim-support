import requests

def wd_query(sparql: str):
    """Issues a query against WikiData

    Parameters
    ----------
    sparql: str
        the query

    Returns 
    -------
    request.Response
        The WikiData response to the SPRQL query, in JSON format.
    """
    return requests.get('https://query.wikidata.org/sparql', params = {'format': 'json', 'query': sparql})
