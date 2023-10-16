## Install environment settings

We only use conda as an env manager (but you could use other env manager as venv or
virtualenvwrapper) and pip as a package manager.

```
conda create -n footprint-model python=3.11.2
conda activate footprint-model
conda install ipykernel jupyter
pip install -r requirements.txt
python -m ipykernel install --user --name=footprint-model
```

If you have trouble managing the python versions on your laptop you can check out [pyenv](https://github.com/pyenv/pyenv) and also manage your virtual environments with [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)

## add your workdir in python path, launch tests and main

To execute main.py at the root of the project
```shell
export PYTHONPATH="./:$PYTHONPATH"
python -m pytest tests
python use_cases.first_use_case.py
```
