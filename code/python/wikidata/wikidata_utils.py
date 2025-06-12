import requests

def wd_query(sprql: str):
    """Issues a query against WikiData

    Returns 
    -------
    request.Response
        The WikiData response to the SPRQL query, in JSON format.
    """
    return requests.get('https://query.wikidata.org/sparql', params = {'format': 'json', 'query': sprql})