#!/bin/bas
pip3 install -r requirements.txt
cp gofile.py /usr/local/bin/gofile
chmod +x /usr/local/bin/gofile
echo "" && gofile -h
