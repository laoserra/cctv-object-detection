#!/usr/bin/env python3

import sys
import pandas as pd
import os

#manually correcting faulty camera
# warning = 2 ("engineering_note": "Mechanical camera fault - cannot tilt. Found out in 2023-11-06")
# warning = 3 (capture preset pointing to tree foliage)
# warning = 4 (camera pointing to the wrong location)
# warning = 5 (camera out of focus)
# warning = 6 (street environment in use for other purposes, e.g. Christmas fair)
# warning = 7 (one color image)

def main(file_path):

    data = pd.read_csv(file_path)
    report = f'{file_path}'
    data.loc[data['camera_ref']=='C134', 'warnings'] = 3
    data.to_csv(report, index=False, compression='gzip')


if __name__ == '__main__':
    main(sys.argv[1])
