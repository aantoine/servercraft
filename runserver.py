#!/usr/bin/python
# -*- coding: utf-8 -*-
from test.config import install_if_required
from test.utils import get_args
from test.models import create_tables
from test.views import *

if __name__ == '__main__':
    args = get_args()
    create_tables()
    install_if_required()
    auth.load()
    app.run(threaded=True, debug=args.debug, host=args.host, port=args.port)
