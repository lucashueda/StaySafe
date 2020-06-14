#!/usr/bin/env python
# coding: utf-8

# Imports
import googlemaps
from datetime import datetime
import requests


# Support functions
def geo_location():
    import geocoder
    g = geocoder.ip("me")
    return g

# Google Places recommendation Class

with open('api_key.txt','r') as file:
    api_key = file.read()


class StaySafe_places:
    def __init__(self):
        self.geo = geo_location()
        self.g_maps = googlemaps.Client(key=api_key)
        self.gmaps = gmaps.configure(api_key=api_key)
        self.map_url = "https://maps.googleapis.com/maps/api/staticmap?"

    def get_places_nearby(self, max_results, max_radius):
        places = self.g_maps.places_nearby(
            location=(self.geo.lat, self.geo.lng),
            type="gas_station",
            language="pt-BR",
            open_now=True,
            radius=max_radius,
        )
        if len(places["results"]) > max_results:
            return places["results"][0:max_results]
        else:
            return places["results"]

    def get_directions_info(self, destiny_address, time=None):
        # Request directions via public transit
        if time is None:
            time = datetime.now()
        directions_result = self.g_maps.directions(
            origin=(self.geo.lat, self.geo.lng),
            destination=destiny_address,
            mode="driving",
            departure_time=time,
        )
        return directions_result[0]

    def get_places_rec(self, max_results=10, max_radius=10000):
        places_json = {}
        places_nearby = self.get_places_nearby(max_results, max_radius)
        for place in places_nearby:
            general_info = self.get_directions_info(destiny_address=place["vicinity"])
            directions_info = general_info["legs"][0]

            places_json[place["name"]] = dict(
                address=place["vicinity"],
                coord=(
                    place["geometry"]["location"]["lat"],
                    place["geometry"]["location"]["lng"],
                ),
                rating=place["rating"],
                distance=directions_info["distance"]["text"],
                travel_time=directions_info["duration"]["text"],
                place_id=place["place_id"],
                polyline=general_info["overview_polyline"]["points"],
            )

        return places_json

    def get_map(self, place_info, file_path):
        g = geo_location()
        geo_latlng = str(g.latlng)[1:-1]
        destiny_address = str(place_info["coord"])[1:-1]
        polyline = place_info["polyline"]

        map_request = (
            f"size=400x400"
            f"&markers=color:blue%7Clabel:I%7C{geo_latlng}"
            f"&markers=color:red%7Clabel:F%7C{destiny_address}"
            f"&path=weight:5%7Ccolor:0x2A3DF89f%7Cenc:{polyline}"
            f"&key={api_key}"
        )

        request = self.map_url + map_request
        response = requests.get(request)

        with open(file_path, "wb") as image:
            image.write(response.content)


# StaySafe_places Tests

if __name__ == '__main__':
    test = StaySafe_places()
    places = test.get_places_rec(max_results=1,max_radius=10000)
    print(places)
    for i in places:
        file_path = i+'.png'
        place = places[i]
        test.get_map(place_info=place, file_path=file_path)

