import pathlib

# initialize common local paths for data input and output results

# the directory the epistolae's repo (https://github.com/DFCLAM/epistolae-hugo or https://github.com/ccnmtl/epistolae-hugo) is cloned to
epistolae_base_path = pathlib.Path.home().joinpath('tmp/epistolae')
epistolae_base_path = pathlib.Path(input("Epistolae path (defaults to %s): " % str(epistolae_base_path)) or str(epistolae_base_path))
if not epistolae_base_path.is_dir():
    raise  FileNotFoundError(epistolae_base_path)

epistolae_letters_path = epistolae_base_path.joinpath('content/letter')
epistolae_women_path = epistolae_base_path.joinpath('content/woman')
epistolae_people_path = epistolae_base_path.joinpath('content/people')

for testee_path in (epistolae_letters_path, epistolae_women_path, epistolae_people_path):
    if not testee_path.is_dir():
        raise FileNotFoundError(testee_path)
    
# the directory where results (TEI files) will be generated
output_base_path = pathlib.Path.home().joinpath('tmp/epistolae-alim')
output_base_path = pathlib.Path(input("Epistolae path (defaults to %s): " % str(output_base_path)) or str(output_base_path))
if not output_base_path.is_dir():
    raise FileNotFoundError(output_base_path)
