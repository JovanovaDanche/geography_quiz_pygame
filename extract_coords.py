import requests
import json

MAP_WIDTH = 800
MAP_HEIGHT = 600

def latlng_to_xy(lat, lng, map_width, map_height):
    x = (lng + 180) * (map_width / 360)
    y = (90 - lat) * (map_height / 180)
    return int(x), int(y)

def generate_country_coords_json():
    url = "https://restcountries.com/v3.1/all?fields=name,latlng"
    try:
        response = requests.get(url)
        response.raise_for_status()
        countries = response.json()

        country_coords = {}

        for country in countries:
            name = country.get("name", {}).get("common", "N/A")
            latlng = country.get("latlng", None)
            if latlng:
                lat, lng = latlng
                x, y = latlng_to_xy(lat, lng, MAP_WIDTH, MAP_HEIGHT)
                country_coords[name] = {"coords": (x, y)}

        with open("assets/country_coords.json", "w") as f:
            json.dump(country_coords, f, indent=2)

        print("✅ country_coords.json generated successfully!")

    except Exception as e:
        print("Error fetching data:", e)

if __name__ == "__main__":
    generate_country_coords_json()
