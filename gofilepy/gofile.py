#!/usr/bin/env python3
# coding: utf-8

import argparse
import json
import mimetypes
import os
import subprocess
import time
from datetime import datetime
from glob import glob
from pathlib import Path
from platform import platform

import requests
from rich import print as rprint
from rich.highlighter import JSONHighlighter
from rich.panel import Panel
from rich.progress import track

from .__version__ import __version__


def upload(file, best_server):
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
                data={'token': os.getenv('GOFILE_TOKEN')},
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


def opts():
    parser = argparse.ArgumentParser(
        description='Example: gofile <file/folder_path>')
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


def gofile_upload(path, verbose=False, export=False, open_urls=False):
    highlighter = JSONHighlighter()

    get_server = requests.get('https://apiv2.gofile.io/getServer')
    best_server = get_server.json()['data']['server']

    files = []

    for _path in path:
        if Path(_path).is_dir():
            dir_items = glob(str(Path(f'{_path}/**/*')), recursive=True)
            local_files = [x for x in dir_items if not Path(x).is_dir()]
            files.append(local_files)
        else:
            files.append([_path])

    files = sum(files, [])

    export_data = []
    urls = []

    for file in track(files, description='[blue]Uploading progress:'):
        upload_resp = upload(file, best_server).json()
        ts = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        record = {file: {'timestamp': ts, 'response': upload_resp}}

        url = upload_resp['data']['downloadPage']
        urls.append(url)

        if verbose:
            highlighted_resp = highlighter(json.dumps(record, indent=2))
            rprint(Panel(highlighted_resp))

        else:
            rprint(
                Panel.fit(
                    f'[yellow]File:[/yellow] [blue]{file}[/blue]\n'
                    f'[yellow]Download page:[/yellow] [blue]{url}[/blue]'))

        if export:
            export_data.append(record)

    if export:
        export_fname = f'gofile_export_{int(time.time())}.json'
        with open(export_fname, 'w') as j:
            json.dump(export_data, j, indent=4)
        rprint('[green]Exported data to:[/green] '
               f'[magenta]{export_fname}[/magenta]')

    if 'macOS' in platform() and open_urls:
        for url in urls:
            subprocess.call(['open', f'{url}'])


def main():
    args = opts()
    gofile_upload(path=args.path,
                  verbose=args.verbose,
                  export=args.export,
                  open_urls=args.open_urls)


if __name__ == '__main__':
    main()
