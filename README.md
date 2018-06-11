# Profiles.Freeside.co.uk

[![Build Status](https://ci.freeside.co.uk/api/badges/FreesideHull/Profiles.Freeside.co.uk/status.svg)](https://ci.freeside.co.uk/FreesideHull/Profiles.Freeside.co.uk)

Flask app to register IPA accounts for Freeside users

# Setting up dev enviroment
Requirements: Python3
```
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
FLASK_APP=main:app flask db upgrade
FLASK_APP=main:app flask run
```

Running inside docker.
```
docker build -t freesidehull/profiles .
docker run --env-file ./deploy/env.list --name=profiles -v "$(pwd)/data":/usr/src/app/data freesidehull/profiles
```
