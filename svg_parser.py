from xml.etree import ElementTree as ET
import re
from shapely.geometry import Polygon
from svgpathtools import parse_path
def extract_coords_from_path(d):
    path = parse_path(d)
    coords = []
    for segment in path:
        try:
            coords.append((segment.start.real, segment.start.imag))
        except AttributeError:
            pass
    if path:
        coords.append((path[-1].end.real, path[-1].end.imag))
    return coords

svg_file = "svg/Blank_map_of_Europe_(with_disputed_regions).svg"
tree = ET.parse(svg_file)
root = tree.getroot()
ns = {"svg": "http://www.w3.org/2000/svg"}

valid_polygons = {}

for path_elem in root.findall(".//svg:path", namespaces=ns):
    country_id = path_elem.get("id")
    d_attr = path_elem.get("d")
    if country_id and d_attr:
        coords = extract_coords_from_path(d_attr)
        print(f"{country_id}: {len(coords)} coords")
        if len(coords) >= 3:
            poly = Polygon(coords)
            if poly.is_valid:
                valid_polygons[country_id] = poly

print(f"Total valid polygons: {len(valid_polygons)}")
print("First 10:", list(valid_polygons.keys())[:10])
def load_country_polygons(svg_file):
    tree = ET.parse(svg_file)
    root = tree.getroot()
    ns = {"svg": "http://www.w3.org/2000/svg"}

    country_polygons = {}

    for path in root.findall(".//svg:path", namespaces=ns):
        country_id = path.get("id")
        d_attr = path.get("d")
        if country_id and d_attr:
            coords = extract_coords_from_path(d_attr)
            if len(coords) >= 3:
                poly = Polygon(coords)
                #if poly.is_valid:
                country_polygons[country_id] = poly

    return country_polygons

