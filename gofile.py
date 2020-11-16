#!/usr/bin/env python
# coding: utf-8

import subprocess
import ast
import pyperclip
from rich.panel import Panel
from rich import print as rich_print
from platform import platform
import argparse


def gofile():
    def curl_response(command):
        server = subprocess.check_output(command)
        server = server.decode('UTF-8')
        server = ast.literal_eval(server)
        return server

    parser = argparse.ArgumentParser(
        description='Simple file upload: gofile -f <file_path>')
    parser.add_argument('-f',
                        '--file',
                        help='path to the file you want to upload')
    parser.add_argument('-o',
                        '--open',
                        help='open the link when the file upload is completed',
                        action='store_true')
    args = parser.parse_args()

    server = curl_response(['curl', '-s', 'https://apiv2.gofile.io/getServer'])
    server = server['data']['server']

    try:
        res = curl_response([
            'curl', '-F', f'file=@{args.file}',
            f'https://{server}.gofile.io/uploadFile'
        ])
        code = res['data']['code']

        url = f'https://gofile.io/d/{code}'

        pyperclip.copy(url)

        rich_print(Panel.fit(f'[blue]{url}    [red]Copied!'))

        if 'macOS' in platform() and args.open is True:
            subprocess.call(['open', f'{url}'])

    except:
        rich_print('[red]Something went wrong! Try again.')


if __name__ == '__main__':
    gofile()
