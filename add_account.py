#!/usr/bin/env python3
# coding: utf-8

from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove


email = input('Email address: ')
fh, abs_path = mkstemp()
with fdopen(fh, 'w') as new_file:
    with open('gofile.py') as old_file:
        for line in old_file:
            new_file.write(line.replace('NONE', email))
copymode('gofile.py', abs_path)
remove('gofile.py')
move(abs_path, 'gofile.py')
