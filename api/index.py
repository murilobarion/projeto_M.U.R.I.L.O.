from flask import Flask, render_template, request, send_file
import requests
import os
import json
import pandas as pd
import io
import math
from datetime import datetime, timedelta

# ── Caminhos para a estrutura NASA/ ──────────────────────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
)

def get_nasa_apod():
    api_key = os.environ.get('NASA_API_KEY', "faZ5X3HvBrJ32ynZMH7lp08wBESv3ZOdKmXuf6f3")
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
    try:
        res = requests.get(url, timeout=5)
        return res.json().get('url') if res.status_code == 200 else None
    except Exception:
        return None

def calculate_kinetic_energy(diameter_m, velocity_km_h):
    """ Calcula a energia cinética aproximada em Megatons de TNT. """
    radius = diameter_m / 2
    volume = (4/3) * math.pi * (radius**3)
    mass = volume * 3000  # Massa em kg (densidade rocha)
    velocity_m_s = velocity_km_h / 3.6
    energy_joules = 0.5 * mass * (velocity_m_s**2)
    megatons = energy_joules / 4.184e15
    return round(megatons, 4)

def get_space_weather(data_pesquisa):
    """Busca eventos de clima espacial (CME) na NASA DONKI."""
    api_key = os.environ.get('NASA_API_KEY', "faZ5X3HvBrJ32ynZMH7lp08wBESv3ZOdKmXuf6f3")
    url = f"https://api.nasa.gov/DONKI/CME?startDate={data_pesquisa}&endDate={data_pesquisa}&api_key={api_key}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            dados = res.json()
            return f"{len(dados)} CMEs detectadas" if dados else "Vento Solar Calmo"
        return "Dados Indisponíveis"
    except:
        return "Erro na Telemetria Solar"

