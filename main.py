# main.py
# Versão com sprites gráficos para as cartas e a mesa.

import pygame
import sys
import time
# Importamos as classes e também as constantes para montar os nomes dos arquivos
from classes_jogo import Jogador, Baralho
from constantes import VALORES, NAIPES

# --- 1. Inicialização e Configurações ---
pygame.init()

LARGURA_TELA, ALTURA_TELA = 1280, 720
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Blackjack Multiplayer Gráfico")

# Cores e Fontes
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (50, 50, 50)
COR_DESTAQUE = (255, 215, 0) # Dourado para destacar o jogador atual
fonte_padrao = pygame.font.SysFont('arial', 24)
fonte_titulo = pygame.font.SysFont('arial', 40)
fonte_msg = pygame.font.SysFont('arial', 35)

# --- 2. Carregar Assets (Imagens) ---
try:
    fundo_mesa = pygame.image.load('assets/fundo_mesa.png').convert()
    fundo_mesa = pygame.transform.scale(fundo_mesa, (LARGURA_TELA, ALTURA_TELA))
    
    costas_carta = pygame.image.load('assets/costas_carta.png').convert_alpha()
    # Ajuste o tamanho das cartas conforme necessário
    costas_carta = pygame.transform.scale(costas_carta, (90, 140))

    # Carrega todas as 52 cartas em um dicionário
    imagens_cartas = {}
    # Mapeia o símbolo do naipe para o nome do arquivo
    mapa_naipes = {'Copas ♥': 'copas', 'Ouros ♦': 'ouros', 'Paus ♣': 'paus', 'Espadas ♠': 'espadas'}

    for naipe_simbolo, naipe_arquivo in mapa_naipes.items():
        for valor in VALORES:
            nome_arquivo = f'assets/cards/{valor}_{naipe_arquivo}.png'
            chave = f'{valor}_{naipe_simbolo}'
            imagem = pygame.image.load(nome_arquivo).convert_alpha()
            imagens_cartas[chave] = pygame.transform.scale(imagem, (90, 140))

except pygame.error as e:
    print(f"Erro ao carregar assets: {e}")
    print("Verifique se a pasta 'assets' e todas as imagens estão no lugar e com os nomes corretos.")
    pygame.quit()
    sys.exit()


# --- 3. Funções Auxiliares de Desenho (Atualizadas) ---

def desenhar_texto(texto, fonte, cor, x, y, centrado=True):
    """Função para desenhar texto na tela."""
    superficie_texto = fonte.render(texto, True, cor)
    if centrado:
        retangulo_texto = superficie_texto.get_rect(center=(x, y))
    else:
        retangulo_texto = superficie_texto.get_rect(topleft=(x, y))
    tela.blit(superficie_texto, retangulo_texto)

def desenhar_mao(jogador, x_inicial, y, esconder_primeira=False):
    """Desenha a mão completa de um jogador usando as imagens carregadas."""
    for i, carta in enumerate(jogador.mao):
        pos_x = x_inicial + i * 40 # Cartas levemente sobrepostas
        if i == 0 and esconder_primeira:
            tela.blit(costas_carta, (pos_x, y))
        else:
            chave_carta = f'{carta.valor}_{carta.naipe}'
            tela.blit(imagens_cartas[chave_carta], (pos_x, y))

# --- Lógica do Jogo (O restante do código permanece quase igual) ---

