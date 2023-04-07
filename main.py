
import paho.mqtt.client as mqtt #Biblioteca para comunicação MQTT
import time
from googletrans import Translator, constants
import requests
import json

from Class import vectorizeImage, sendToRobot, generateCode

import os
from dotenv import load_dotenv

translator = Translator()

Broker = os.getenv("BROKER_MQTT")           #Ip do broker no raspberry
PortaBroker = int(os.getenv("PORT_MQTT"))        #Porta do broker
TopicoSubscribe = os.getenv("TOPIC_MQTT")   #Topíco que a central ficara inscrita aguardando mensagens 
username = os.getenv("USERNAME_MQTT")       #Para brokers mqtt com autentiação, é necessário login e senhaz
password = os.getenv("PASSWORD_MQTT")
KeepAliveBroker = 60       

APIKEY = os.getenv("APIKEY_DALLE")          #API KEY para utilização do serviço de geração de imagens DALL-E 2 

def generateImage(prompt): #Função para requisição a API em cima da mensagem enviada pela skill da alexa
    req = requests.post("https://api.openai.com/v1/images/generations", headers={
        "Content-Type" : "application/json",
        "Authorization" : f"Bearer  {APIKEY}"
    }, json={                   
          "prompt": f"{prompt}, one line, black nd white", #AQUI ENTRA O PROMPT JÁ EM INGLES PARA GERAÇÃO DA IMAGEM
            "n": 1,                                        #Numero de imagens a serem geradas 
            "size": "256x256"                              #Resolução da imagem
    })

    print(req.text) #Resultado da requisição
    try:
        url = json.loads(req.text)['data'][0]["url"] #Capturar a URL da imagem gerada pelo DALL-E 2

        img_data = requests.get(url).content         #Download da imagem a partir da URL
        src  = f"img/{prompt}.jpg"                   #Diretório onde a imagem será salva, seu nome será o prompt
        
        with open(src, 'wb') as handler:             #Salva imagem no diretório escolhido
            handler.write(img_data)

        vetorizar = vectorizeImage(src)              #Instancia a classe responsável por vetorizar a imagem
        imgList = vetorizar.imageGetContour()          #Utiliza detecção de bordas para formas o vetor da imagem a ser desenhada
        # vetorizar.resultImageShow()                #Mostra o previwe da imagem (apenas para visulização)
        
        draw = generateCode.generateCode([160, -169, 444.29],0,imgList) #Instancia classe que irá gerar código de desenho
        listComands = draw.generateCode()                               #Gera o código de desenho
        sendToRobot.sendToRobot(listComands)                            #Envia códio para o robô


    except:
        print("Houve um problema com a aquisição da URL e o download da imagem.")

def on_connect(client, userdata, flags, rc): 
    print(f"[STATUS] Conectado ao Broker. Resultado de conexao: {str(rc)}") #Printa o resultado da conexão
    client.subscribe(TopicoSubscribe)                                     #Se inscreve nom tópico escolhido

def on_message(client, userdata, message):
    translation = translator.translate(text=str(message.payload.decode("utf-8")), dest="en")        #Traduz para ingles a mensagem recebida por MQTT
    print(f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")  
    generateImage(translation.text)                                                                 #Chama a função de gerar imagem pelo DALL-E 2   


if __name__ == "__main__":
    print("Iniciando MQTT...")
    client = mqtt.Client()           #Instancia da classe da biblioteca MQTT
    client.on_connect = on_connect   #Definição da função que será execultada no momento que a central conectar com o broker
    client.on_message = on_message   #Definção da função que será execultada quando a central receber alguma mensagem no tópico cdastrado

    while True:
        try: 
            client.username_pw_set(username=username, password=password) #Seta o login e senha para conexaõ com o broker
            client.connect(Broker, PortaBroker, KeepAliveBroker)         #Tenta conectar com o broker
            client.loop_forever()                                        #Loop do mqtt
        except: 
            print("Falha no MQTT, tentando reconectar em 5 segundos...") 
            time.sleep(5)       

