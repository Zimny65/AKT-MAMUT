import requests
import pandas as pd
import folium
from folium.features import DivIcon
from folium.plugins import MarkerCluster

# Ustawienia z nowym kluczem API
google_sheets_url = (
    'https://sheets.googleapis.com/v4/spreadsheets/'
    '1SNj2bRlcneGGBdqA3_btM3rZ8-oPy-U6fcouOylQibk/'
    'values/Mountains?alt=json&key=AIzaSyDtf7Svkxg-3DpCnpMw3YFPyJDx8dedWIw'
)

# Pobierz dane z Google Sheets
response = requests.get(google_sheets_url)
data = response.json()

# Sprawdź, czy odpowiedź zawiera klucz 'values'
if 'values' not in data:
    raise KeyError("'values' not found in the response. Please check the "
                   "Google Sheets URL and API key.")

# Przekształć dane na DataFrame
columns = data['values'][0]
rows = data['values'][1:]
df = pd.DataFrame(rows, columns=columns)

# Zakładam, że S to 19. kolumna (indeks 18)
df['WAR'] = df.iloc[:, 18].apply(lambda x: int(x) if x else None)

# Konwertuj kolumny LAT i LON na float
df['LAT'] = pd.to_numeric(df['LAT'], errors='coerce')
df['LON'] = pd.to_numeric(df['LON'], errors='coerce')

# Usuń wiersze z brakującymi wartościami LAT, LON lub WAR
df = df.dropna(subset=['LAT', 'LON', 'WAR'])

# Resetuj indeksy, aby numeracja zaczynała się od 0
df = df.reset_index(drop=True)

# Zamień znaki nowej linii na <br> oraz " - " na <br> w odpowiednich kolumnach
df['PEAK'] = df['PEAK'].str.replace('\n', '<br>').str.replace(' - ', '<br>')
df['REGION'] = df['REGION'].str.replace('\n', '<br>').str.replace(' - ', '<br>')
df['MESOREGION'] = df['MESOREGION'].str.replace('\n', '<br>').str.replace(' - ', '<br>')
df['MICROREGION'] = df['MICROREGION'].str.replace('\n', '<br>').str.replace(' - ', '<br>')
df['HEIGHT'] = df['HEIGHT'].str.replace('\n', '<br>').str.replace(' - ', '<br>')
df['EXPEDITION'] = df['EXPEDITION'].str.replace('\n', '<br>').str.replace(' - ', '<br>')
df['DATE'] = df['DATE'].str.replace('\n', '<br>').str.replace(' - ', '<br>')

# Stwórz mapę z domyślnymi kafelkami OpenStreetMap
m = folium.Map(
    location=[45.0, 25.0],
    zoom_start=6,
    tiles=None,  # Brak domyślnych kafelków
    width="100%"
)

# Dodaj mapę OpenTopoMap jako główną warstwę
folium.TileLayer(
    tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attr='Map data: &copy; OpenStreetMap contributors, SRTM | Map style: &copy; OpenTopoMap (CC-BY-SA)',
    name='OpenTopoMap'
).add_to(m)

# Dodaj MarkerCluster
marker_cluster = MarkerCluster().add_to(m)

# Dodaj markery do MarkerCluster zamiast bezpośrednio do mapy
for index, row in df.iterrows():
    lat = row['LAT']
    lon = row['LON']
    peak = row['PEAK']
    region = row['REGION']
    mesoregion = row['MESOREGION']
    microregion = row['MICROREGION']
    height = row['HEIGHT']
    expedition = row['EXPEDITION']
    date = row['DATE']
    number = f"{index + 1:03d}"  # Numeracja markerów od 001, trzycyfrowa
    
    # Określ kolor na podstawie wartości WAR
    color = 'green' if row['WAR'] == 1 else 'red'

    # Stwórz dynamiczny popup z tabelką, czcionką Oswald 12px i wyrównaniem do góry
    popup_html = f"""
    <div style="font-family: 'Oswald', sans-serif; font-size: 12px; color: black;">
        <table style="width: auto; border-collapse: collapse;">
            <tr>
                <td style="font-weight: bold; padding: 4px; vertical-align: top;">PEAK:</td>
                <td style="padding: 4px; vertical-align: top;">{peak}</td>
            </tr>
            <tr>
                <td style="font-weight: bold; padding: 4px; vertical-align: top;">REGION:</td>
                <td style="padding: 4px; vertical-align: top;">{region}</td>
            </tr>
            <tr>
                <td style="font-weight: bold; padding: 4px; vertical-align: top;">MESOREGION:</td>
                <td style="padding: 4px; vertical-align: top;">{mesoregion}</td>
            </tr>
            <tr>
                <td style="font-weight: bold; padding: 4px; vertical-align: top;">MICROREGION:</td>
                <td style="padding: 4px; vertical-align: top;">{microregion}</td>
            </tr>
            <tr>
                <td style="font-weight: bold; padding: 4px; vertical-align: top;">HEIGHT:</td>
                <td style="padding: 4px; vertical-align: top;">{height} m</td>
            </tr>
            <tr>
                <td style="font-weight: bold; padding: 4px; vertical-align: top;">EXPEDITION:</td>
                <td style="padding: 4px; vertical-align: top;">{expedition}</td>
            </tr>
            <tr>
                <td style="font-weight: bold; padding: 4px; vertical-align: top;">DATE:</td>
                <td style="padding: 4px; vertical-align: top;">{date}</td>
            </tr>
        </table>
    </div>
    """

    # Dodaj marker do MarkerCluster
    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(24, 24),
            icon_anchor=(12, 12),
            html=f'<div style="font-size: 10px; font-family: Oswald, sans-serif; '
                 f'font-weight: bold; color: white; background-color: {color}; '
                 f'border-radius: 50%; border: 1px solid white; width: 24px; '
                 f'height: 24px; display: flex; align-items: center; '
                 f'justify-content: center;">{number}</div>'
        ),
        popup=folium.Popup(popup_html, max_width=300)
    ).add_to(marker_cluster)

# Dodaj styl CSS i JavaScript, aby przesunąć przyciski
map_style = """
    <style>
    .leaflet-container {
        width: 100vw;
        height: 100vh;
    }
    .leaflet-control-zoom {
        transform: translateY(160px); /* Większe przesunięcie kontrolki w dół */
    }
    .leaflet-control-attribution {
        display: none;
    }
    </style>
"""

# Dodaj styl do mapy
m.get_root().html.add_child(folium.Element(map_style))

# Zapisz mapę do pliku HTML
m.save('mountains_map02.html')
