import re
import os

ans = input('Add an email address (y/n)? ')

if ans.lower() == 'y':

    email_addr = input('Email Address: ')

    target_line1 = f"                res = curl_response(['curl', '-s', '-F', '{email_addr}', '-F', f'file=@{{file}}',"

    target_line2 = f"            res = curl_response(['curl', '-F', '{email_addr}', '-F', f'file=@{{args.file}}',"

    with open('gofile.py') as f:

        with open('gofile_.py', 'w') as f2:
            for num, line in enumerate(f):
                if re.findall(r'# re_email1', line):
                    f2.write(f'{target_line1}\n')
                elif re.findall(r'# re_email2', line):
                    f2.write(f'{target_line2}\n')
                else:
                    f2.write(line)

    os.remove('gofile.py')
    os.rename('gofile_.py', 'gofile.py')
