import requests

def get_country_data():
    url = "https://restcountries.com/v3.1/all?fields=name,capital,region,flags"
    try:
        response = requests.get(url)
        response.raise_for_status()
        countries = response.json()
        result = []
        for c in countries:
            name = c.get("name", {}).get("common", "N/A").strip()
            capital_list = c.get("capital", [])
            capital = capital_list[0].strip() if capital_list else "N/A"
            region = c.get("region", "N/A").strip()
            flag = c.get("flags", {}).get("png", "")

            # Debug print — ова ќе ти ги покаже сите земји и нивните главни градови
            #print(f"{name} -> {capital}")

            result.append({
                "country": name,
                "capital": capital,
                "region": region,
                "flag": flag
            })
        return result
    except Exception as e:
        print("Error fetching data:", e)
        return []
