from geopy.geocoders import Nominatim

def get_lat_long_by_zip(zip_code):
    geolocator = Nominatim(user_agent="friender")
    location = geolocator.geocode(zip_code)
    return (location.latitude, location.longitude)
