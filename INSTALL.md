## Install environment settings

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

## Launch tests

```shell
export PYTHONPATH="./:$PYTHONPATH"
python -m pytest --cov=tests
```

## Push package to PyPi (if you have push rights)

```shell
python setup.py sdist
twine upload --repository pypi dist/*
```
