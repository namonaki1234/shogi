import pygame
import cshogi

# 初期化
pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()

# 将棋盤の初期化
board = cshogi.Board()

# 盤面を描画する関数
def draw_board():
    screen.fill((255, 255, 255))  # 背景を白に
    for i in range(9):
        for j in range(9):
            color = (200, 200, 200) if (i + j) % 2 == 0 else (150, 150, 150)
            pygame.draw.rect(screen, color, (i * 60, j * 60, 60, 60))
            piece = board.piece_at(cshogi.SQUARES[i + j * 9])
            if piece:
                pygame.draw.circle(screen, (0, 0, 0), (i * 60 + 30, j * 60 + 30), 20)

# メインループ
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_board()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
