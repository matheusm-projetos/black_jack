import pygame
import sys
import time

from classes_jogo import Jogador, Baralho


pygame.init()


LARGURA_TELA, ALTURA_TELA = 1280, 720
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Blackjack Multiplayer")

COR_FUNDO = (0, 102, 0)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (200, 0, 0)
CINZA = (50, 50, 50)
fonte_padrao = pygame.font.SysFont('arial', 24)
fonte_carta = pygame.font.SysFont('arial', 30)
fonte_titulo = pygame.font.SysFont('arial', 40)
fonte_msg = pygame.font.SysFont('arial', 35)

def desenhar_texto(texto, fonte, cor, x, y):
    """Função para desenhar texto na tela."""
    superficie_texto = fonte.render(texto, True, cor)
    retangulo_texto = superficie_texto.get_rect(center=(x, y))
    tela.blit(superficie_texto, retangulo_texto)

def desenhar_carta(carta, x, y):
    """Desenha uma única carta na tela (como um retângulo com texto)."""
    cor_carta = VERMELHO if carta.naipe in ('Copas ♥', 'Ouros ♦') else PRETO
    ret_carta = pygame.Rect(x, y, 90, 140)
    pygame.draw.rect(tela, BRANCO, ret_carta)
    pygame.draw.rect(tela, PRETO, ret_carta, 2)

    texto_valor = fonte_carta.render(carta.valor, True, cor_carta)
    texto_naipe = fonte_carta.render(carta.naipe.split(' ')[1], True, cor_carta)
    tela.blit(texto_valor, (x + 10, y + 10))
    tela.blit(texto_naipe, (x + 10, y + 50))

def desenhar_mao(jogador, x_inicial, y, esconder_primeira=False):
    """Desenha a mão completa de um jogador."""
    for i, carta in enumerate(jogador.mao):
        if i == 0 and esconder_primeira:

            ret_verso = pygame.Rect(x_inicial + i * 40, y, 90, 140)
            pygame.draw.rect(tela, VERMELHO, ret_verso)
            pygame.draw.rect(tela, BRANCO, ret_verso, 3)
        else:
            desenhar_carta(carta, x_inicial + i * 40, y)

