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
    return requests.get('https://query.wikidata.org/sparql', params = {'format': 'json', 'query': sparql}, headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'})
