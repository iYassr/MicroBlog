#! /usr/bin/env bash

export FLASK_APP=application.py

export FLASK_ENV=development

if [ -z "$1" ]
then
flask run -p 9999
else
flask run -p $1
fi

