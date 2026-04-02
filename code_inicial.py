import requests
from rich.console import Console
from rich.table import Table
import os

console = Console()

api_key = os.environ.get('NASA_API_KEY', "faZ5X3HvBrJ32ynZMH7lp08wBESv3ZOdKmXuf6f3") 
link_api = "https://api.nasa.gov/neo/rest/v1/feed"

data_usuario = input('Digite a data (Ex: 2026-03-31): ')

parametros = {
    'start_date': data_usuario,
    'end_date': data_usuario,
    'api_key': api_key
}

resposta = requests.get(link_api, params=parametros)

if resposta.status_code == 200:
    dados_requisicao = resposta.json()

    table = Table(title=f"Asteroides em {data_usuario}", show_header=True, header_style="bold magenta")
    table.add_column("Nome", style="green")
    table.add_column("ID", style="green")
    table.add_column("Diametro Máx (m)", style="green")
    table.add_column("Diametro Mín (m)", style="green")   
    table.add_column("Velocidade (km/h)", style="green")
    table.add_column("Dist. Terra (km)", style="green")
    table.add_column("Perigo", style="green")

    lista_asteroides = dados_requisicao['near_earth_objects'][data_usuario]

    for asteroide in lista_asteroides:
        nome = asteroide['name']
        id_asteroid = asteroide['id']
        d_min = f"{asteroide['estimated_diameter']['meters']['estimated_diameter_min']:.2f}"
        d_max = f"{asteroide['estimated_diameter']['meters']['estimated_diameter_max']:.2f}"
        dados = asteroide['close_approach_data'][0]
        vel = f"{float(dados['relative_velocity']['kilometers_per_hour']):,.2f}"
        dist = f"{float(dados['miss_distance']['kilometers']):,.0f}"
        perigo = "SIM" if asteroide['is_potentially_hazardous_asteroid'] else "NÃO"
        
        table.add_row(nome, id_asteroid, d_max, d_min, vel, dist, perigo)

    console.print(table)
        
else:
    print('API deu erro!')