# Alaudidae
Modules required:
- piexif: Python package to simplify exif manipulations.
- pysrt: Python library to edit and create SubRip files.
- geopy: Geocoding library for Python.
- simplekml: Python package to generate KML with as little effort as possible.

You can use these commands to install these modules:
```
  pip install simplekml
  pip install pysrt
  pip install geopy
  pip install piexif
```
The script takes two parameters:
- VID_RADIUS: Radius used for the video with the drone coordinates at different times.
- POI_RADIUS: Radius used for the points of interest csv file.

Example usage:
```
  python script.py 35 50
```
