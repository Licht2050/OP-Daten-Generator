import requests
from tabulate import tabulate

# InfluxDB API-URL
url = "http://localhost:8086/query"

# Abfrage zusammenstellen
query = 'SELECT * FROM "op_room_environment"'

# Parameter für die Abfrage
params = {
    "db": "environment", 
    "q": query
}

# HTTP-POST-Anfrage an die InfluxDB-API senden
response = requests.post(url, params=params)

# Die Antwort als JSON analysieren
data = response.json()

# Ergebnisse in eine Liste von Zeilen umwandeln
rows = []
columns = []
for result in data["results"]:
    if "series" in result:
        for serie in result["series"]:
            columns = serie["columns"]
            for values in serie["values"]:
                rows.append(values)

# Tabellarische Darstellung
table = tabulate(rows, headers=columns, tablefmt="grid")

# Die Tabelle anzeigen
print(table)
