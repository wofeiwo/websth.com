#!/bin/bash

sudo kill -HUP `cat /home/www/run/gunicorn.pid`
