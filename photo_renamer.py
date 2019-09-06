#!/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os
import PIL.Image
import PIL.ExifTags
import sys


def main(args):
    folderpath = os.path.abspath(args[0])
    print("Working with directory: %s" % folderpath)
    try:
        timezone_offset = int(args[1])
    except IndexError:
        timezone_offset = 0
    except ValueError:
        timezone_offset = 0

    pictures = [f for f in os.listdir(folderpath) if f.endswith('.JPG')]
    pictures.sort()

    for pic in pictures:
        img = PIL.Image.open(os.path.join(folderpath, pic))
        raw_time = img._getexif()[306]
        img.close()

        converted_time = datetime.datetime.strptime(raw_time, '%Y:%m:%d %H:%M:%S')
        if timezone_offset:
            print("Offsetting original time by %d hours" % timezone_offset)
            converted_time = converted_time + datetime.timedelta(hours=timezone_offset)
        newname = str(converted_time).replace(':', '.') + '.jpg'

        os.rename(os.path.join(folderpath, pic), os.path.join(folderpath, newname))

        print('%s -> %s' % (pic, newname))


if __name__ == "__main__":
    args = sys.argv[1:]
    main(args)
