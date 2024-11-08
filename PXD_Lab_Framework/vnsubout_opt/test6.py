#!/usr/bin/env python
# coding:utf8

import os
from epics_utils import pvlist_get, pvname


#pvlist=['PXD:B:config-H1011:device_config:VALUE:set','PXD:B:config-H1011:device_module:VALUE:set']

pvlist=[]
dhes = ['H1011','H1021','H1022','H1032']
user = 'PXD'

for dhe in dhes:
    pvlist.append('%s:B:config-%s:device_config:VALUE:set' % (user,dhe))
    pvlist.append('%s:B:config-%s:device_module:VALUE:set' % (user,dhe))
    pvlist.append('%s:B:config-%s:module_type:VALUE:set' % (user,dhe))
pvlist.append('%s:B:config-commitid' %user)

#print pvlist


results = pvlist_get(pvlist)
#print results

results_format={}


for first, second in results:
    results_format[first]=[second, True]

print results_format


