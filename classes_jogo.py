import random
from constantes import NAIPES, VALORES, VALOR_CARTA

class Carta:

    def __init__(self, valor, naipe):

        self.valor = valor
        self.naipe = naipe

    def __str__(self):

        return f'{self.valor} de {self.naipe}'

class Baralho:

    def __init__(self):
        self.cartas = []

        for naipe in NAIPES:
            for valor in VALORES:
                self.cartas.append(Carta(valor, naipe))
        self.embaralhar()

    def embaralhar(self):

        random.shuffle(self.cartas)
    
    def distribuir_carta(self):

        if self.cartas:
            return self.cartas.pop()
        return None

class Jogador:
    
    def __init__(self, nome, fichas = 0):

        self.nome = nome
        self.fichas = fichas
        self.mao = []
        self.aposta = 0

    def adicionar_carta(self, carta):

        self.mao.append(carta)

    def calcular_mao(self):

        valor = sum(VALOR_CARTA[carta.valor] for carta in self.mao)
        num_ases = sum(1 for carta in self.mao if carta.valor == 'A')

        while valor > 21 and num_ases > 0:
            valor -= 10
            num_ases -= 1
        return valor
    
    def limpar_mao(self):

        self.mao = []
        self.aposta = 0