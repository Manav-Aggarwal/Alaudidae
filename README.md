# Alaudidae
Technical Assignment for Skylark Drones

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
- POI_RADIUS: Radius used for the points of interest CSV file.

The script reads the SRT files in the video directory which contain GPS coordinates of the drone at the all the different times that the drone flew over the survey site. It creates a map of images in the image directory which are geotagged to map image names to their coordinates. Finally, it creates a CSV file containing a list of images within the given radius at each second of the drone's flight. Additionally, it generates a KML file of the drone's path in the videos in the video directory.

It reads a CSV file with some points of interests and their coordinates to create another file containing a list of images within the given radius at each point of interest.

Example usage:
```
  python script.py 35 50
```
