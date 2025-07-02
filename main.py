# main.py
# Versão com sistema de apostas, limite de rodadas e eliminação de jogadores.

import pygame
import sys
import time
from classes_jogo import Jogador, Baralho
from constantes import VALORES, NAIPES

# --- 1. Inicialização e Configurações ---
pygame.init()

LARGURA_TELA, ALTURA_TELA = 1280, 720
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Blackjack Multiplayer - Rodadas")

# Cores e Fontes
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (50, 50, 50)
COR_DESTAQUE = (255, 215, 0)
COR_INPUT_ATIVO = pygame.Color('lightskyblue3')
COR_INPUT_INATIVO = pygame.Color('gray15')
fonte_padrao = pygame.font.SysFont('arial', 24)
fonte_titulo = pygame.font.SysFont('arial', 40)
fonte_msg = pygame.font.SysFont('arial', 35)

# --- 2. Carregar Assets (Imagens) ---
try:
    fundo_mesa = pygame.image.load('assets/fundo_mesa.png').convert()
    fundo_mesa = pygame.transform.scale(fundo_mesa, (LARGURA_TELA, ALTURA_TELA))
    costas_carta = pygame.image.load('assets/costas_carta.png').convert_alpha()
    costas_carta = pygame.transform.scale(costas_carta, (90, 140))
    imagens_cartas = {}
    mapa_naipes = {'Copas ♥': 'copas', 'Ouros ♦': 'ouros', 'Paus ♣': 'paus', 'Espadas ♠': 'espadas'}
    for naipe_simbolo, naipe_arquivo in mapa_naipes.items():
        for valor in VALORES:
            nome_arquivo = f'assets/cards/{valor}_{naipe_arquivo}.png'
            chave = f'{valor}_{naipe_simbolo}'
            imagem = pygame.image.load(nome_arquivo).convert_alpha()
            imagens_cartas[chave] = pygame.transform.scale(imagem, (90, 140))
except pygame.error as e:
    print(f"Erro ao carregar assets: {e}")
    pygame.quit()
    sys.exit()

# --- 3. Funções Auxiliares de Desenho ---
def desenhar_texto(texto, fonte, cor, x, y, centrado=True):
    superficie_texto = fonte.render(texto, True, cor)
    retangulo_texto = superficie_texto.get_rect(center=(x, y)) if centrado else superficie_texto.get_rect(topleft=(x, y))
    tela.blit(superficie_texto, retangulo_texto)

def desenhar_mao(jogador, x_inicial, y, esconder_primeira=False):
    for i, carta in enumerate(jogador.mao):
        pos_x = x_inicial + i * 40
        if i == 0 and esconder_primeira:
            tela.blit(costas_carta, (pos_x, y))
        else:
            chave_carta = f'{carta.valor}_{carta.naipe}'
            tela.blit(imagens_cartas[chave_carta], (pos_x, y))

# --- 4. Lógica e Estado do Jogo ---

# Constantes do Jogo
TOTAL_RODADAS = 20

