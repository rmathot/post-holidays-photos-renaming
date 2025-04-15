#!/bin/env python3

from argparse import ArgumentParser
from datetime import datetime
from datetime import timedelta
import os
from os import scandir
from os.path import join as path_join
import sys

import PIL
from PIL import Image
from PIL import ExifTags


def _rename(config):
    folderpath = os.path.abspath(config.directory)
    print(f"Scanning directory {folderpath}...")

    pictures = [f for f in scandir(folderpath) if f.name.lower().endswith(".jpg") or f.name.lower().endswith(".jpeg")]
    pictures.sort(key=lambda x: x.name)
    print(f"{len(pictures)} pictures found.")

    if config.apply:
        print("Renaming files...")
    else:
        print("Simulating the files renaming...")

    for pic in pictures:

        # list candidate values from EXIF tags, depending on availability
        candidates = dict()
        with Image.open(pic.path) as img:
            exif = img.getexif()

            candidates["base_date_time"] = exif.get(ExifTags.Base.DateTime)
            candidates["original_date_time"] = exif.get_ifd(ExifTags.IFD.Exif).get(ExifTags.Base.DateTimeOriginal)
            candidates["digitized_date_time"] = exif.get_ifd(ExifTags.IFD.Exif).get(ExifTags.Base.DateTimeDigitized)
            candidates["gps_date"] = exif.get_ifd(ExifTags.IFD.GPSInfo).get(ExifTags.GPS.GPSDateStamp)
            if candidates["gps_date"]:
                if candidates["gps_date"].startswith("1970"):
                    candidates["gps_date"] = None  # we don't need epoch
                else:
                    candidates["gps_date"] += " 00:00:00"  # gps date does not have time info

            if config.verbose:
                print(f"DEBUG: Here is what we learnt about {pic.name}: {candidates}")

        # try candidates from most to less accurate
        if candidates["base_date_time"]:
            use_this_date = candidates["base_date_time"]
        elif candidates["original_date_time"]:
            use_this_date = candidates["original_date_time"]
        elif candidates["digitized_date_time"]:
            use_this_date = candidates["digitized_date_time"]
        elif candidates["gps_date"]:
            use_this_date = candidates["gps_date"]
        else:
            print(f"{pic.name} -> no EXIF date information found, ignoring it.")
            continue

        timestamp = datetime.strptime(use_this_date, "%Y:%m:%d %H:%M:%S")
        if config.offset:
            # this ugly line unpacks a string like: years=1,months=2,days=3,hours=4,minutes=5,seconds=6 ...
            delta_parameters = {s.split("=")[0]: int(s.split("=")[1]) for s in config.offset.split(",")}
            # ...and build a timedelta object from it
            delta = timedelta(**delta_parameters)

            if config.verbose:
                print(f"DEBUG: Offsetting original date & time by {delta} hours")

            timestamp = timestamp + delta

        newname = timestamp.strftime("%Y-%m-%d %H.%M.%S.jpg")

        if config.apply:
            os.rename(pic.path, path_join(folderpath, newname))

        print(f"{pic.name} -> {newname}")


def main():
    parser = ArgumentParser(
        description="Renames photos based on EXIF datetime information",
    )
    parser.add_argument(
        "directory",
        type=str,
        help="Path to the folder containing the photos to rename",
    )
    parser.add_argument(
        "-a",
        "--apply",
        action="store_true",
        help="Actually rename the files. If this option is not enabled, the script will only print the new file names.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
    )
    parser.add_argument(
        "-o",
        "--offset",
        type=str,
        help="timedelta specificator to apply",
    )
    # TODO function to write back the Exif tag after offset fix
    config = parser.parse_args(sys.argv[1:])
    _rename(config)


if __name__ == "__main__":
    main()
