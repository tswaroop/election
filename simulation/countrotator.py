'''
A simulator for counting day. Rotates through 2014-summary.json files
'''

import os
from glob import glob
from time import sleep

count = -1
while True:
    files = glob('2014-summary-*.json')
    count = (count + 1) % len(files)
    with open('../2014-summary.json', 'w') as out:
        out.write(open(files[count]).read())
    print files[count]
    sleep(15)
