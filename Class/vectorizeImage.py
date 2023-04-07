import cv2 as cv
# import generateCode
# import sendToRobot
import numpy as np

class vectorizeImage:
    def __init__(self, src) -> None:
        self.src = src
        self.img = cv.imread(self.src)

    def imageGetContour(self):     
        """
        "Descobre" o contorno da imagem escolhida e transforma em vetor. Isso para que o código que
            o robô ira receber para fazer o desenho vai utilizar os pontos do vetor para criar os pontos
            do programa.
        
        Retorna o vetor da imagem pronto.
        """                                                              #Vetoriza imagem utilizando tecnica de detecção de borda                                                                #Lê imagem do diretório
        self.img = cv.resize(self.img, (250  , 250))                                        #Redimenciona imagem 
        gray  = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY )                                   #Transforma a imagem em escala de cinza
        blur = cv.blur(gray, (3,3))                                                         #Aplica blur na imagem
        ret, thresh = cv.threshold(blur, 1, 255, cv.THRESH_OTSU) 
        contours, heirarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE) #Encontra borda
    

        contoursList = []   #Lista que irá receber cada objeto da imagem, vetorizado
        totalPoints = 0     #Total de pontos em que a imagem foi vetorizada  
        """ Essas duas variáveis a baixo, vão trabalhar na logica da aquisição dos pontos de cada objeto veotorizado na imagem.
        
        pointsReductionFactor -> É um fator que indica a quantidade de pontos que podem ser ignorados na formação de um
                                objeto. Por exemplo, caso seu valor seja 2, ele irá inercalar os pontos dos objetos. Supondo
                                que tenhamos 10 pontos, do p0 ao p9, o vetor resultante será : [p0, p2, p4, p6, p8].
                                Caso esse fator seja 3, ele ira salvar um ponto e ignorar 2: [p0, p3, p6, p9].
                                Dessa forma, é possível reduzir o total de pontos do objeto para reduzir o total de
                                pontos criados no código do robô.
        
        imageReduction -> Esse será o valor pelo qual cada coordenada será dividida. Isso faz com que a qauntidade de pontos
                        gerados em uma imagem com maior resolução, seja mantido em uma imagem menor. 

        Use dessas variaveis para descobrir qual se aplica melhor a sua situação.
        """
        pointsReductionFactor = 1
        imageReduction = 1

        for conteurs_ in contours:                                                  # Para cada objeto contido na imagem
            
            contoursTemp = []
            x = 0
            
            for i in conteurs_:                                                     #Para cada ponto de cada objeto
                if len(conteurs_) > pointsReductionFactor * pointsReductionFactor: #Garante que um objeto com menos pontos que o necessário passe pelo algoritimo de redução de pontos
                    #Lógica de reução de pontos
                    if x == 0: contoursTemp.append(np.array([[int(i[0][0]/imageReduction), int(i[0][1]/imageReduction)]])) 
                    x += 1
                    if x == pointsReductionFactor: x = 0
                else:
                    contoursTemp.append(np.array([[int(i[0][0]/imageReduction), int(i[0][1]/imageReduction)]]))

            if len(contoursTemp)  > 1: #Sinaliza quantidade de pontos do objeto atual e salva na lista final
                print("Pontos do objeto x antes e depois:", len(conteurs_), len(contoursTemp))
                totalPoints +=  len(contoursTemp)
                contoursList.append(np.array(contoursTemp))
            
        print("Pontos totais do desenho: ",totalPoints) #Lista quantos pontos totais foram criados para essa imagem
        return contoursList

    def resultImageShow(self, contoursList): 
        """
        Exibe a imagem original e a imagem vetorizada em 2 janelas diferentes, apenas para visualização.
        
        :param contoursList: Lista que contem os contornos criada pelo método imageGetContour.
        """

        #Exibe as imagens
        img_1 = np.zeros([300,300,1],dtype=np.uint8)
        img_1.fill(255)
        cv.drawContours(img_1, contoursList, -1, (0,0,255), 1)
        print(contoursList[0])
        # show the image
        cv.namedWindow('Contours',cv.WINDOW_NORMAL)
        cv.namedWindow('Thresh',cv.WINDOW_NORMAL)
        cv.imshow('Contours', img_1)
        cv.imshow('Thresh', self.img)
        if cv.waitKey(0):
            cv.destroyAllWindows()

        

        # draw = generateCode.generateCode([160, -169, 444.29],0,contoursList)
        # listComands = draw.generateCode()
        # print(listComands)
        
        # sendToRobot.sendToRobot(listComands)

if __name__ == "__main__":
    vetorizar = vectorizeImage("img/testeImg.png")
    lista = vetorizar.imageGetContour()
    # vetorizar.resultImageShow()
    vetorizar.resultImageShow(lista)
    pass