from flask import Flask, render_template, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    dados_asteroides = []
    data_pesquisa = ""
    erro = None

    if request.method == 'POST':
        data_pesquisa = request.form.get('data')

        hoje = datetime.now().strftime('%Y-%m-%d')
        
        if data_pesquisa > hoje:
            erro = "Acesso Negado: O sistema monitora apenas eventos passados ou em curso."
        else:
            # Busca a chave no Render (NASA_API_KEY) ou usa a sua local como fallback
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
                    else:
                        erro = "Nenhum dado encontrado para esta data específica."
                else:
                    erro = "Falha na comunicação com a base de dados da NASA."
            except Exception:
                erro = "Erro de conexão. Tente novamente em alguns instantes."

    return render_template('index.html', asteroides=dados_asteroides, data=data_pesquisa, erro=erro)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)