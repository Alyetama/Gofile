#!/usr/bin/env python3
# coding: utf-8

import argparse
import json
import mimetypes
import os
import subprocess
import sys
import time
from datetime import datetime
from glob import glob
from pathlib import Path
from platform import platform
from typing import Optional

import requests
from rich import print as rprint
from rich.highlighter import JSONHighlighter
from rich.panel import Panel
from rich.progress import track

from .__version__ import __version__


def upload(file: str, best_server: str, folder_id: Optional[str] = None):
    f_obj = Path(file)
    content_type = mimetypes.guess_type(f_obj)[0]
    upload_url = f'https://{best_server}.gofile.io/uploadFile'
    with open(f_obj, 'rb') as f:
        f_data = f.read()

    attempt = 0
    while True:
        try:
            resp = requests.post(
                upload_url,
                data={
                    'token': os.getenv('GOFILE_TOKEN'),
                    'folderId': folder_id
                },
                files={'file': (f_obj.name, f_data, content_type)})
            break
        except requests.exceptions.ConnectionError:
            rprint(
                'The connection was refused from the API side! '
                f'Trying again... ([cyan]{attempt}[/cyan]/10)',
                style='red')
            time.sleep(2)
            attempt += 1
            if attempt > 10:
                break
    return resp


def gofile_upload(path: list,
                  to_single_folder: bool = False,
                  verbose: bool = False,
                  export: bool = False,
                  open_urls: bool = False):
    highlighter = JSONHighlighter()

    get_server = requests.get('https://apiv2.gofile.io/getServer')
    best_server = get_server.json()['data']['server']

    files = []

    for _path in path:
        if not Path(_path).exists():
            rprint(
                f'[red]ERROR: [dim blue]"{Path(_path).absolute()}"[/dim blue] '
                'does not exist! [/red]')
            continue
        if Path(_path).is_dir():
            dir_items = glob(str(Path(f'{_path}/**/*')), recursive=True)
            local_files = [x for x in dir_items if not Path(x).is_dir()]
            files.append(local_files)
        else:
            files.append([_path])

    files = sum(files, [])

    export_data = []
    urls = []
    folder_id = None
    n = 0

    for file in track(files, description='[magenta]Uploading progress:'):
        upload_resp = upload(file, best_server, folder_id).json()

        if to_single_folder and not os.getenv('GOFILE_TOKEN'):
            rprint('[red]ERROR: Gofile token is required when passing '
                   '`--to-single-folder`![/red]\n[dim red]You can find your '
                   'account token on this page: '
                   '[u][blue]https://gofile.io/myProfile[/blue][/u]\nCopy it '
                   'then export it as `GOFILE_TOKEN`. For example:\n'
                   'export GOFILE_TOKEN=\'xxxxxxxxxxxxxxxxx\'[/dim red]')
            sys.exit(1)
        elif to_single_folder and os.getenv('GOFILE_TOKEN'):
            folder_id = upload_resp['data']['parentFolder']

        ts = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        file_abs = str(Path(file).absolute())
        record = {'file': file_abs, 'timestamp': ts, 'response': upload_resp}

        url = upload_resp['data']['downloadPage']
        urls.append(url)

        if verbose:
            highlighted_resp = highlighter(json.dumps(record, indent=2))
            rprint(Panel(highlighted_resp))

        elif not to_single_folder:
            rprint(
                Panel.fit(
                    f'[yellow]File:[/yellow] [blue]{file}[/blue]\n'
                    f'[yellow]Download page:[/yellow] [u][blue]{url}[/blue][/u]'
                ))
        if export:
            export_data.append(record)

    if not urls:
        sys.exit()

    if to_single_folder:
        files = '\n'.join([str(Path(x).absolute()) for x in files])
        rprint(
            Panel.fit(f'[yellow]Files:[/yellow]\n[blue]{files}[/blue]\n'
                      '[yellow]Download page:[/yellow] '
                      f'[u][blue]{urls[0]}[/blue][/u]'))

    if export:
        export_fname = f'gofile_export_{int(time.time())}.json'
        with open(export_fname, 'w') as j:
            json.dump(export_data, j, indent=4)
        rprint('[green]Exported data to:[/green] '
               f'[magenta]{export_fname}[/magenta]')

    if 'macOS' in platform() and open_urls:
        for url in urls:
            subprocess.call(['open', f'{url}'])
            if to_single_folder:
                break


def opts():
    parser = argparse.ArgumentParser(
        description='Example: gofile <file/folder_path>')
    parser.add_argument(
        '-s',
        '--to-single-folder',
        help=
        'Upload multiple files to the same folder. All files will share the '
        'same URL. This option requires a valid token exported as: '
        '`GOFILE_TOKEN`',
        action='store_true')
    parser.add_argument(
        '-o',
        '--open-urls',
        help='Open the URL(s) in the browser when the upload is complete '
        '(macOS-only)',
        action='store_true')
    parser.add_argument('-e',
                        '--export',
                        help='Export upload response(s) to a JSON file',
                        action='store_true')
    parser.add_argument('-vv',
                        '--verbose',
                        help='Show more information',
                        action='store_true')
    parser.add_argument('path',
                        nargs='+',
                        help='Path to the file(s) and/or folder(s)')
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version=f'%(prog)s {__version__}')
    return parser.parse_args()


def main():
    args = opts()
    gofile_upload(
        path=args.path,
        to_single_folder=args.to_single_folder,
        verbose=args.verbose,
        export=args.export,
        open_urls=args.open_urls,
    )


if __name__ == '__main__':
    main()
