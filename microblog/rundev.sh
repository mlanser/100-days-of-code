#! /bin/bash

# These vars are now set in .flaskenv and Flask uses
# the 'python-dotenv' library to grab those values
#export FLASK_APP=microblog.py
#export FLASK_ENV=development
flask run --host 0.0.0.0 --port 3000
