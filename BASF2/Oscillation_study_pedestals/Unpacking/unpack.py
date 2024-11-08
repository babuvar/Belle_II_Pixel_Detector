#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from basf2 import *

from basf2 import Module

main = create_path()

rawinput = register_module('PXDReadRawBonnDAQ')

rawinput.param('FileName', 'H60rawframe_data.dat')
rawinput.param('ExpNr', 0)
rawinput.param('RunNr', 14)


main.add_module(rawinput)

unpacker = register_module('PXDUnpacker')
unpacker.param('FormatBonnDAQ', True)

main.add_module(unpacker)

simpleoutput = register_module('RootOutput')
simpleoutput.param('outputFileName', 'H60rawframe_data.root')
simpleoutput.param('compressionLevel', 0)

main.add_module(simpleoutput)

process(main)
