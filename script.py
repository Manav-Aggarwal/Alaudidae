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
    """Constructs a dictionary that maps images in the the image
    directory to their corresponding GPS coordinates"""
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
    """Get a list of images in the given radius of the given
    coordinates from a image map to coordinates"""
    img_list = []
    for image, coords in imgToGPS.items():
        if vincenty(currCoords, coords).meters <= Radius:
            img_list.append(image)
    return img_list


def getCoordsFromSub(sub):
    currLng, currLat, elevation = sub.text.split(',')
    return (currLat, currLng)


def getImgListInRadius(subsList, imgToGPS, RADIUS):
    img_list = []
    for sub in subsList:
        img_list += getImgInRadius(getCoordsFromSub(sub), imgToGPS, RADIUS)
    return img_list


def getSubsFromTo(subs, currTime, nextTime):
    return subs.slice(
        starts_after={
            'minutes': currTime.minute,
            'seconds': currTime.second},
        starts_before={
            'minutes': nextTime.minute,
            'seconds': nextTime.second})


def writeDataToCSV(data, csvFileName):
    with open(csvFileName, "w") as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(data)


def createPrefixFileName(prefix, filename, ext):
    filename = filename.split(".")[0]
    return prefix + filename + "." + ext


def processVideo(video, vid_path, imgToGPS):
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
    listOfVideos = os.listdir(vidDir)
    for video in listOfVideos:
        if fnmatch.fnmatch(video, vidPattern):
            vid_path = '/'.join([vidDir, video])
            processVideo(video, vid_path, imgToGPS)
            generate_kml(video, vid_path)


def readCSV(csvFileName):
    data = []
    with open(csvFileName) as csvFile:
        reader = csv.DictReader(csvFile)
        for row in reader:
            data.append(row)
    return data


def processPOIFile(imgToGPS, csvFileName):
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
processPOIFile(imgToGPS, "assets.csv")
