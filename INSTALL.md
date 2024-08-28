## Install environment settings

### With poetry (recommended)

For installing poetry and command line auto-complete, see [this documentation](https://python-poetry.org/docs/). Then you can do:

```shell
poetry install --with dev
poetry run ipython
Python 3.10.6 (main, Mar 10 2023, 10:55:28) [GCC 11.3.0]
Type 'copyright', 'credits' or 'license' for more information
IPython 8.18.1 -- An enhanced Interactive Python. Type '?' for help.
In [1]: import efootprint
...
```

Every `poetry run` command will use python virtual env.

If you want to be "inside" the virtual env you can type `poetry shell`.

## Launch tests

```shell
export PYTHONPATH="./:$PYTHONPATH"
poetry run python -m pytest --cov=tests
```

## Distributing to pypi
If you have a pypi API token with push right to the efootprint package: 

```shell
poetry config pypi-token.pypi ${YOUR_API_TOKEN}
poetry publish --build
```

for testing on test-pypi:

```shell
poetry config repositories.test-pypi https://test.pypi.org/legacy/
poetry config pypi-token.test-pypi ${YOUR_API_TOKEN}
poetry publish --build -r test-pypi
# then inside your virtualenv
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ efootprint
```

## Generating requirements files

You can generate `requirements.txt` and `requirements-dev.txt` from `pyproject.toml` and poetry with:

```shell
poetry export -f requirements.txt --without-hashes -o requirements.txt 
poetry export -f requirements.txt --without-hashes --dev -o requirements-dev.txt 
```

### With Conda
Here is an example using conda as an env manager (but you could use other env manager as pyvenv or
virtualenvwrapper):

```
conda create -n e-footprint python=3.11.2
conda activate e-footprint
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Optionally, if you want to use jupyter notebooks during the development process:

```
conda install ipykernel jupyter
python -m ipykernel install --user --name=e-footprint
```

If you have trouble managing the python versions on your laptop you can check out [pyenv](https://github.com/pyenv/pyenv) and also manage your virtual environments with [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)