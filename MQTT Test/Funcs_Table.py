"""
Script that stores a dictionary of functions used in subscribe.py
Functions are of consistent format, taking a string parameter to parse and use
Functions are added in external scripts with the init() function for consistency
Table obtained using "from Funcs_Table import FunctionTable"
"""
import Funcs_Motor
import Funcs_Sound

FunctionTable = dict()
Funcs_Motor.init(FunctionTable)
Funcs_Sound.init(FunctionTable)