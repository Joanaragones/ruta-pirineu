import os
import requests
import json
import polyline
from datetime import datetime

# --- CONFIGURACIÓ ---
CLIENT_ID = os.environ.get('STRAVA_CLIENT_ID')
CLIENT_SECRET = os.environ.get('STRAVA_CLIENT_SECRET')
REFRESH_TOKEN = os.environ.get('STRAVA_REFRESH_TOKEN')
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
activities_url = "https://www.strava.com/api/v3/athlete/activities?per_page=50"
activities = requests.get(activities_url, headers=header).json()

print(f"🧐 He trobat {len(activities)} activitats recents.")

totes_les_rutes = []
distancia_total = 0
llista_etapes_completades = []

# Strava dóna les activitats de la més nova a la més antiga. 
# Les girem perquè a la taula surtin en ordre cronològic.
for activity in reversed(activities):
    nom = activity['name']
    descripcio = activity.get('description', '') or ''
    
    if HASHTAG.lower() in nom.lower() or HASHTAG.lower() in descripcio.lower():
        print(f"✅ Etapa trobada: {nom}")
        
        # 1. Sumem distància
        distancia_km = round(activity['distance'] / 1000, 2)
        distancia_total += distancia_km
        
        # 2. Guardem la data (format: 14/04/2024)
        data_bruta = datetime.strptime(activity['start_date_local'], "%Y-%m-%dT%H:%M:%SZ")
        data_neta = data_bruta.strftime("%d/%m/%Y")
        
        # 3. Afegim a la llista d'etapes per la taula
        llista_etapes_completades.append({
            "data": data_neta,
            "nom": nom.replace(HASHTAG, "").strip(), # Netegem el hashtag del nom
            "distancia": distancia_km
        })
        
        # 4. Afegim la ruta al mapa
        if activity['map']['summary_polyline']:
            punts = polyline.decode(activity['map']['summary_polyline'])
            totes_les_rutes.extend(punts)

# 3. Guardar el resultat
# Fins i tot si la distància és 0, guardem el JSON perquè la web s'actualitzi
dades = {
    "distancia": round(distancia_total, 2),
    "ruta": totes_les_rutes,
    "etapes": llista_etapes_completades
}

with open('dades_ruta.json', 'w') as f:
    json.dump(dades, f)

if llista_etapes_completades:
    print(f"🥳 FET! S'han guardat {len(llista_etapes_completades)} etapes.")
else:
    print(f"ℹ️ El fitxer s'ha posat a zero (no s'han trobat activitats amb {HASHTAG}).")