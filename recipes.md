# Massively change the EXIF Date/Time of files that don't have it

```bash
exiftool "-DateTimeOriginal=2023:01:12 12:23:57" *.jpg
```

# MTS video files have wrong date/times

1. Transcode them into MP4

```bash
for f in *.MTS; do
    ffmpeg -i "$f" -c copy "${f%.MTS}.mp4"
done
```

2. Reassign the timestamps with exiftool

```bash
exiftool "-DateTimeOriginal=2023:12:31 00:00:00" *.mp4
```

(this will duplicate your .mp4 files so it may be slow)
