#!/usr/bin/env python3
# coding: utf-8

import subprocess
import ast
import argparse
from rich.panel import Panel
from rich import print
from platform import platform
from glob import glob
from rich.progress import track
from pathlib import Path
import json
import pyshorteners


def gofile():
    
    def curl_response(command):
        server = subprocess.check_output(command)
        server = server.decode('UTF-8')
        server = ast.literal_eval(server)
        return server

    email_addr = 'NONE'
    s = pyshorteners.Shortener(domain='https://ttm.sh')

    parser = argparse.ArgumentParser(
        description='Example: gofile -f <file_path>',
        epilog='Tip: if you\'re plan to download the links you generated from the command line, use `$ curl -LOJ <direct_link>` to preserve the original file name.')
    parser.add_argument('-f',
                        '--file',
                        help='Path to the file/folder you want to upload')
    parser.add_argument('-o',
                        '--open',
                        help='Open the link when the file upload is completed (doesn\'t work on folders) (macOS support only).',
                        action='store_true')
    parser.add_argument('-e',
                        '--export',
                        help='Export file URLs as a JSON file when the input is a folder.',
                        action='store_true')
    args = parser.parse_args()

    # server = curl_response(['curl', '-s', 'https://apiv2.gofile.io/getServer'])
    # server = server['data']['server']

    for X in [1, 2, 4, 5, 6]:
        try:
            if Path(args.file).is_dir():
                files = [x for x in glob(f'{args.file}/**/*', recursive = True) if path.isfile(x)]
                data = {}

                for file in track(files, description='[blue]Uploading...'):
                    res = curl_response(['curl', '-s', '-F', f'email={email_addr}', '-F', f'file=@{file}',
                        f'https://srv-store{X}.gofile.io/uploadFile'
                    ])
                    name = Path(file).name
                    url = res['data']['downloadPage']
                    o_direct_link = res['data']['directLink']
                    direct_link = s.nullpointer.short(res['data']['directLink'])

                    print(Panel.fit(f'[yellow]File:[/yellow] [blue]{name}[/blue]\n' +
                    f'[yellow]Download page:[/yellow] [blue]{url}[/blue]\n' +
                    f'[yellow]Direct link:[/yellow] [blue]{direct_link}[/blue]\n'))

                    if args.export is True:
                        data[name] = {
                        'DownloadPage': url,
                        'DirectLink': o_direct_link
                        }

                with open(f'{Path(args.file).name}.json', 'w') as f:
                    json.dump(data, f, indent=4)
                    print(f'[green]Exported links to:[/green] [magenta]{args.file}.json[/magenta]')
                break


            if Path(args.file).is_file():
                res = curl_response(['curl', '-F', f'email={email_addr}', '-F', f'file=@{args.file}',
                    f'https://srv-store{X}.gofile.io/uploadFile'
                ])
                url = res['data']['downloadPage']
                direct_link = s.nullpointer.short(res['data']['directLink'])
                
                print(Panel.fit(f'[yellow]File:[/yellow] [blue]{Path(args.file).name}[/blue]\n' +
                    f'[yellow]Download page:[/yellow] [blue]{url}[/blue]\n' +
                    f'[yellow]Direct link:[/yellow] [blue]{direct_link}[/blue]'))

                if 'macOS' in platform() and args.open is True:
                    subprocess.call(['open', f'{url}'])

                break

        except Exception as e:
            print('[red]Something went wrong! Try again.')
            print(e)


if __name__ == '__main__':
    gofile()
