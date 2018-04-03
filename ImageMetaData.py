import piexif


class ImageMetaData(object):
    '''
    Extract the exif data from any image. Data includes GPS coordinates,
    Focal Length, Manufacture, and more.
    '''
    exif_data = None
    img_path = None

    def __init__(self, img_path):
        self.img_path = img_path
        self.get_exif_data()
        super(ImageMetaData, self).__init__()

    def get_exif_data(self):
        """Returns a dictionary from the exif data of an PIL
        Image item. Also converts the GPS Tags"""
        self.exif_data = piexif.load(self.img_path)
        return self.exif_data

    def get_if_exist(self, data, key):
        if key in data:
            return data[key]
        return None

    def convert_to_degress(self, value):
        """Helper function to convert the GPS coordinates
        stored in the EXIF to degress in float format"""
        d0 = value[0][0]
        d1 = value[0][1]
        d = float(d0) / float(d1)

        m0 = value[1][0]
        m1 = value[1][1]
        m = float(m0) / float(m1)

        s0 = value[2][0]
        s1 = value[2][1]
        s = float(s0) / float(s1)

        return d + (m / 60.0) + (s / 3600.0)

    def get_lat_lng(self):
        """Returns the latitude and longitude, if available, from the
        provided exif_data (obtained through get_exif_data above)"""
        lat = None
        lng = None
        exif_data = self.get_exif_data()
        if "GPS" in exif_data:
            gps_data = exif_data["GPS"]
            gps_latitude = self.get_if_exist(
                gps_data, piexif.GPSIFD.GPSLatitude)
            gps_latitude_ref = self.get_if_exist(
                gps_data, piexif.GPSIFD.GPSLatitudeRef)
            gps_longitude = self.get_if_exist(
                gps_data, piexif.GPSIFD.GPSLongitude)
            gps_longitude_ref = self.get_if_exist(
                gps_data, piexif.GPSIFD.GPSLongitudeRef)
            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                gps_latitude_ref = gps_latitude_ref.decode("utf-8")
                gps_longitude_ref = gps_longitude_ref.decode("utf-8")
                lat = self.convert_to_degress(gps_latitude)
                if gps_latitude_ref != 'N':
                    lat = 0 - lat
                lng = self.convert_to_degress(gps_longitude)
                if gps_longitude_ref != 'E':
                    lng = 0 - lng
        return lat, lng
