import os

file_path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(file_path, "tutorial.md"), "r") as file:
    tutorial = file.read()

tutorial_reformated = tutorial.replace("```python\n\n```", "")

tutorial_reformated = tutorial_reformated.replace(
    'print("PLACEHOLDER_SYSTEM_FOOTPRINTS")\n```\n\n    PLACEHOLDER_SYSTEM_FOOTPRINTS',
    '```\n--8<-- "docs_sources/mkdocs_sourcefiles/System footprints.html"')

tutorial_reformated = tutorial_reformated.replace(
    'print("PLACEHOLDER_OBJECT_RELATIONSHIPS")\n```\n\n    ../mkdocs_sourcefiles/object_relationships_graph.html\n    PLACEHOLDER_OBJECT_RELATIONSHIPS',
    '```\n--8<-- "docs_sources/mkdocs_sourcefiles/object_relationships_graph.html"'
)

tutorial_reformated = tutorial_reformated.replace(
    'print("PLACEHOLDER_CALCULUS_GRAPH")\n```\n\n    ../mkdocs_sourcefiles/device_population_fab_footprint_calculus_graph.html\n    PLACEHOLDER_CALCULUS_GRAPH',
    '```\n--8<-- "docs_sources/mkdocs_sourcefiles/device_population_fab_footprint_calculus_graph.html"'
)

tutorial_reformated = tutorial_reformated.replace("notebook=False", "notebook=True")

tutorial_reformated = tutorial_reformated.replace("../mkdocs_sourcefiles/", "")

with open(os.path.join(file_path, "..", "mkdocs_sourcefiles", "tutorial_reformated.md"), "w") as file:
    file.write(tutorial_reformated)
