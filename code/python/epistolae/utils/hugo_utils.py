import pathlib
import yaml

def read_hugo_front_matter(path: pathlib.Path):
    """Generator function that extract the Hugo's front matter line by line

    The generator iterates over all the lines included
    between the '---' separators. The separators itself
    are not included.

    Parameters
    ----------
    path : pathlib.Path
        the path of the hugo file containing a front matter
    """
    for line in path:
        if line.startswith('---'):
            for line in path:
                if line.startswith('---'):
                    return
                yield line

def read_hugo_body(path: pathlib.Path):
    """Generator function that extract the Hugo's body line by line

    The generator iterates over all the lines included
    below the second '---' separators. The separators itself
    are not included.

    Parameters
    ----------
    path : pathlib.Path
        the path of the hugo file containing a front matter
    """
    for line in path:
        if line.startswith('---'):
            for line in path:
                if line.startswith('---'):
                    break
            for line in path:
                yield line

def parse_hugo_front_matter(path: pathlib.Path):
    """Parse the YML front matter of the hugo files
    
    Returns
    -------
    An object containg all the front matter tree
    """
    with path.open('r') as file:
        return yaml.load(''.join(read_hugo_front_matter(file)), Loader=yaml.Loader)
    
def get_hugo_body(path: pathlib.Path):
    """Return the body of the hugo files
    
    Returns
    -------
    A string with the body
    """
    with path.open('r') as file:
        return ''.join(read_hugo_body(file))
    
