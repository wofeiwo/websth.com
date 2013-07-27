#!/bin/sh

cd /home/www/vh0sts/www.websth.com
gunicorn -c scripts/gunicorn.py app:app