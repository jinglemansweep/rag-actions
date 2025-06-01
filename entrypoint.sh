#!/bin/sh

. /venv/bin/activate
cd /app
exec /venv/bin/python $@
