import socket
import time


class sendToRobot():
    def __init__(self, listToSend, codeName = "5", HOST = "192.168.2.40", PORT = 10001 ) -> None:
        """Envia para o robô em requisições de no máximo 254 Bytes todo o código em MBV (Melfa Basic V)
        referente ao desenho que deve ser feito. No mometo que a classe é instanciada, o código é enviado
        ao controlador do robô e o robô inicia o programa.s

        :param listToSend: Lista contendo o código em MBV, já quebrado em blocos de no máximo 254 Bytes.
        :param codeName: Nome que será dado ao código no controlador
        :param HOST: ip do robô
        :param PORT: Porta do controlador referente ao protocolo MXT
        """
        self.listToSend = listToSend
        self.codeName = codeName
        self.HOST = HOST
        self.PORT = PORT

        self.socketRobo = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Instancia socket
        self.socketRobo.connect((HOST, PORT))                               #Efetua conexão com o robô

        self.initConnection()                                 #Envia sequencia de comandos referentes a preparação do controlador para receber o código
        self.sendCodeToRobot(self.listToSend, self.codeName) #Envia o código ao controlador
        self.runCode(self.codeName)                          #Roda o código
    
    def initConnection(self):
        """Envia para o controlador do robô uma lista de comandos, preparando o mesmo para
        receber o código de desenho da imagem, que virá a seguir.
        """

        list = [  #Lista de comandos a ser enviada para o controlador do robô via requisição.
        "1;1;OPEN=NARCUSR",
        "1;1;PARRLNG",
        "1;1;PDIRTOP",
        "1;1;PPOSF",
        "1;1;PARMEXTL",
        "1;1;PARRBSERIAL",
        "1;1;VALP_BASE",
        "1;1;KEYWDptest",
        ]

        self.sendListComands(list) #Envia os comandos.

    def sendCodeToRobot(self, listToSend,codeName):
        """Envia código ao robô.
        :param listToSend: Lista contendo o código em MBV, já quebrado em blocos de no máximo 254 Bytes.
        :param codeName: Nome que será dado ao código no controlador
        """

        list1 = [#Lista de comandos referente a criação de um novo programa no controlador
            "1;1;NEW",
            "1;1;LOAD=" + codeName,
            "1;1;PRTVERLISTL",
            "1;1;PRTVEREMDAT",
            "1;9;LISTL<",
                ]
        
        list2 = [#Lista de comandos referente ao salvamento do programa enviado
            "1;1;SAVE",
            "1;1;PDIRTOP",
            "1;1;PDIR1"
            ]
 
        self.sendListComands(list1) #Envia lista de payload referente a criação do programa
        self.sendListComands(listToSend) #Enviando lista de payloads referente ao programa
        self.sendListComands(list2) #Enviando lista de payloads referente ao salvamento do programa criado no controlador

    def runCode(self, codeName):
        """Faz o controlador armar o braço robótico e iniciar o programa anterioremente criado.

        :param codeName: Nome que será dado ao código no controlador
        """
        list1 = ["1;1;CNTLON" , #Lista de payloads referentes a preparar o braço para iniciar programa
            "1;1;EXECSPD 100"  ,
            "1;1;EXECACCEL 100", 
            "1;1;SRVON"]
        
        list2 =[ #Lista de comandos referentes a rodar o programa
            "1;1;PRGLOAD=" + codeName ,
            "1;1;RUN"  ]
        
        self.sendListComands(list1) #Envia lista 1
        time.sleep(2)
        self.sendListComands(list2) #Envia Lista 2

    def sendListComands(self, list):
        """Esse método faz requisições ao controlador do robô, em cima de uma lista de payloads.
        :param list: Lista que contem payload de cada requisição que esse método deve fazer.
        """
        for i in list: #Para cada payload, efetuar um envio
            # print(bytes(i, encoding='utf-8'))
            self.socketRobo.sendall(bytes(i, encoding='utf-8')) #Envia payload
            data = self.socketRobo.recv(1024)                   #Aguarda reasposta
            print(f"Received {data!r}") #Printa resposta (a mesma dele ver Ok)
            
    