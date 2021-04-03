#! /usr/bin/env python

import traceback

from game import main

try:
    main.main()
except Exception as e:
    with open("errors.log", "a+") as logfile:
        traceback.print_tb(e.__traceback__, file=logfile)
        logfile.write(f"{e.__class__.__name__}\n")
    raise e