# Botões e Caixas de Input
botao_pedir_rect = pygame.Rect(LARGURA_TELA - 220, ALTURA_TELA - 150, 200, 60)
botao_parar_rect = pygame.Rect(LARGURA_TELA - 220, ALTURA_TELA - 80, 200, 60)
botao_confirmar_aposta_rect = pygame.Rect(LARGURA_TELA // 2 - 100, ALTURA_TELA // 2 + 40, 200, 50)
input_aposta_rect = pygame.Rect(LARGURA_TELA // 2 - 100, ALTURA_TELA // 2 - 20, 200, 50)

# Variáveis de estado do jogo
jogadores = [Jogador("Jogador 1", fichas=1000), Jogador("Jogador 2", fichas=1000)]
dealer = Jogador("Dealer")
baralho = None
jogadores_ativos = []
jogador_atual_idx = 0
jogador_aposta_idx = 0
rodada_atual = 0
fase_jogo = "INICIO"
mensagem = ""
input_aposta_texto = ""
input_aposta_ativo = False

def setup_nova_rodada():
    global rodada_atual, jogadores_ativos, jogador_aposta_idx, fase_jogo, mensagem, input_aposta_texto
    rodada_atual += 1
    if rodada_atual > TOTAL_RODADAS:
        fase_jogo = "FIM_DE_JOGO"
        return

    jogadores_ativos = [j for j in jogadores if j.fichas > 0]
    if len(jogadores_ativos) <= 1:
        fase_jogo = "FIM_DE_JOGO"
        return

    for jogador in jogadores_ativos:
        jogador.limpar_mao()
    dealer.limpar_mao()
    
    jogador_aposta_idx = 0
    input_aposta_texto = ""
    mensagem = ""
    fase_jogo = "APOSTAS"

def distribuir_cartas():
    global baralho, jogador_atual_idx, fase_jogo
    baralho = Baralho()
    for _ in range(2):
        for jogador in jogadores_ativos:
            jogador.adicionar_carta(baralho.distribuir_carta())
        dealer.adicionar_carta(baralho.distribuir_carta())
    jogador_atual_idx = 0
    fase_jogo = "JOGANDO"
    verificar_turno_jogador()

def proximo_jogador():
    global jogador_atual_idx, fase_jogo
    jogador_atual_idx += 1
    if jogador_atual_idx >= len(jogadores_ativos):
        fase_jogo = "TURNO_DEALER"
    else:
        verificar_turno_jogador()

def verificar_turno_jogador():
    jogador_atual = jogadores_ativos[jogador_atual_idx]
    if jogador_atual.calcular_mao() >= 21:
        time.sleep(1)
        proximo_jogador()

# --- 5. O Laço Principal do Jogo (Game Loop) ---
rodando = True
clock = pygame.time.Clock()

while rodando:
    clock.tick(60)

    # --- A. Processamento de Eventos ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        
        # --- Eventos de Aposta ---
        if fase_jogo == "APOSTAS":
            if evento.type == pygame.MOUSEBUTTONDOWN:
                input_aposta_ativo = input_aposta_rect.collidepoint(evento.pos)
                if botao_confirmar_aposta_rect.collidepoint(evento.pos):
                    try:
                        aposta = int(input_aposta_texto)
                        jogador_que_aposta = jogadores_ativos[jogador_aposta_idx]
                        if 0 < aposta <= jogador_que_aposta.fichas:
                            jogador_que_aposta.aposta = aposta
                            jogador_que_aposta.fichas -= aposta
                            jogador_aposta_idx += 1
                            input_aposta_texto = ""
                            if jogador_aposta_idx >= len(jogadores_ativos):
                                distribuir_cartas()
                        else:
                            mensagem = "Aposta inválida ou fichas insuficientes."
                    except ValueError:
                        mensagem = "Por favor, digite um número."
            if evento.type == pygame.KEYDOWN and input_aposta_ativo:
                if evento.key == pygame.K_BACKSPACE:
                    input_aposta_texto = input_aposta_texto[:-1]
                elif evento.unicode.isdigit():
                    input_aposta_texto += evento.unicode
        
        # --- Eventos de Jogo ---
        elif fase_jogo == "JOGANDO":
            if evento.type == pygame.MOUSEBUTTONDOWN:
                jogador_atual = jogadores_ativos[jogador_atual_idx]
                if botao_pedir_rect.collidepoint(evento.pos):
                    jogador_atual.adicionar_carta(baralho.distribuir_carta())
                    if jogador_atual.calcular_mao() >= 21:
                        proximo_jogador()
                elif botao_parar_rect.collidepoint(evento.pos):
                    proximo_jogador()
        
        # --- Eventos de Fim de Rodada/Jogo ---
        elif fase_jogo in ["RESULTADO", "INICIO"]:
            if evento.type == pygame.MOUSEBUTTONDOWN:
                setup_nova_rodada()
        
        elif fase_jogo == "FIM_DE_JOGO":
             if evento.type == pygame.MOUSEBUTTONDOWN:
                 rodando = False


    # --- B. Lógica de Jogo Automática ---
    if fase_jogo == "TURNO_DEALER":
        while dealer.calcular_mao() < 17:
            dealer.adicionar_carta(baralho.distribuir_carta())
        valor_dealer = dealer.calcular_mao()
        for jogador in jogadores_ativos:
            valor_jogador = jogador.calcular_mao()
            if valor_jogador > 21: pass
            elif valor_dealer > 21 or valor_jogador > valor_dealer:
                pagamento = int(jogador.aposta * 2.5) if valor_jogador == 21 and len(jogador.mao) == 2 else jogador.aposta * 2
                jogador.fichas += pagamento
            elif valor_jogador == valor_dealer:
                jogador.fichas += jogador.aposta
        fase_jogo = "RESULTADO"
        mensagem = "Rodada finalizada! Clique para continuar."

    # --- C. Desenho na Tela ---
    tela.blit(fundo_mesa, (0, 0))
    desenhar_texto(f"Rodada {rodada_atual} / {TOTAL_RODADAS}", fonte_titulo, BRANCO, LARGURA_TELA // 2, 40)

    if fase_jogo == "INICIO":
        desenhar_texto("Bem-vindo ao Blackjack!", fonte_titulo, BRANCO, LARGURA_TELA // 2, ALTURA_TELA // 2 - 40)
        desenhar_texto("Clique em qualquer lugar para começar", fonte_padrao, BRANCO, LARGURA_TELA // 2, ALTURA_TELA // 2 + 20)
    
    elif fase_jogo == "APOSTAS":
        jogador_que_aposta = jogadores_ativos[jogador_aposta_idx]
        desenhar_texto(f"Vez de {jogador_que_aposta.nome} apostar", fonte_titulo, BRANCO, LARGURA_TELA // 2, ALTURA_TELA // 2 - 150)
        desenhar_texto(f"Você tem {jogador_que_aposta.fichas} fichas", fonte_padrao, BRANCO, LARGURA_TELA // 2, ALTURA_TELA // 2 - 100)
        
        cor_input = COR_INPUT_ATIVO if input_aposta_ativo else COR_INPUT_INATIVO
        pygame.draw.rect(tela, cor_input, input_aposta_rect, border_radius=5)
        desenhar_texto(input_aposta_texto, fonte_padrao, BRANCO, input_aposta_rect.centerx, input_aposta_rect.centery)
        
        pygame.draw.rect(tela, CINZA, botao_confirmar_aposta_rect, border_radius=10)
        desenhar_texto("Confirmar Aposta", fonte_padrao, BRANCO, botao_confirmar_aposta_rect.centerx, botao_confirmar_aposta_rect.centery)
        if mensagem:
            desenhar_texto(mensagem, fonte_padrao, (255, 100, 100), LARGURA_TELA // 2, ALTURA_TELA // 2 + 110)

    elif fase_jogo == "FIM_DE_JOGO":
        vencedor = max(jogadores, key=lambda j: j.fichas)
        desenhar_texto("FIM DE JOGO!", fonte_titulo, COR_DESTAQUE, LARGURA_TELA // 2, ALTURA_TELA // 2 - 100)
        desenhar_texto(f"O vencedor é {vencedor.nome} com {vencedor.fichas} fichas!", fonte_msg, BRANCO, LARGURA_TELA // 2, ALTURA_TELA // 2)
        desenhar_texto("Clique para sair", fonte_padrao, BRANCO, LARGURA_TELA // 2, ALTURA_TELA // 2 + 60)
        
    else: # Fases JOGANDO, TURNO_DEALER, RESULTADO
        # Mão do Dealer
        pontos_dealer_txt = str(dealer.calcular_mao()) if fase_jogo != 'JOGANDO' else '?'
        desenhar_texto(f"Dealer (Pontos: {pontos_dealer_txt})", fonte_padrao, BRANCO, LARGURA_TELA // 2, 100)
        desenhar_mao(dealer, LARGURA_TELA // 2 - 100, 130, esconder_primeira=(fase_jogo == "JOGANDO"))

        # Mãos dos Jogadores
        for i, jogador in enumerate(jogadores_ativos):
            pos_x = (LARGURA_TELA // (len(jogadores_ativos) + 1)) * (i + 1)
            fundo_texto = pygame.Surface((300, 150), pygame.SRCALPHA)
            fundo_texto.fill((0, 0, 0, 120))
            tela.blit(fundo_texto, (pos_x - 150, ALTURA_TELA - 170))
            
            desenhar_texto(f"{jogador.nome}", fonte_padrao, BRANCO, pos_x, ALTURA_TELA - 150)
            desenhar_texto(f"Fichas: {jogador.fichas}", fonte_padrao, BRANCO, pos_x, ALTURA_TELA - 120)
            desenhar_texto(f"Aposta: {jogador.aposta}", fonte_padrao, BRANCO, pos_x, ALTURA_TELA - 90)
            desenhar_texto(f"Pontos: {jogador.calcular_mao()}", fonte_padrao, BRANCO, pos_x, ALTURA_TELA - 60)
            
            desenhar_mao(jogador, pos_x - 100, ALTURA_TELA - 330)
            
            if fase_jogo == "JOGANDO" and i == jogador_atual_idx:
                pygame.draw.rect(tela, COR_DESTAQUE, (pos_x - 150, ALTURA_TELA - 340, 300, 300), 4, border_radius=10)

        # Botões e Mensagens
        if fase_jogo == "JOGANDO":
            pygame.draw.rect(tela, CINZA, botao_pedir_rect, border_radius=10)
            pygame.draw.rect(tela, CINZA, botao_parar_rect, border_radius=10)
            desenhar_texto("Pedir", fonte_padrao, BRANCO, botao_pedir_rect.centerx, botao_pedir_rect.centery)
            desenhar_texto("Parar", fonte_padrao, BRANCO, botao_parar_rect.centerx, botao_parar_rect.centery)
        
        elif fase_jogo == "RESULTADO":
            desenhar_texto(mensagem, fonte_msg, BRANCO, LARGURA_TELA // 2, ALTURA_TELA // 2)

    pygame.display.flip()

# --- 6. Finalização ---
pygame.quit()
sys.exit()
