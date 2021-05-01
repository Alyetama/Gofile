#!/usr/bin/env python3
# coding: utf-8

import subprocess
import ast
import pyperclip
import argparse
from rich.panel import Panel
from rich import print
from platform import platform
from os import path
from glob import glob
from rich.progress import track


def gofile():
    def curl_response(command):
        server = subprocess.check_output(command)
        server = server.decode('UTF-8')
        server = ast.literal_eval(server)
        return server

    email_addr = 'NONE'

    parser = argparse.ArgumentParser(
        description='Example: gofile -f <file_path>')
    parser.add_argument('-f',
                        '--file',
                        help='path to the file/folder you want to upload')
    parser.add_argument('-o',
                        '--open',
                        help='open the link when the file upload is completed (doesn\'t work when uploading a folder)',
                        action='store_true')
    parser.add_argument('-H',
                        '--headless',
                        help='Add this flag if you\'re on a headless machine or don\'t have access to clipboard',
                        action='store_true')
    args = parser.parse_args()

    # server = curl_response(['curl', '-s', 'https://apiv2.gofile.io/getServer'])
    # server = server['data']['server']

    for X in [1, 2, 4, 5, 6]:
        try:
            if path.isdir(args.file):
                files = [x for x in glob(f'{args.file}/**/*', recursive = True) if path.isfile(x)]
                links = []

                for file in track(files, description='[blue]Uploading...'):
                    res = curl_response(['curl', '-s', '-F', f'email={email_addr}', '-F', f'file=@{file}',
                        f'https://srv-store{X}.gofile.io/uploadFile'
                    ])
                    code = res['data']['code']
                    url = f'https://gofile.io/d/{code}'
                    links.append(url)

                files_list = '\n'.join(x for x in links)
                if args.headless is not True:
                    pyperclip.copy(files_list)
                print(Panel.fit(f'[blue]{files_list}\n[red]Copied!'))

                break


            if path.isfile(args.file):
                res = curl_response(['curl', '-F', f'email={email_addr}', '-F', f'file=@{args.file}',
                    f'https://srv-store{X}.gofile.io/uploadFile'
                ])
                code = res['data']['code']
                url = f'https://gofile.io/d/{code}'
                if args.headless is not True:
                    pyperclip.copy(url)
                    copied = '[red]Copied!'
                else:
                    copied = ''
                print(Panel.fit(f'[blue]{url}    {copied}'))

                if 'macOS' in platform() and args.open is True:
                    subprocess.call(['open', f'{url}'])

                break

        except KeyError:
            print('Are you trying to use the program on a headless machine? Add the flag "-H" to your command.')
            break

        except Exception as e:
            print('[red]Error:', e)
            print('Trying the next server...')


if __name__ == '__main__':
    gofile()
