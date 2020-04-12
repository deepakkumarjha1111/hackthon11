from bs4 import BeautifulSoup
import requests
from flask import Flask, jsonify
import json
from opencage.geocoder import OpenCageGeocode

key = "db5e12475643479390239ad92a1f7698"
geocoder = OpenCageGeocode(key)
app = Flask(__name__)
page = requests.get("https://bing.com/covid")
soup = BeautifulSoup(page.content, "html.parser")
data = soup.find("div").text[9:-1]

data = json.loads(data)


def find_country(cou):
    try:
        for loc in data["areas"]:
            if loc["id"] == cou:
                return loc
    except Exception as e:
        print(e)
    return None


@app.route('/location', methods=['GET'])
def get_all_data():
    return jsonify({'data': data})


@app.route('/location/<float:lat>/<float:long>', methods=['GET'])
def get_data(lat, long):
    try:
        results = geocoder.reverse_geocode(lat, long)
        country = results[0]["components"]["country"]
        country_searched = find_country(country.lower())
        if country_searched:
            try:
                state = results[0]["components"]["state"]
                for state_searched in country_searched["areas"]:
                    if state_searched["displayName"] == state:
                        try:
                            state_district = results[0]["components"]["state_district"]
                            for district_searched in state_searched["areas"]:
                                if district_searched["displayName"] == state_district:
                                    district_searched.pop("areas")
                                    return jsonify(district_searched)
                        except Exception as e:
                            print(e)
                            state_searched.pop("areas")
                            return jsonify(state_searched)
            except Exception as e:
                print(e)
                country_searched.pop("areas")
                return jsonify(country_searched)
    except Exception as e:
        print(e)
    return jsonify({"message": "Not able to Locate."})


app.run()
