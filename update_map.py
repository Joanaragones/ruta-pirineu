import json
import polyline
from stravalib.client import Client

# Les teves claus d'Strava
CLIENT_ID = '222248'
CLIENT_SECRET = '479e199c52c8cc5d3f77241327480099b9f7016a'
REFRESH_TOKEN = '8637d0f689e2a1265e4bb2326c7dcc98633a98ac'

client = Client()

# Refresquem el permís
response = client.refresh_access_token(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    refresh_token=REFRESH_TOKEN
)
client.access_token = response['access_token']

# Busquem rutes amb el hashtag
activities = client.get_activities(limit=10)
punts_totals = []
dist_acumulada = 0

for act in activities:
    if "#DelMarAlPirineu" in act.name:
        dist_acumulada += float(act.distance) / 1000
        detall = client.get_activity(act.id)
        if detall.map.summary_polyline:
            punts_totals.extend(polyline.decode(detall.map.summary_polyline))

# Guardem el resultat en un fitxer que l'index.html pugui llegir
dades = {
    "distancia": round(dist_acumulada, 2),
    "ruta": punts_totals
}

with open('dades_ruta.json', 'w') as f:
    json.dump(dades, f)

print(f"✅ Fet! Has recorregut {dades['distancia']} km")