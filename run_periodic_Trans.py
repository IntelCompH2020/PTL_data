# -*- coding: utf-8 -*-
"""
Main program for importing databases for use with projects from the PTL

Created on Jul 4, 2018

@author:    Jerónimo Arenas García
            (based on code from jcid)

"""


from __future__ import print_function    # For python 2 compatibility
import os
import platform
import time
import runFECYTscripts


time_delay = 3600 #Runs every our

for n in range(38):
    print(n)
    #cmd = 'python runFECYTscripts.py --resetDB'
    #os.system(cmd)
    runFECYTscripts.main()

    #time.sleep(time_delay)
