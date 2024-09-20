import os

from docs_sources.doc_utils.format_builders_md import format_builders_ipynb_to_md_and_save_to_mkdocs_sourcefiles
from docs_sources.doc_utils.format_tutorial_md import efootprint_tutorial_to_md, \
    format_tutorial_and_save_to_mkdocs_sourcefiles
from docs_sources.doc_utils.generate_object_reference import generate_object_reference

file_path = os.path.dirname(os.path.abspath(__file__))

print("Converting e-footprint tutorial to markdown")
md_doc_tuto_path = efootprint_tutorial_to_md()
print("Reformating markdown tutorial file and saving it to mkdocs_sourcefiles")
format_tutorial_and_save_to_mkdocs_sourcefiles(md_doc_tuto_path)
print("Formating builders.ipynb to md and saving it to mkdocs_sourcefiles")
format_builders_ipynb_to_md_and_save_to_mkdocs_sourcefiles()
print("Generating object reference")
generate_object_reference()

with open(os.path.join(file_path, "..", "..", "CHANGELOG.md"), "r") as file:
    changelog = file.read()

changelog = changelog.replace("./", "https://github.com/Boavizta/e-footprint/tree/main/")

with open(os.path.join("..", "mkdocs_sourcefiles", "Changelog.md"), "w") as file:
    file.write(changelog)