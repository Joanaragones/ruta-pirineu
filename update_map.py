import requests
import json
import polyline

# --- CONFIGURACIÓ ---
CLIENT_ID = '222248'
CLIENT_SECRET = '479e199c52c8cc5d3f77241327480099b9f7016a'
REFRESH_TOKEN = '8637d0f689e2a1265e4bb2326c7dcc98633a98ac'
HASHTAG = "#delmaralpirineu"

# 1. Obtenir nou token d'accés
print("🔄 Connectant amb Strava...")
auth_url = "https://www.strava.com/oauth/token"
payload = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'refresh_token': REFRESH_TOKEN,
    'grant_type': 'refresh_token',
    'f': 'json'
}
res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']

# 2. Demanar activitats
header = {'Authorization': 'Bearer ' + access_token}
# Demanem les últimes 20 activitats
activities_url = "https://www.strava.com/api/v3/athlete/activities?per_page=20"
activities = requests.get(activities_url, headers=header).json()

print(f"🧐 He trobat {len(activities)} activitats totals al teu compte.")

totes_les_rutes = []
distancia_total = 0

for activity in activities:
    nom = activity['name']
    descripcio = activity.get('description', '') or ''
    
    # Comprovem si el hashtag està al títol O a la descripció
    if HASHTAG.lower() in nom.lower() or HASHTAG.lower() in descripcio.lower():
        print(f"✅ Activitat trobada: {nom}")
        
        if activity['map']['summary_polyline']:
            punts = polyline.decode(activity['map']['summary_polyline'])
            totes_les_rutes.extend(punts)
            distancia_total += activity['distance'] / 1000
        else:
            print(f"⚠️ L'activitat '{nom}' no té dades de mapa (GPS).")

# 3. Guardar si hem trobat alguna cosa
if totes_les_rutes:
    dades = {
        "distancia": round(distancia_total, 2),
        "ruta": totes_les_rutes
    }
    with open('dades_ruta.json', 'w') as f:
        json.dump(dades, f)
    print(f"🥳 FET! Has recorregut {round(distancia_total, 2)} km en total.")
else:
    print(f"❌ No he trobat cap activitat amb el hashtag {HASHTAG}.")
    print("Revisa que l'activitat sigui pública i tingui el hashtag al títol.")