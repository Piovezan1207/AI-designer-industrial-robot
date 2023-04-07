class generateCode():
    def __init__(self, referencePosition, maxSize, imageContour) -> None:
        """ Gera o código que será enviado ao robô, a partir do vetor criado com a imagem.

        :param referencePosition: Posição [X,Y,Z] do ponto onde o desenho será iniciado (canto superior esquerdo do papel) 
        :param maxSize: - 
        :param imageContour: Contorno da imagem feito pelo algoritimo de deteção de borda
        """
        self.referencePosition = referencePosition #Posição de referencia para do robô iniciar o desenho (considerar canto superior direito da area o ponto 0,0 do desenho)
        self.maxSize = maxSize 
        self.imageContour = imageContour           #Contorno da imagem feito pelo algoritimo de deteção de borda
        self.listToSend = [] 
        self.stringToSend = "1;9;EMDAT"
        self.nCaracterAdd = 0
        self.programLineNumber = 1


    def line(self):
        """Cria uma string para formatar uma linha do código MBV. cada linha de código deve ser numerada,
        para que o controlador consiga coordenar o código em ordem. A sua unica função é verificar o numero
        da linha atual e retornar em uma string.
        """
        actualNumber = self.programLineNumber 
        self.programLineNumber += 1
        return "{} ".format(actualNumber)
    
    def generateCode(self):

        pointNumber = 0

        flagNpoint = False
        fristObjPoint = []
        lastObjPoint = []

        for oneContour in self.imageContour: #Para cada contorno que forma a imagem
            for position in oneContour:      #Para cada posição de cada contorno
                position = position[0]

                if not flagNpoint:                    #Para todo o primeiro ponto de cada objeto
                    fristObjPoint.append(pointNumber) #Salva o numero desse ponto em um vetor
                    flagNpoint = True

                """
                    Cria a linha de comando em MBV (Melfa Basic V, a lingiagem de programação dos robôs mitsubishi)
                Essa linha cria um ponto X a sintaxa é  < P1 = (0.00,0.00,0.00,-180.00,+0.00,-180.00) >
                Um ponto é referente as coordenadas X Y Z A B C de uma posição cartesiana, sendo A, B e C os angulos em torno de cada eixo do grafico.
                """
                pointPosition = "P{} = ({},{},{},-180,+0,-180)\x0b".format(pointNumber, self.referencePosition[0]+position[1], self.referencePosition[1]+position[0], self.referencePosition[2])
                #Adicicona essa posição criada a lista final de código, a partir do método 'verifyMaxCaracterAndAppendToList()'
                self.verifyMaxCaracterAndAppendToList(pointPosition) 

                pointNumber += 1
        
            lastObjPoint.append(pointNumber-1)  #Todo o ultimo ponto de um objeto,é salvo em um vetor
            flagNpoint = False                  #Reseta a flag utilizada para saber qual o primeiro ponto


           
        fristPointTemp = 0
        for i in range(pointNumber):    #Para todos os pontos criados
            if i in fristObjPoint:      #Caso o numero do ponto atual seja equivalente a uma posição que corresponde a posição INICIAL de um contorno de um objeto
                fristPointTemp = i      #Salva esse ponto em uma variavel temporaria
                """Aplica a lógica de aproximação da caneta. Sabendo que esse é o primeir ponto de um desenho, o robô
                deve se aproximar dele em um movimento aéreo, para então, tocar o papel.
                """
                self.verifyMaxCaracterAndAppendToList('MVS P{}, -10\x0b'.format (i)) #Se aproxima do ponto, 10mm a cima dele no eixo Z
                self.verifyMaxCaracterAndAppendToList('DLY 0.1\x0b')                 #Pequeno delay para travar movimento do robô e preservar desenho

            self.verifyMaxCaracterAndAppendToList('MVS P{}\x0b'.format(i))           #Move o robô para o pono desejado, na altura em que a caneta toca o papel
            self.verifyMaxCaracterAndAppendToList('DLY 0.1\x0b')                     #Delay

            if i in lastObjPoint:  #Caso o numero do ponto atual seja equivalente a uma posição que corresponde a posição FINAL de um contorno de um objeto
                """Por se tratar da ultima posição de um contorno, o próximo ponto seria o primeiro, assim, fechando o contorno.
                A lógica a seguir efetua exatamente esse movimento, move o robô para o primeiro ponto e levanta a caneta do papel,
                garantindo que o robô não fara riscos indesejados no momento de começar o próximo contorno.
                """
                self.verifyMaxCaracterAndAppendToList('MVS P{}\x0b'.format(fristPointTemp)) #Move para o primeiro ponto do contorno
                self.verifyMaxCaracterAndAppendToList('DLY 0.1\x0b')                        #delay
                self.verifyMaxCaracterAndAppendToList('MVS P{}, -10\x0b'.format(fristPointTemp)) #Levanta a caneta do papel
                self.verifyMaxCaracterAndAppendToList('DLY 0.1\x0b')                             #Delay
            
            #O for segue até que todos os pontos tenham sido incluidos no código.

        """Após todos os pontos serem adicionados na movimentação do robô, o desenho estará pronto. O próximo passo
        é o robô ir para uma posição alta (para que seja possivel remover a folha da mesa) e o fim do programa.
        """
        self.verifyMaxCaracterAndAppendToList('MVS P{}, -100\x0b'.format(fristPointTemp)) #Move para 100mm a cima do ultimo ponto desenhado
        self.verifyMaxCaracterAndAppendToList('DLY 0.1\x0b')                              #delay
        self.verifyMaxCaracterAndAppendToList('DLY 10\x0b')                               #Delay maior para garantir que o programa seja realemnte parado caso o controlador rode em loop 
        self.verifyMaxCaracterAndAppendToList('end\x0b')                                  #Sinaliza o final do programa
        pointNumber = 0                                                                   #Zera a variavel de numero do ponto

        self.listToSend.append(self.stringToSend) #Adiciona a ultima string formatada para a requisição
        return self.listToSend                    #Retorna a lista contendo todo o código, separado de forma a ser enviado em varias requisições

    def verifyMaxCaracterAndAppendToList(self, line):
        """Para enviar um programa ao controlador do robô via rede, não se basta apernas uma string bruta, contendo
        todos os comandos necessários. As requisições que enviarão o código devem ser quebradas de acordo com seu tamanho
        em Bytes (254 Bytes no máximo por requisição).


        """
        #Forma a string da linha, utilizando o métoo "line", que retorna uma string com o npumero atual da liha no programa, concatenando o comando que veio como parametro nesse método.
        line = self.line() + line 
        if  not len(self.stringToSend) == 0: #Caso não seja a primeira linha criada do programa   
            if len(self.stringToSend) + len(line) < 254: #caso ainda haja Bytes disponíveis no corpo da requisição para esse trecho novo
                self.stringToSend += line #adiciona nova linha e código
                
            else:#Caso não haja mais espaço nessa requisição
                self.listToSend.append(self.stringToSend) #Salva a string formada até agora em uma lista

                #Cria uma nova string zerada, que será enviada em outra requisição
                """ No inicio de cada trecho de código enviado, deve-se conter uma string que é um comando ao controlador
                do robô. Essa string é "1;9;EMDAT", que sinaliza o controlador que está sendo enviado um trecho de código MBV."""
                self.stringToSend = "1;9;EMDAT"
                self.stringToSend += line
                 
        else:#Caso seja a primeira linha, a string "stringToSend" já contem o "1;9;EMDAT" no seu inicio.
            self.stringToSend += line



    #x [0][0][0][1] - Vertical
    #y [0][0][0][0] - Horizontal