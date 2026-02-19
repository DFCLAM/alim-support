from env import *
from pathlib import Path
import mariadb
from saxonche import PySaxonProcessor

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
, b1.n7tra_xml_content 
FROM agora_book_version b1
JOIN agora_book_version_last b2 ON b2.id = b1.id AND b2.max_version = b1.version
LIMIT 10
'''
with mariadb.connect(**connection_properties) as conn:
    with conn.cursor() as cur:
        cur.execute(query)
        for (id, title, author, xml) in cur:
            print('\n######################################################################')
            print (id, title, author)
            print('---')
            xml = bytes(xml,"utf-8").decode("utf-8-sig") # Remove UTF BOM, avoiding "Content is not allowed in prolog" error during XML parsing
            document = processor.parse_xml(xml_text = xml)
            output = executable.transform_to_string(xdm_node = document)
            print(output)