def convert_distance_ld(kilometers):
    """Converte quilômetros para Lunar Distances (LD) e Milhões de km (M km)."""
    ld = float(kilometers) / 384400 
    m_km = float(kilometers) / 1000000 
    return {
        'kilometers': round(float(kilometers), 1),
        'ld': round(ld, 1),
        'm_km': round(m_km, 2)
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    dados_asteroides = []
    chart_labels, chart_data = [], []
    js_3d_asteroids = []
    
    data_pesquisa = ""
    erro = None
    bg_nasa = get_nasa_apod() or 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop'

    terremotos = []
    total_terremotos = 0
    correlacao_ironica = ""
    
    total_energy = 0
    space_weather = "Aguardando Varredura..."

    lista_fotos = [
        "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?w=150&h=150&fit=crop",
        "https://images.unsplash.com/photo-1614728263952-84ea256f9679?w=150&h=150&fit=crop",
        "https://images.unsplash.com/photo-1614726365930-627c75da663e?w=150&h=150&fit=crop",
        "https://images.unsplash.com/photo-1506318137071-a8e063b4bc3c?w=150&h=150&fit=crop",
        "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=150&h=150&fit=crop",
        "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=150&h=150&fit=crop",
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=150&h=150&fit=crop",
        "https://images.unsplash.com/photo-1630839437035-dac17da580d0?w=150&h=150&fit=crop",
        "https://images.unsplash.com/photo-1446941611757-91d2c3bd3d45?w=150&h=150&fit=crop",
        "https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=150&h=150&fit=crop",
    ]

    if request.method == 'POST':
        data_pesquisa = request.form.get('data')
        hoje = datetime.now().strftime('%Y-%m-%d')

        if data_pesquisa > hoje:
            erro = "ERRO: ACESSO AO FUTURO BLOQUEADO PELO PROTOCOLO DE SEGURANÇA."
        else:
            api_key = os.environ.get('NASA_API_KEY', "faZ5X3HvBrJ32ynZMH7lp08wBESv3ZOdKmXuf6f3")
            link_api = "https://api.nasa.gov/neo/rest/v1/feed"
            try:
                resposta = requests.get(
                    link_api,
                    params={'start_date': data_pesquisa, 'end_date': data_pesquisa, 'api_key': api_key},
                    timeout=15,
                )
                if resposta.status_code == 200:
                    dados = resposta.json()['near_earth_objects'].get(data_pesquisa, [])
                    dados_asteroides = dados
                    
                    space_weather = get_space_weather(data_pesquisa)

                    for a in dados:
                        chart_labels.append(a['name'].split(' ')[-1].replace('(', '').replace(')', ''))
                        diametro_max = a['estimated_diameter']['meters']['estimated_diameter_max']
                        chart_data.append(diametro_max)
                        
                        js_3d_asteroids.append({
                            'id': a['id'],
                            'name': a['name'].replace('(', '').replace(')', ''),
                            'diameter': diametro_max,
                            'radius_km': convert_distance_ld(a['close_approach_data'][0]['miss_distance']['kilometers'])
                        })
                        
                        velocidade = float(a['close_approach_data'][0]['relative_velocity']['kilometers_per_hour'])
                        total_energy += calculate_kinetic_energy(diametro_max, velocidade)
            
                    try:
                        data_obj = datetime.strptime(data_pesquisa, '%Y-%m-%d')
                        dia_seguinte = (data_obj + timedelta(days=1)).strftime('%Y-%m-%d')
                        
                        link_usgs = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={data_pesquisa}&endtime={dia_seguinte}&minmagnitude=2.5"
                        res_eq = requests.get(link_usgs, timeout=10)
                        
                        if res_eq.status_code == 200:
                            dados_eq = res_eq.json()
                            total_terremotos = dados_eq['metadata']['count']
                            features = dados_eq['features']
                            
                            features.sort(key=lambda x: x['properties']['mag'], reverse=True)
                            terremotos = features[:5]
                            
                            for t in terremotos:
                                tempo_ms = t['properties']['time']
                                t['data_formatada'] = datetime.fromtimestamp(tempo_ms / 1000.0).strftime('%H:%M:%S')

                            if total_terremotos > 0 and len(dados_asteroides) > 0:
                                chance = min(99.9, (len(dados_asteroides) * 0.082) + (total_terremotos * 0.015))
                                if total_energy > 1000000:
                                    correlacao_ironica = "99.9% de chance! ANOMALIA DE ENERGIA GRAVITACIONAL MASSIVA DETECTADA!"
                                else:
                                    correlacao_ironica = f"{chance:.3f}% de chance da culpa ser do espaço."
                            elif total_terremotos > 0:
                                correlacao_ironica = "0% de culpa espacial. Apenas a Terra espreguiçando."
                            else:
                                correlacao_ironica = "Nenhum tremor. A Terra está imóvel de medo."
                    except Exception as e:
                        print("Erro no AstroQuake:", e)
                        correlacao_ironica = "Sismógrafos offline no multiverso."

                else:
                    erro = "FALHA NA CONEXÃO COM A REDE DEEP SPACE."
            except Exception:
                erro = "INTERRUPÇÃO DE SINAL DETECTADA."

    return render_template(
        'index.html',
        asteroides=dados_asteroides,
        data=data_pesquisa,
        erro=erro,
        bg_nasa=bg_nasa,
        chart_labels=json.dumps(chart_labels),
        chart_data=json.dumps(chart_data),
        js_3d_asteroids=json.dumps(js_3d_asteroids),
        fotos_procedurais=lista_fotos,
        terremotos=terremotos,
        total_terremotos=total_terremotos,
        correlacao_ironica=correlacao_ironica,
        total_energy=round(total_energy, 2),
        space_weather=space_weather
    )

@app.route('/exportar', methods=['POST'])
def exportar():
    data_alvo = request.form.get('data_export')
    api_key = os.environ.get('NASA_API_KEY', "faZ5X3HvBrJ32ynZMH7lp08wBESv3ZOdKmXuf6f3")

    try:
        res = requests.get(
            f"https://api.nasa.gov/neo/rest/v1/feed"
            f"?start_date={data_alvo}&end_date={data_alvo}&api_key={api_key}"
        )

        if res.status_code == 200:
            dados = res.json()['near_earth_objects'][data_alvo]

            lista_relatorio = []
            for a in dados:
                lista_relatorio.append({
                    'ID_OBJETO':          a['id'],
                    'DESIGNAÇÃO':         a['name'].replace('(', '').replace(')', ''),
                    'DIÂMETRO_MAX_METROS': round(a['estimated_diameter']['meters']['estimated_diameter_max'], 2),
                    'VELOCIDADE_KM_H':    round(float(a['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']), 2),
                    'DISTÂNCIA_KM':       round(float(a['close_approach_data'][0]['miss_distance']['kilometers']), 2),
                    'AMEAÇA_DETECTADA':   "SIM" if a['is_potentially_hazardous_asteroid'] else "NÃO",
                })

            df = pd.DataFrame(lista_relatorio)

            buffer = io.BytesIO()
            df.to_csv(buffer, index=False, sep=';', encoding='utf-8-sig')
            buffer.seek(0)

            return send_file(
                buffer,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f"LOG_TELEMETRIA_{data_alvo}.csv",
            )

    except Exception as e:
        return f"Erro na exportação: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
    