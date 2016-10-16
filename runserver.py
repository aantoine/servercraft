#!/usr/bin/python
# -*- coding: utf-8 -*-
from test.config import install_if_required
from test.models import create_tables
from test.views import *

if __name__ == '__main__':
    create_tables()
    install_if_required()
    auth.load()
    app.run(threaded=True)
