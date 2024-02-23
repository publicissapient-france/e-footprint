
La convention de nommage est la date (pour l'ordre), les initiales du créateur, 
et une description, e.g. `20-04-09 VV plot tests`.
## Plugin JupyTEXT
Nous utilisons le plugin [JupyTEXT](https://github.com/mwouts/jupytext) pour versionner les notebooks. 
Commande pour lancer Jupyter correctement configuré 
source venv/bin/activate
cd /builders/usage
./jupyter.sh
Ouvrir indifférement les fichiers `.ipynb` ou `.py` appairés.
Pour créer un fichier python avec le contenu du notebook : 
python - m jupytext --set-formats ipynb,py:percent notebook.ipynb 
### Pourquoi ce plugin ?
Les fichiers bruts des notebooks Jupyter (extension `.ipynb`) contiennent les résultats des calculs.
Ces résultats sont potentiellement sensibles, il faut donc éviter de les versionner.
JupyTEXT permet de sauvegarder le contenu des notebooks, sans ces sorties, dans un fichier python (extension `.py`). 
Ces fichiers peuvent être versionnés sans risque. 
De plus la différence entre 2 versions successives (`git diff`) est exploitable pour suivre l'évolution du code,
ce qui n'est pas le cas pour le format d'origine `.ipynb`.
Enfin, ces fichiers peuvent être rééxecutés facilement s'ils produisent des résultats, 
par exemple `python 001-decouverte_données.py`.
Pour versionner un notebook *avec* ses sorties, par exemple s'il sert de rapport, préférer un export `pdf` ou `html`.

### Dépannage
Parfois, l'un des 2 fichiers `.ipynb` et `.py` est modifié en dehors de Jupyter + JupyTEXT, via git ou une édition directe. 
*Problème* : Les fichiers ne sont alors plus compatibles, ce qui créé une erreur à l'ouverture. 
*Solution* : Supprimer (ou déplacer ailleurs par sécurité) l'un des deux fichiers. 