# Botões (serão usados para detectar cliques)
botao_pedir_rect = pygame.Rect(LARGURA_TELA - 220, ALTURA_TELA - 150, 200, 60)
botao_parar_rect = pygame.Rect(LARGURA_TELA - 220, ALTURA_TELA - 80, 200, 60)
botao_prox_rodada_rect = pygame.Rect(LARGURA_TELA // 2 - 150, ALTURA_TELA // 2 - 30, 300, 60)

# Variáveis de estado do jogo
jogadores = [Jogador("Jogador 1", fichas=100), Jogador("Jogador 2", fichas=100)]
dealer = Jogador("Dealer")
baralho = None
jogadores_ativos = []
jogador_atual_idx = 0
fase_jogo = "INICIO"
mensagem = ""

def iniciar_nova_rodada():
    global baralho, jogadores_ativos, jogador_atual_idx, fase_jogo, mensagem
    baralho = Baralho()
    mensagem = ""
    jogadores_ativos = [j for j in jogadores if j.fichas > 0]
    if not jogadores_ativos:
        fase_jogo = "FIM_DE_JOGO"
        mensagem = "Todos os jogadores estão sem fichas!"
        return
    for jogador in jogadores_ativos:
        jogador.limpar_mao()
        jogador.aposta = 10
        jogador.fichas -= 10
    dealer.limpar_mao()
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
    global fase_jogo
    jogador_atual = jogadores_ativos[jogador_atual_idx]
    if jogador_atual.calcular_mao() >= 21:
        time.sleep(1)
        proximo_jogador()

# --- 4. O Laço Principal do Jogo (Game Loop) ---
rodando = True
clock = pygame.time.Clock()

while rodando:
    clock.tick(60)

    # --- A. Processamento de Eventos ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if fase_jogo == "JOGANDO":
                jogador_atual = jogadores_ativos[jogador_atual_idx]
                if botao_pedir_rect.collidepoint(evento.pos):
                    jogador_atual.adicionar_carta(baralho.distribuir_carta())
                    if jogador_atual.calcular_mao() >= 21:
                        proximo_jogador()
                elif botao_parar_rect.collidepoint(evento.pos):
                    proximo_jogador()
            
            elif fase_jogo in ["RESULTADO", "INICIO", "FIM_DE_JOGO"]:
                if botao_prox_rodada_rect.collidepoint(evento.pos):
                    if fase_jogo == "FIM_DE_JOGO":
                        rodando = False
                    else:
                        iniciar_nova_rodada()

    # --- B. Atualização da Lógica do Jogo ---
    if fase_jogo == "TURNO_DEALER":
        while dealer.calcular_mao() < 17:
            dealer.adicionar_carta(baralho.distribuir_carta())
        
        valor_dealer = dealer.calcular_mao()
        for jogador in jogadores_ativos:
            valor_jogador = jogador.calcular_mao()
            if valor_jogador > 21:
                pass
            elif valor_dealer > 21 or valor_jogador > valor_dealer:
                pagamento = int(jogador.aposta * 2.5) if valor_jogador == 21 and len(jogador.mao) == 2 else jogador.aposta * 2
                jogador.fichas += pagamento
            elif valor_jogador == valor_dealer:
                jogador.fichas += jogador.aposta
        
        fase_jogo = "RESULTADO"
        mensagem = "Rodada finalizada! Clique para continuar."

    # --- C. Desenho na Tela ---
    tela.blit(fundo_mesa, (0, 0)) # Desenha o fundo primeiro
    
    desenhar_texto("Mesa de Blackjack", fonte_titulo, BRANCO, LARGURA_TELA // 2, 40)

    # Mão do Dealer
    pontos_dealer_txt = str(dealer.calcular_mao()) if fase_jogo != 'JOGANDO' else '?'
    desenhar_texto(f"Dealer (Pontos: {pontos_dealer_txt})", fonte_padrao, BRANCO, LARGURA_TELA // 2, 100)
    desenhar_mao(dealer, LARGURA_TELA // 2 - 100, 130, esconder_primeira=(fase_jogo == "JOGANDO"))

    # Mãos dos Jogadores
    num_jogadores = len(jogadores_ativos) if fase_jogo != 'INICIO' else len(jogadores)
    for i, jogador in enumerate(jogadores_ativos if fase_jogo != 'INICIO' else jogadores):
        pos_x = (LARGURA_TELA // (num_jogadores + 1)) * (i + 1)
        
        # Desenha um fundo semi-transparente para o texto do jogador
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
    
    elif fase_jogo in ["RESULTADO", "INICIO", "FIM_DE_JOGO"]:
        pygame.draw.rect(tela, CINZA, botao_prox_rodada_rect, border_radius=10)
        texto_botao = "Iniciar Jogo" if fase_jogo == "INICIO" else "Próxima Rodada"
        if fase_jogo == "FIM_DE_JOGO": texto_botao = "Sair"
        desenhar_texto(texto_botao, fonte_padrao, BRANCO, botao_prox_rodada_rect.centerx, botao_prox_rodada_rect.centery)
        if mensagem:
            desenhar_texto(mensagem, fonte_msg, BRANCO, LARGURA_TELA // 2, ALTURA_TELA // 2 + 60)

    pygame.display.flip()

# --- 5. Finalização ---
pygame.quit()
sys.exit()
