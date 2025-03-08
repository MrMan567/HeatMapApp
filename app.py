import os
import re
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import folium
from folium.plugins import HeatMap
from geopy.geocoders import Nominatim
import time

app = Flask(__name__)

# Initialize the geolocator (using Nominatim)
geolocator = Nominatim(user_agent="south_korea_map_app")

def geocode_location(name, lang='en'):
    """Geocode a location name in South Korea. Returns (lat, lon, display_name)."""
    query = f"{name}, South Korea"
    location = geolocator.geocode(query, language=lang)
    if location is None:
        return None
    # Pause briefly to respect Nominatim's usage policy.
    time.sleep(1)
    return (location.latitude, location.longitude, location.address)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        language_choice = request.form.get("language", "romanized").lower()
        geocode_lang = 'ko' if language_choice == 'korean' else 'en'
        if 'file' not in request.files or request.files['file'].filename == '':
            return "No file uploaded.", 400
        file = request.files['file']
        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", file.filename)
        file.save(file_path)
        try:
            df = pd.read_excel(file_path, header=None, names=["Name", "Engagements"])
        except Exception as e:
            return f"Error processing file: {e}", 400
        m = folium.Map(location=[36.5, 127.5], zoom_start=7, tiles='CartoDB Voyager')
        heat_data = []
        for _, row in df.iterrows():
            loc_name = str(row["Name"]).strip()
            engagements = row["Engagements"]
            geocoded = geocode_location(loc_name, geocode_lang)
            if geocoded is None:
                return f"Location '{loc_name}' could not be geocoded.", 400
            lat, lon, _ = geocoded
            heat_data.append([lat, lon, engagements])
        if heat_data:
            HeatMap(heat_data, radius=25).add_to(m)

        # --- Add static military base markers here ---
        # US bases
        us_bases = [
            {"name": "Camp Humphreys", "lat": 36.9630, "lon": 127.0308},
            {"name": "Camp Casey", "lat": 37.9400, "lon": 127.0668},
            {"name": "Camp Walker", "lat": 35.8497, "lon": 128.5944},
            {"name": "Camp Carroll", "lat": 35.9059, "lon": 128.8500},
            {"name": "Osan Air Base", "lat": 37.1522, "lon": 127.0706},
            {"name": "Kunsan Air Base", "lat": 35.9042, "lon": 126.6155},
            {"name": "Jinhae Naval Base", "lat": 35.1484, "lon": 128.6811},
            {"name": "Yongsan Garrison", "lat": 37.5387, "lon": 126.9656},
            {"name": "K-16 Air Base", "lat": 37.4568, "lon": 127.1205}
        ]
        for base in us_bases:
            folium.Marker(
                location=[base["lat"], base["lon"]],
                popup=base["name"],
                tooltip=base["name"],
                icon=folium.DivIcon(
                html='<i class="fa fa-star" style="font-size:12px; color: red;"></i>',
                icon_size=(12, 12),
                icon_anchor=(12, 12)  # Center the icon over the coordinate
                )
            ).add_to(m)
        
        # ROK bases
        rok_bases = [
            {"name": "Gyeryong", "lat": 36.2741, "lon": 127.2486},
            {"name": "Paju", "lat": 37.7536, "lon": 126.8367},
            {"name": "Chuncheon", "lat": 37.8746, "lon": 127.7306},
            {"name": "Yongin", "lat": 37.2411, "lon": 127.1774},
            {"name": "Yangju", "lat": 37.7920, "lon": 127.0620},
            {"name": "Pocheon", "lat": 38.0624, "lon": 127.2746},
            {"name": "Uijeongbu", "lat": 37.7383, "lon": 127.0378},
            {"name": "Wonju", "lat": 37.3420, "lon": 127.9425},
            {"name": "Gangneung", "lat": 37.7517, "lon": 128.8965},
            {"name": "Seongnam", "lat": 37.4123, "lon": 127.1258},
            {"name": "Busan Naval Base", "lat": 35.1796, "lon": 129.0756},
            {"name": "Jeju Naval Base", "lat": 33.4996, "lon": 126.5312},
            {"name": "Seosan Air Base", "lat": 36.7830, "lon": 126.4995},
            {"name": "Cheongju Air Base", "lat": 36.7173, "lon": 127.4986},
            {"name": "Gimhae Air Base", "lat": 35.1798, "lon": 129.1302},
            {"name": "Gwangju Air Base", "lat": 35.1232, "lon": 126.8054},
            {"name": "Suwon Air Base", "lat": 37.2869, "lon": 127.0087},
            {"name": "Wonju Air Base", "lat": 37.3420, "lon": 127.9425}
        ]
        for base in rok_bases:
            folium.CircleMarker(
                location=[base["lat"], base["lon"]],
                radius=5,
                popup=base["name"],
                tooltip=base["name"],
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=1
            ).add_to(m)
        # --- End marker section ---

        # Save the generated map to an HTML file in the static folder
        os.makedirs("static", exist_ok=True)
        output_file = os.path.join("static", "south_korea_map.html")
        m.save(output_file)
        
        return redirect(url_for('view_map'))
    
    return render_template("index.html")
    
@app.route('/view')
def view_map():
    # This template will display the generated map.
    return render_template("view.html")

if __name__ == '__main__':
    app.run(debug=True)