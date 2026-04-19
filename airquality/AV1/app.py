import os
import numpy as np
from flask import Flask, request, jsonify
from joblib import load

# =============================== Objetivo: Prever CO(GT) ==================================== #

app = Flask(__name__)

medias = {
    #"CO(GT)": 2.1,
    "PT08.S1(CO)": 1098.1,
    #"NMHC(GT)": 40.7,
    "C6H6(GT)": 10.1,
    "PT08.S2(NMHC)": 937.7,
    "NOx(GT)": 239.3,
    "PT08.S3(NOx)": 834.2,
    "NO2(GT)": 109.6,
    "PT08.S4(NO2)": 1454,
    "PT08.S5(O3)": 1021.3,
    #"T": 18.3,
    #"RH": 49.2,
    #"AH": 1.0245,
}

desvio = {
    #"CO(GT)": 0.83,
    "PT08.S1(CO)": 213,
    #"NMHC(GT)": 86.7,
    "C6H6(GT)": 7.3,
    "PT08.S2(NMHC)": 261.7,
    "NOx(GT)": 194.1,
    "PT08.S3(NOx)": 251.8,
    "NO2(GT)": 44.6,
    "PT08.S4(NO2)": 339.5,
    "PT08.S5(O3)": 390.7,
    #"T": 8.6,
    #"RH": 17,
    #"AH": 0.4,
}

# Carregar o modelo
modelo_path = os.path.join('models', 'modelo2.pkl')
modelo = load(modelo_path)

def preprocessing(data):
    for coluna in ["Date", "Time", "CO(GT)", "NMHC(GT)", "T", "AH", "RH"]:
        data.pop(coluna, None) # Retirar colunas desnecessárias para a previsão se existirem
    for dado in data:
        if data[dado] > 0 and not np.isnan(data[dado]):
            dist_tolerancia = desvio[dado] * 2
            upper_outlier = medias[dado] + dist_tolerancia
            lower_outlier = medias[dado] - dist_tolerancia
            if data[dado] <= upper_outlier and data[dado] >= lower_outlier:
                continue
        data[dado] = medias[dado]
    return data

# Definir rota para receber requisições POST

@app.route('/predict', methods=['POST'])
def predict():
    # Receber dados JSON da requisição
    data = preprocessing(request.get_json())

    PT08S1 = data["PT08.S1(CO)"]
    C6H6 = data["C6H6(GT)"]
    PT08S2 = data["PT08.S2(NMHC)"]
    NOx = data["NOx(GT)"]
    PT08S3 = data["PT08.S3(NOx)"]
    NO2 = data["NO2(GT)"]
    PT08S4 = data["PT08.S4(NO2)"]
    PT08S5 = data["PT08.S5(O3)"]

    # Fazer a previsão usando o modelo
    predicao = modelo.predict([[PT08S1, C6H6, PT08S2, NOx, PT08S3, NO2, PT08S4, PT08S5]])

    # Mapear o resultado da previsão para uma resposta legível
    resultado = ['ruim' if pred > 9 else 'bom' if pred <= 4 else 'medio' for pred in predicao]

    # Retornar o resultado como JSON
    return jsonify(predicao.tolist() + resultado)

@app.route('/apidocs')
def inicio():
    return "Página inicial"

# Executar o aplicativo Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

'''
curl -X POST   -H "Content-Type: application/json"   -d @teste.json  http://localhost:5000/predict

curl -X POST   -H "Content-Type: application/json"   -d '{
    "Date": "11/03/2004",
    "Time": "08.00.00",
    "CO(GT)": 2.8,
    "PT08.S1(CO)": 1420,
    "NMHC(GT)": 165,
    "C6H6(GT)": 12.5,
    "PT08.S2(NMHC)": 1080,
    "NOx(GT)": 180,
    "PT08.S3(NOx)": 980,
    "NO2(GT)": 120,
    "PT08.S4(NO2)": 1750,
    "PT08.S5(O3)": 1350,
    "T": 14.2,
    "RH": 50.1,
    "AH": 0.7845
    }'   http://localhost:5000/predict
'''