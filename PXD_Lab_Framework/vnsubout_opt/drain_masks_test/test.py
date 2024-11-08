#!/usr/bin/env python
# coding: utf-8
import file_utils
import numpy as np


x = np.array([[1, 2], [3, 4], [5,6]])

y = np.array([3, 3, 3, 6, 6])

z = np.array([True,  True, False, False, True, True])

zp = np.reshape(z,(3, 2))

xp=x[zp]

print xp
print xp.shape


