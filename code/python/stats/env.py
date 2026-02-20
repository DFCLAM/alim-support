import os
from pathlib import Path

# ALIM DB (local copy)
MARIADB_ALIM_PHP7_HOST = os.getenv('MARIADB_ALIM_PHP7_HOST', '127.0.0.1')
MARIADB_ALIM_PHP7_PORT = os.getenv('MARIADB_ALIM_PHP7_PORT', '3307')
MARIADB_ALIM_PHP7_DB = os.getenv('MARIADB_ALIM_PHP7_DB', 'alim_php7')
MARIADB_ALIM_PHP7_USER = os.getenv('MARIADB_ALIM_PHP7_USER', 'root')
MARIADB_ALIM_PHP7_PSW = os.getenv('MARIADB_ALIM_PHP7_PSW', None) # Call . read-passwords.sh

# Base path of the TEI official Stylesheets - https://github.com/TEIC/Stylesheets
TEI_STYLESHEETS_BASE_PATH = os.getenv('TEI_STYLESHEETS_BASE_PATH', str(Path.home()) + '/Development/git/TEI-Stylesheets')

# JSON files produced by epistolae/letters_to_tei/main.py
EPISTOLAE_LETTERS_BASE_PATH = os.getenv('EPISTOLAE_LETTERS_BASE_PATH', str(Path.home()) + '/tmp/epistolae-alim/letters')

# Output paths
ALIM_STATS_OUTPUT_BASE_PATH = os.getenv('ALIM_STATS_OUTPUT_BASE_PATH', str(Path.home()) + '/tmp/alim-support/stats/output')


