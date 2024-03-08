import unittest
from nbconvert import PythonExporter
from nbformat import read
import os


def run_notebook(notebook_path):
    notebook = read(notebook_path, as_version=4)
    exporter = PythonExporter()

    # Execute the notebook and collect the output
    python_code, _ = exporter.from_notebook_node(notebook)

    exec(python_code)


class TestQuickstart(unittest.TestCase):
    def test_quickstart(self):
        run_notebook(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "quickstart.ipynb"))
