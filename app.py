from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    dados_asteroides = []
    data_pesquisa = ""
    erro = None

    if request.method == 'POST':
        data_pesquisa = request.form.get('data')
        
        api_key = os.environ.get('NASA_API_KEY', "faZ5X3HvBrJ32ynZMH7lp08wBESv3ZOdKmXuf6f3") 
        
        link_api = "https://api.nasa.gov/neo/rest/v1/feed"
        
        parametros = {
            'start_date': data_pesquisa,
            'end_date': data_pesquisa,
            'api_key': api_key
        }

        try:
            resposta = requests.get(link_api, params=parametros, timeout=10)

            if resposta.status_code == 200:
                dados_requisicao = resposta.json()
                
                if data_pesquisa in dados_requisicao['near_earth_objects']:
                    dados_asteroides = dados_requisicao['near_earth_objects'][data_pesquisa]
                else:
                    erro = f"Nenhum asteroide detectado para a data {data_pesquisa}. O céu está limpo!"
            else:
                erro = f"Erro na NASA: Status {resposta.status_code}. Talvez a chave tenha expirado?"
        
        except requests.exceptions.RequestException as e:
            erro = "Falha na conexão com o servidor da NASA. Verifique sua internet."

    return render_template('index.html', asteroides=dados_asteroides, data=data_pesquisa, erro=erro)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)