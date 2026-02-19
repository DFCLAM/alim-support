from env import *
from pathlib import Path
import mariadb
import re
from xml.etree import ElementTree
from saxonche import PySaxonProcessor

def generate_documents():
  connection_properties = {
          'user' : MARIADB_ALIM_PHP7_USER,
          'password' : MARIADB_ALIM_PHP7_PSW,
          'host' : MARIADB_ALIM_PHP7_HOST,
          'port' : int(MARIADB_ALIM_PHP7_PORT),
          'database' : MARIADB_ALIM_PHP7_DB
  }

  processor = PySaxonProcessor()
  xslt_processor = processor.new_xslt30_processor()
  executable = xslt_processor.compile_stylesheet(stylesheet_file = TEI_STYLESHEETS_BASE_PATH + '/txt/tei-to-text.xsl')

  # print (connection_properties)
  query = '''
  -- The query use windows functions to get the last version of each book with not empty XML
  WITH agora_book_version_last AS (
    SELECT DISTINCT id, MAX(version) OVER (PARTITION BY id) AS max_version FROM agora_book_version WHERE length(n7tra_xml_content) > 0
  )
  SELECT
    b1.id
  , b1.title
  , b1.author
  , b1.is_document
  , b1.consistenza
  , b1.metadata
  , b1.n7tra_xml_content 
  FROM agora_book_version b1
  JOIN agora_book_version_last b2 ON b2.id = b1.id AND b2.max_version = b1.version
  -- WHERE b1.id = 13147
  LIMIT 100
  '''
  with mariadb.connect(**connection_properties) as conn:
      with conn.cursor() as cur:
          cur.execute(query)
          for (id, title, author, is_document, consistenza, metadata, xml) in cur:
              xml = bytes(xml,"utf-8").decode("utf-8-sig") # Remove UTF BOM, avoiding "Content is not allowed in prolog" error during XML parsing
              document = processor.parse_xml(xml_text = xml)
              text = executable.transform_to_string(xdm_node = document)
              yield {
                  'id' : id,
                  'title' : title,
                  'author' : author,
                  'is_document' : is_document,
                  'consistenza' : consistenza,
                  'metadata' : metadata,
                  'xml' : xml,
                  'xml_obj' : ElementTree.fromstring(xml),
                  'text' : text
              }

find_words_re = re.compile(r'(parole|words)\s*:\s*(\d+)', re.IGNORECASE)
find_characters_re = re.compile(r'(caratteri|characters)[^:]*:\s*(\d+)', re.IGNORECASE)
def measure(text : str, xml_obj : ElementTree.Element, consistenza : str, metadata : str):
    
    # Get measures from TEI if any
    declared_words : str = None
    declared_measure_characters_without_spaces : str = None
    declared_measure_characters_unspecified : str = None
    measure_words = xml_obj.find(".//{http://www.tei-c.org/ns/1.0}measure[@unit='words']")
    measure_characters_without_spaces = xml_obj.find(".//{http://www.tei-c.org/ns/1.0}measure[@unit='characters_without_spaces']")
    if ElementTree.iselement(measure_words) and ElementTree.iselement(measure_characters_without_spaces):
        declared_words = int(measure_words.attrib['quantity'])
        declared_measure_characters_without_spaces = int(measure_characters_without_spaces.attrib['quantity'])
    
    # Get measures from "consistenza" if any
    if not declared_words and consistenza:
        match = find_words_re.search(consistenza)
        if match:
            declared_words = int(match.group(2))
    if consistenza:
        match = find_characters_re.search(consistenza)
        if match:
            declared_measure_characters_unspecified = int(match.group(2))
    
    # Get measures from "metadata" if any
    if not declared_words and metadata:
        match = find_words_re.search(metadata)
        if match:
            declared_words = int(match.group(2))
    if not declared_measure_characters_unspecified and metadata:
        match = find_characters_re.search(metadata)
        if match:
            declared_measure_characters_unspecified = int(match.group(2))
    
    # Calculate measures from text
    # Simplest way of tokenization using split
    tokens = text.strip().split()
    calculated_words = len(tokens)
    calculated_characters_without_spaces = 0
    for token in tokens:
        calculated_characters_without_spaces += len(token)

    return {
        'declared_words' : declared_words,
        'declared_measure_characters_without_spaces' : declared_measure_characters_without_spaces,
        'declared_measure_characters_unspecified' : declared_measure_characters_unspecified,
        'calculated_words' : calculated_words,
        'calculated_characters_without_spaces' : calculated_characters_without_spaces
    }

for result in generate_documents():
    print('\n##########################################################################################')
    print(result['id'], result['title'])
    print(measure(result['text'], result['xml_obj'], result['consistenza'], result['metadata']))
