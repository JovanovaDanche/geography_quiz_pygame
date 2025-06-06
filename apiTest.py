from utils.api import get_country_data

countries = get_country_data()
for c in countries[:5]:  # првите 5 земји
    print(f"{c['country']} - Capital: {c['capital']} - Region: {c['region']}")