botao_pedir_rect = pygame.Rect(LARGURA_TELA - 220, ALTURA_TELA - 150, 200, 60)
botao_parar_rect = pygame.Rect(LARGURA_TELA - 220, ALTURA_TELA - 80, 200, 60)
botao_prox_rodada_rect = pygame.Rect(LARGURA_TELA // 2 - 150, ALTURA_TELA // 2 - 30, 300, 60)

jogadores = [Jogador("Jogador 1", fichas=100), Jogador("Jogador 2", fichas=100)]
dealer = Jogador("Dealer")
baralho = None
jogadores_ativos = []
jogador_atual_idx = 0
fase_jogo = "INICIO"
mensagem = ""

def iniciar_nova_rodada():
    """Prepara tudo para uma nova rodada."""
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
    """Passa para o próximo jogador ou para o turno do dealer."""
    global jogador_atual_idx, fase_jogo
    
    jogador_atual_idx += 1
    if jogador_atual_idx >= len(jogadores_ativos):
        fase_jogo = "TURNO_DEALER"
    else:
        verificar_turno_jogador()

def verificar_turno_jogador():
    """Verifica se o jogador atual já tem 21 ou mais."""
    global fase_jogo
    jogador_atual = jogadores_ativos[jogador_atual_idx]
    if jogador_atual.calcular_valor_mao() >= 21:
        time.sleep(1)
        proximo_jogador()

rodando = True
clock = pygame.time.Clock()

while rodando:
    clock.tick(60)


    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
            pygame.quit()
            sys.exit()
        
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if fase_jogo == "JOGANDO":
                jogador_atual = jogadores_ativos[jogador_atual_idx]

                if botao_pedir_rect.collidepoint(evento.pos):
                    jogador_atual.adicionar_carta(baralho.distribuir_carta())
                    if jogador_atual.calcular_valor_mao() >= 21:
                        proximo_jogador()
       
                elif botao_parar_rect.collidepoint(evento.pos):
                    proximo_jogador()
            
            elif fase_jogo in ["RESULTADO", "INICIO", "FIM_DE_JOGO"]:
                if botao_prox_rodada_rect.collidepoint(evento.pos):
                    if fase_jogo == "FIM_DE_JOGO":
                        rodando = False
                    else:
                        iniciar_nova_rodada()


    if fase_jogo == "TURNO_DEALER":
 
        while dealer.calcular_valor_mao() < 17:
            dealer.adicionar_carta(baralho.distribuir_carta())
        
        valor_dealer = dealer.calcular_valor_mao()
        for jogador in jogadores_ativos:
            valor_jogador = jogador.calcular_valor_mao()
            if valor_jogador > 21:
                pass
            elif valor_dealer > 21 or valor_jogador > valor_dealer:
                if valor_jogador == 21 and len(jogador.mao) == 2:
                    jogador.fichas += int(jogador.aposta * 2.5)
                else:
                    jogador.fichas += jogador.aposta * 2
            elif valor_jogador == valor_dealer:
                jogador.fichas += jogador.aposta
        
        fase_jogo = "RESULTADO"
        mensagem = "Rodada finalizada! Clique para continuar."

    tela.fill(COR_FUNDO)
    
    desenhar_texto("Mesa de Blackjack", fonte_titulo, BRANCO, LARGURA_TELA // 2, 40)

    desenhar_texto(f"Dealer (Pontos: {dealer.calcular_mao() if fase_jogo != 'JOGANDO' else '?'})", fonte_padrao, BRANCO, LARGURA_TELA // 2, 100)
    desenhar_mao(dealer, LARGURA_TELA // 2 - 100, 130, esconder_primeira=(fase_jogo == "JOGANDO"))

    num_jogadores = len(jogadores_ativos) if fase_jogo != 'INICIO' else len(jogadores)
    for i, jogador in enumerate(jogadores_ativos if fase_jogo != 'INICIO' else jogadores):
        pos_x = (LARGURA_TELA // (num_jogadores + 1)) * (i + 1)
        desenhar_texto(f"{jogador.nome} (Fichas: {jogador.fichas})", fonte_padrao, BRANCO, pos_x, 500)
        desenhar_texto(f"Aposta: {jogador.aposta}", fonte_padrao, BRANCO, pos_x, 530)
        desenhar_mao(jogador, pos_x - 100, 340)
        desenhar_texto(f"Pontos: {jogador.calcular_mao()}", fonte_padrao, BRANCO, pos_x, 560)
        
        if fase_jogo == "JOGANDO" and i == jogador_atual_idx:
            pygame.draw.rect(tela, BRANCO, ((LARGURA_TELA // (num_jogadores + 1)) * (i + 1) - 150, 320, 300, 280), 3)

    if fase_jogo == "JOGANDO":
        pygame.draw.rect(tela, CINZA, botao_pedir_rect)
        pygame.draw.rect(tela, CINZA, botao_parar_rect)
        desenhar_texto("Pedir", fonte_padrao, BRANCO, botao_pedir_rect.centerx, botao_pedir_rect.centery)
        desenhar_texto("Parar", fonte_padrao, BRANCO, botao_parar_rect.centerx, botao_parar_rect.centery)
    
    elif fase_jogo in ["RESULTADO", "INICIO", "FIM_DE_JOGO"]:
        pygame.draw.rect(tela, CINZA, botao_prox_rodada_rect)
        texto_botao = "Iniciar Jogo" if fase_jogo == "INICIO" else "Próxima Rodada"
        if fase_jogo == "FIM_DE_JOGO": texto_botao = "Sair"
        desenhar_texto(texto_botao, fonte_padrao, BRANCO, botao_prox_rodada_rect.centerx, botao_prox_rodada_rect.centery)
        if mensagem:
            desenhar_texto(mensagem, fonte_msg, BRANCO, LARGURA_TELA // 2, ALTURA_TELA // 2 + 60)

    pygame.display.flip()

pygame.quit()
sys.exit()
