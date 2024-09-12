# Release process

## Make sure all tests pass

```shell
export PYTHONPATH="./:$PYTHONPATH"
python -m pytest --cov=tests
```

## Update [CHANGELOG.md](CHANGELOG.md)

## Update [README.md](README.md) if needed

## Update [tutorial notebook](tutorial.ipynb) if needed, [builders notebook](docs_sources/doc_utils/builders.ipynb) if needed and update doc

```shell
python docs_sources/doc_utils/main.py
```

## Release new version of doc

```shell
mkdocs gh-deploy
```

## Update e-footprint version in [pyproject.toml](pyproject.toml)

## Update poetry dependencies

```shell
poetry update
```

## Generate latest requirements files with poetry

```shell
poetry export -f requirements.txt --without-hashes -o requirements.txt 
poetry export -f requirements.txt --without-hashes --dev -o requirements-dev.txt 
```

## Make new version commit, starting with [Vx.y.z]

## Merge main with new version commit, and publish package

```shell
poetry publish --build
```