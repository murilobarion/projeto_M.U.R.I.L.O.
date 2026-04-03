from flask import Flask, render_template, request, send_file
import requests
import os
import json
import pandas as pd
import io
from datetime import datetime

app = Flask(__name__, 
            template_folder='../templates', 
            static_folder='../static')

def get_nasa_apod():
    api_key = os.environ.get('NASA_API_KEY', "faZ5X3HvBrJ32ynZMH7lp08wBESv3ZOdKmXuf6f3")
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
    try:
        res = requests.get(url, timeout=5)
        return res.json().get('url') if res.status_code == 200 else None
    except: 
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    dados_asteroides = []
    chart_labels, chart_data = [], []
    data_pesquisa = ""
    erro = None
    bg_nasa = get_nasa_apod() or 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop'

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
        "https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=150&h=150&fit=crop"
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
                resposta = requests.get(link_api, params={'start_date': data_pesquisa, 'end_date': data_pesquisa, 'api_key': api_key}, timeout=15)
                if resposta.status_code == 200:
                    dados = resposta.json()['near_earth_objects'].get(data_pesquisa, [])
                    dados_asteroides = dados
                    for a in dados:
                        chart_labels.append(a['name'].split(' ')[-1].replace('(', '').replace(')', ''))
                        chart_data.append(a['estimated_diameter']['meters']['estimated_diameter_max'])
                else: 
                    erro = "FALHA NA CONEXÃO COM A REDE DEEP SPACE."
            except: 
                erro = "INTERRUPÇÃO DE SINAL DETECTADA."

    return render_template('index.html', asteroides=dados_asteroides, data=data_pesquisa, erro=erro, 
                           bg_nasa=bg_nasa, chart_labels=json.dumps(chart_labels), 
                           chart_data=json.dumps(chart_data), fotos_procedurais=lista_fotos)

@app.route('/exportar', methods=['POST'])
def exportar():
    data_alvo = request.form.get('data_export')
    api_key = os.environ.get('NASA_API_KEY', "faZ5X3HvBrJ32ynZMH7lp08wBESv3ZOdKmXuf6f3")
    
    try:
        res = requests.get(f"https://api.nasa.gov/neo/rest/v1/feed?start_date={data_alvo}&end_date={data_alvo}&api_key={api_key}")
        
        if res.status_code == 200:
            dados = res.json()['near_earth_objects'][data_alvo]
            
            lista_relatorio = []
            for a in dados:
                lista_relatorio.append({
                    'ID_OBJETO': a['id'],
                    'DESIGNAÇÃO': a['name'].replace('(', '').replace(')', ''),
                    'DIÂMETRO_MAX_METROS': round(a['estimated_diameter']['meters']['estimated_diameter_max'], 2),
                    'VELOCIDADE_KM_H': round(float(a['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']), 2),
                    'DISTÂNCIA_KM': round(float(a['close_approach_data'][0]['miss_distance']['kilometers']), 2),
                    'AMEAÇA_DETECTADA': "SIM" if a['is_potentially_hazardous_asteroid'] else "NÃO"
                })
            
            df = pd.DataFrame(lista_relatorio)
 
            buffer = io.BytesIO()
            df.to_csv(buffer, index=False, sep=';', encoding='utf-8-sig') 
            buffer.seek(0)
            
            return send_file(
                buffer,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f"LOG_TELEMETRIA_{data_alvo}.csv"
            )
    except Exception as e:
        return f"Erro na exportação: {str(e)}", 500

app = app