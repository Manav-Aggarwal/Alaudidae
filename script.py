"""Technical assingnment for Skylark Drones."""

import os
import fnmatch
import pysrt
import csv
import simplekml
import argparse
from ImageMetaData import ImageMetaData
from geopy.distance import vincenty
from datetime import datetime, timedelta


def constructImgMap(imgDir, imgPattern):
    """Construct a dictionary that maps images in the image directory to their
    corresponding GPS coordinates by extracting EXIF data from the geotagged
    images."""
    imgToGPS = {}
    listOfImages = os.listdir(imgDir)
    for image in listOfImages:
        if fnmatch.fnmatch(image, imgPattern):
            img_path = '/'.join([imgDir, image])
            lat, lng = ImageMetaData(img_path).get_lat_lng()
        if lat and lng:
            imgToGPS[image] = (lat, lng)
    return imgToGPS


def getImgInRadius(currCoords, imgToGPS, Radius):
    """Get a list of images in the given radius of the given coordinates from a
    image map to coordinates."""
    img_list = []
    for image, coords in imgToGPS.items():
        #Uses vincenty's method to calculate distance between two coordinates.
        if vincenty(currCoords, coords).meters <= Radius:
            img_list.append(image)
    return img_list


def getCoordsFromSub(sub):
    """Get GPS coordinates from a subtitle item."""
    currLng, currLat, elevation = sub.text.split(',')
    return (currLat, currLng)


def getImgListInRadius(subsList, imgToGPS, RADIUS):
    """Go through a list of subtitle items, and gets a combined image list
    containing images in the given radius of all the items."""
    img_list = []
    for sub in subsList:
        img_list += getImgInRadius(getCoordsFromSub(sub), imgToGPS, RADIUS)
    return img_list


def getSubsFromTo(subs, currTime, endTime):
    """Slice a subtitle file to get a list of items between the given times."""
    return subs.slice(
        starts_after={
            'minutes': currTime.minute,
            'seconds': currTime.second},
        starts_before={
            'minutes': endTime.minute,
            'seconds': endTime.second})


def writeDataToCSV(data, csvFileName):
    """Writes the given data row-wise to the given csv file."""
    with open(csvFileName, "w") as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(data)


def createPrefixFileName(prefix, filename, ext):
    """Creates a appropriate filename out of the given prefix, filename, and
    extension."""
    filename = filename.split(".")[0]
    return prefix + filename + "." + ext


def processVideo(video, vid_path, imgToGPS):
    """Creates a csv file containing images in the raidus VID_RADIUS out of a
    given SRT file that contains GPS coordinates at different times."""
    subs = pysrt.open(vid_path)
    currTime = datetime(2000, 1, 1, minute=0, second=0)
    nextTime = currTime + timedelta(seconds=1)
    data = []
    data.append(["time", "image_names"])
    while True:
        parts = getSubsFromTo(subs, currTime, nextTime)
        if not parts:
            break
        img_list = getImgListInRadius(parts, imgToGPS, VID_RADIUS)
        currTime, nextTime = nextTime, nextTime + timedelta(seconds=1)
        data.append([currTime.strftime("%M:%S"), ", ".join(img_list)])
    writeDataToCSV(data, createPrefixFileName("images_", video, "csv"))


def generate_kml(video, vid_path):

    """Generate a KML out of a given SRT file that contains GPS coordinates at
    different times."""
    subs = pysrt.open(vid_path)
    data = []
    for sub in subs:
        latitude, longitude = getCoordsFromSub(sub)
        data.append([sub.start, latitude, longitude])
    csvFileName = createPrefixFileName("kml_", video, "csv")
    writeDataToCSV(data, csvFileName)
    inputfile = csv.reader(open(csvFileName, "r"))
    kml = simplekml.Kml()
    for row in inputfile:
        kml.newpoint(name=row[0], coords=[(row[2], row[1])])
    kml.save(createPrefixFileName("", video, "kml"))


def processAllVideos(imgToGPS, vidDir, vidPattern):
    """Call processVideo and generate_kml on all the files in the given
    directory matching the given pattern."""
    listOfVideos = os.listdir(vidDir)
    for video in listOfVideos:
        if fnmatch.fnmatch(video, vidPattern):
            vid_path = '/'.join([vidDir, video])
            processVideo(video, vid_path, imgToGPS)
            generate_kml(video, vid_path)


def readCSV(csvFileName):
    """Read a CSV file and returns a dict containing its data."""
    data = []
    with open(csvFileName) as csvFile:
        reader = csv.DictReader(csvFile)
        for row in reader:
            data.append(row)
    return data


def processPOIFile(imgToGPS, csvFileName):
    """Process a file containing points of interest with their GPS coordinates
    to create a csv file that contains images in the radius POI_RADIUS of the
    points of interest."""
    assetsData = readCSV(csvFileName)
    imagesData = []
    imagesData.append(["asset_name", "image_names"])
    for asset in assetsData:
        currCoords = (asset["latitude"], asset["longitude"])
        img_list = getImgInRadius(currCoords, imgToGPS, POI_RADIUS)
        imagesData.append([asset["asset_name"], ", ".join(img_list)])
    writeDataToCSV(imagesData, createPrefixFileName(
        "images_", csvFileName, "csv"))


def parseargs():
    """Parse the given arguments to the file and return them in integer
    form."""
    parser = argparse.ArgumentParser()
    parser.add_argument("VID_RADIUS", type=int)
    parser.add_argument("POI_RADIUS", type=int)
    args = parser.parse_args()
    return args.VID_RADIUS, args.POI_RADIUS


imgDir = "images"
vidDir = "videos"
imgPattern = "*.JPG"
vidPattern = "*.SRT"
VID_RADIUS, POI_RADIUS = parseargs()

imgToGPS = constructImgMap(imgDir, imgPattern)
processAllVideos(imgToGPS, vidDir, vidPattern)
processPOIFile(imgToGPS, "assets.csv") #Replace with the filename to process, if needed.
