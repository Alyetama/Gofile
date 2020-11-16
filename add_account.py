#!/usr/bin/env python
# coding: utf-8

import os


def add_account():
    ans = input('Add an email address (y/n)? ')
    if ans.lower() == 'y':
        email_addr = input('Email Address: ')

        with open('gofile.py') as f:
            
            with open('gofile_.py', 'w') as f2:
                for num, line in enumerate(f):
                    if num == 22:
                        f2.write(f"    email_addr = '{email_addr}'\n")
                    else:
                        f2.write(line)

        os.remove('gofile.py')
        os.rename('gofile_.py', 'gofile.py')


if __name__ == '__main__':
    add_account()
