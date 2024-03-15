from docs_sources.doc_utils.format_tutorial_md import efootprint_tutorial_to_md, \
    format_tutorial_and_save_to_mkdocs_sourcefiles
from docs_sources.doc_utils.generate_object_reference import generate_object_reference

print("Converting e-footprint tutorial to markdown")
md_doc_tuto_path = efootprint_tutorial_to_md()
print("Reformating markdown tutorial file and saving it to mkdocs_sourcefiles")
format_tutorial_and_save_to_mkdocs_sourcefiles(md_doc_tuto_path)
print("Generating object reference")
generate_object_reference()
