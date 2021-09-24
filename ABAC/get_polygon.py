"""
Get the polygon for like columbia university in osimap API
"""

from osmapi import OsmApi
from xml.dom import minidom
import os
import pprint


def get_polygon(file_path):
    # get the xml polygon
    # file path should be xml file
    if not file_path.endswith(".xml"):
        print("Not an XML file!")
        return None
    try:
        xml_dom = minidom.parse(file_path)
        nodes = xml_dom.getElementsByTagName('nd')
        polygon_coordinates = {
            "polygon": []
        }
        mapAPI = OsmApi()
        for node in nodes:
            node_id = node.attributes["ref"].value
            response = mapAPI.NodeGet(node_id)
            polygon_coordinates["polygon"].append(
                {
                    "lat": response["lat"],
                    "lon": response["lon"]
                }
            )

        arr_loc = []
        for lat_lon in polygon_coordinates["polygon"]:
            arr_loc.append([lat_lon["lat"], lat_lon["lon"]])

        return arr_loc
    except Exception as e:
        print(str(e))
        return None


if __name__ == "__main__":
    file = "columbia.xml"
    data_folder = os.path.join("data", "geoxml")
    file_path = os.path.join(data_folder, file)
    polygon = get_polygon(file_path)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(polygon)
