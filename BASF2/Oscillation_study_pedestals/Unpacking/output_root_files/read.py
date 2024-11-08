#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from basf2 import *

from basf2 import Module

main = create_path()

simpleinput = register_module('RootInput')
simpleinput.param('inputFileName', 'H60rawframe_data.root')

main.add_module(simpleinput)


process(main)
