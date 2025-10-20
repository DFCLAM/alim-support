import re

def detox(filename : str):
    return re.sub(r'[^0-9A-Za-z_\-]', '_', filename)
    pass