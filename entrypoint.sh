#!/bin/sh

source /venv/bin/activate
cd /app
exec /venv/bin/python $@
