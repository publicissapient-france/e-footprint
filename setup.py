from setuptools import setup, find_packages
import os
import codecs


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name="efootprint",
    version=get_version(os.path.join("efootprint", "__init__.py")),
    author="Vincent Villet for Publicis Sapient",
    author_email="vincent.villet@gmail.com",
    description="Digital service environmental footprint model",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/publicissapient-france/e-footprint",
    packages=find_packages(exclude="tests"),
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    # TODO: Remove matplotlib from requirements to save bandwidth as usage grows ?
    install_requires=read('requirements.txt').split('\n'),
    include_package_data=True
)
