#! /bin/bash

# These vars are now set in .flaskenv and Flask uses
# the 'python-dotenv' library to grab those values
#export FLASK_APP=microblog.py
#export FLASK_ENV=development

DEBUG_FLAG=1
HOST_NAME='0.0.0.0'
PORT_NUM=3000

while getopts d:h:p: flag
do
    case "${flag}" in
        d) DEBUG_FLAG=${OPTARG};;
        h) HOST_NAME=${OPTARG};;
        p) PORT_NUM=${OPTARG};;
    esac
done

#export MAIL_SERVER=localhost
#export MAIL_PORT=8025

export FLASK_DEBUG=$DEBUG_FLAG
flask run --host $HOST_NAME --port $PORT_NUM
