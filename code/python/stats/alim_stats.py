from env import *
from pathlib import Path
import mariadb
import csv
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
  WHERE NOT b1.alim_plus
  -- WHERE b1.id = 13147
  -- LIMIT 200
  '''
  with mariadb.connect(**connection_properties) as conn:
      with conn.cursor() as cur:
          cur.execute(query)
          for (id, title, author, is_document, consistenza, metadata, xml) in cur:
              xml = bytes(xml,"utf-8").decode("utf-8-sig") # Remove UTF BOM, avoiding "Content is not allowed in prolog" error during XML parsing
              try:
                  document = processor.parse_xml(xml_text = xml)
              except Exception as e:
                  print ('ERRORE!!!')
                  print (title)
                  print (author)
                  print ('https://alim.unisi.it/dl/resource/' + str(id))
                  print ('---')
                  print (e)
                  print ('\n')
                  continue
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
    declared_characters_without_spaces : str = None
    declared_characters_unspecified : str = None
    measure_words = xml_obj.find(".//{http://www.tei-c.org/ns/1.0}measure[@unit='words']")
    measure_characters_without_spaces = xml_obj.find(".//{http://www.tei-c.org/ns/1.0}measure[@unit='characters_without_spaces']")
    if ElementTree.iselement(measure_words) and ElementTree.iselement(measure_characters_without_spaces):
        if measure_words.attrib['quantity'] and measure_words.attrib['quantity'].isnumeric():
            declared_words = int(measure_words.attrib['quantity'])
        if measure_characters_without_spaces.attrib['quantity'] and measure_characters_without_spaces.attrib['quantity'].isnumeric():
            declared_characters_without_spaces = int(measure_characters_without_spaces.attrib['quantity'])
    
    # Get measures from "consistenza" if any
    if not declared_words and consistenza:
        match = find_words_re.search(consistenza)
        if match:
            declared_words = int(match.group(2))
    if consistenza:
        match = find_characters_re.search(consistenza)
        if match:
            declared_characters_unspecified = int(match.group(2))
    
    # Get measures from "metadata" if any
    if not declared_words and metadata:
        match = find_words_re.search(metadata)
        if match:
            declared_words = int(match.group(2))
    if not declared_characters_unspecified and metadata:
        match = find_characters_re.search(metadata)
        if match:
            declared_characters_unspecified = int(match.group(2))
    
    # Calculate measures from text
    # Simplest way of tokenization using split
    tokens = text.strip().split()
    calculated_words = len(tokens)
    calculated_characters_without_spaces = 0
    for token in tokens:
        calculated_characters_without_spaces += len(token)

    return {
        'declared_words' : declared_words,
        'declared_characters_without_spaces' : declared_characters_without_spaces,
        'declared_characters_unspecified' : declared_characters_unspecified,
        'calculated_words' : calculated_words,
        'calculated_characters_without_spaces' : calculated_characters_without_spaces
    }

csv_books_path = Path(ALIM_STATS_OUTPUT_BASE_PATH + '/books.csv')
csv_documents_path = Path(ALIM_STATS_OUTPUT_BASE_PATH + '/documents.csv')
csv_stats_path = Path(ALIM_STATS_OUTPUT_BASE_PATH + '/stats.csv')
containers = {    
  'books' : list(),
  'documents' : list()
}
totals = {
  'books' : {
      'count' : 0,
      'words' : 0,
      'chars' : 0
  },
  'documents' : {
      'count' : 0,
      'words' : 0,
      'chars' : 0      
  }
}
fieldnames = ['id','url','title','author','calculated_words','declared_words','calculated_characters_without_spaces','declared_characters_without_spaces','declared_characters_unspecified']

for result in generate_documents():
    # print('\n##########################################################################################')
    # print(result['id'], result['title'])
    # print(measure(result['text'], result['xml_obj'], result['consistenza'], result['metadata']))
    key = 'documents' if result['is_document'] else 'books'
    result = result | measure(result['text'], result['xml_obj'], result['consistenza'], result['metadata'])
    result['url'] = 'https://alim.unisi.it/dl/resource/' + str(result['id'])
    containers[key].append({k: v for k, v in result.items() if k in fieldnames})
    totals[key]['count'] += 1
    totals[key]['words'] += result['calculated_words']
    totals[key]['chars'] += result['calculated_characters_without_spaces']

with csv_books_path.open('w') as csv_books_fp:
    writer = csv.DictWriter(csv_books_fp, fieldnames = fieldnames)
    writer.writeheader()
    writer.writerows(sorted(containers['books'], key = lambda row : row['title']))
with csv_documents_path.open('w') as csv_documents_fp:
    writer = csv.DictWriter(csv_documents_fp, fieldnames = fieldnames)
    writer.writeheader()
    writer.writerows(sorted(containers['documents'], key = lambda row : row['title']))
with csv_stats_path.open('w') as csv_stats_fp:
    writer = csv.DictWriter(csv_stats_fp, fieldnames = ['TYPE','NUMBER_OF_DOCUMENTS','WORDS','CHARACTERS_WITHOUT_SPACES'])
    writer.writeheader()
    writer.writerow({
        'TYPE' : 'Opere',
        'NUMBER_OF_DOCUMENTS' : totals['books']['count'],
        'WORDS' : totals['books']['words'],
        'CHARACTERS_WITHOUT_SPACES' : totals['books']['chars']
    })
    writer.writerow({
        'TYPE' : 'Fonti documentarie',
        'NUMBER_OF_DOCUMENTS' : totals['documents']['count'],
        'WORDS' : totals['documents']['words'],
        'CHARACTERS_WITHOUT_SPACES' : totals['documents']['chars']
    })
    writer.writerow({
        'TYPE' : 'Tutti',
        'NUMBER_OF_DOCUMENTS' : totals['books']['count'] + totals['documents']['count'],
        'WORDS' : totals['books']['words'] + totals['documents']['words'],
        'CHARACTERS_WITHOUT_SPACES' : totals['books']['chars'] + totals['documents']['chars']
    })


