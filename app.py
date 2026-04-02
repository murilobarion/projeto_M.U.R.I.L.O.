from flask import Flask, render_template, request
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)

def get_nasa_apod():
    """Busca a imagem astronômica do dia da NASA."""
    api_key = os.environ.get('NASA_API_KEY', "faZ5X3HvBrJ32ynZMH7lp08wBESv3ZOdKmXuf6f3")
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json().get('url')
        return None
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    dados_asteroides = []
    chart_labels = []
    chart_data = []
    data_pesquisa = ""
    erro = None
    
    # Pega a imagem ou define uma padrão se a NASA falhar
    background_url = get_nasa_apod()
    if not background_url:
        background_url = 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop'

    if request.method == 'POST':
        data_pesquisa = request.form.get('data')
        hoje = datetime.now().strftime('%Y-%m-%d')
        
        if data_pesquisa > hoje:
            erro = "Acesso Negado: O sistema monitora apenas eventos passados ou em curso."
        else:
            api_key = os.environ.get('NASA_API_KEY', "faZ5X3HvBrJ32ynZMH7lp08wBESv3ZOdKmXuf6f3") 
            link_api = "https://api.nasa.gov/neo/rest/v1/feed"
            
            parametros = {
                'start_date': data_pesquisa,
                'end_date': data_pesquisa,
                'api_key': api_key
            }

            try:
                resposta = requests.get(link_api, params=parametros, timeout=15)
                if resposta.status_code == 200:
                    dados_requisicao = resposta.json()
                    if data_pesquisa in dados_requisicao['near_earth_objects']:
                        dados_asteroides = dados_requisicao['near_earth_objects'][data_pesquisa]
                        
                        # PREPARA OS DADOS PARA O GRÁFICO AQUI NO PYTHON
                        for a in dados_asteroides:
                            nome_limpo = a['name'].split(' ')[-1].replace('(', '').replace(')', '')
                            tamanho = a['estimated_diameter']['meters']['estimated_diameter_max']
                            chart_labels.append(nome_limpo)
                            chart_data.append(tamanho)
                    else:
                        erro = "Nenhum dado encontrado para esta data específica."
                else:
                    erro = "Falha na comunicação com a base de dados da NASA."
            except Exception:
                erro = "Erro de conexão interplanetária."

    return render_template('index.html', 
                           asteroides=dados_asteroides, 
                           data=data_pesquisa, 
                           erro=erro, 
                           bg_nasa=background_url,
                           chart_labels=json.dumps(chart_labels),
                           chart_data=json.dumps(chart_data))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)