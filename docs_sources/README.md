# Serving docs locally

    mkdocs serve

# Building docs

    python docs_sources/doc_utils/generate_docs.py
    # Execute tutorial.ipynb, save it then
    jupyter nbconvert --to markdown tutorial.ipynb
    python docs_sources/doc_utils/format_tutorial_md.py
    mkdocs build -d docs

# Deploying on github pages

    mkdocs gh-deploy