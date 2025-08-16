import pygame as p
import ChessEngine
import sys
from ChessAi import getRandomMove, getAlphaBetaMove

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 15
IMAGES = {}

def loadImages():
    pieces = ['wK', 'wQ', 'wR', 'wB', 'wN', 'wP',
              'bK', 'bQ', 'bR', 'bB', 'bN', 'bP']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))

def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 48, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH/2 - textObject.get_width()/2,
        HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    p.display.flip()

def main():
    print("Choose a game mode:")
    print("1: Human vs Random AI")
    print("2: Human vs Alpha-Beta AI")
    print("3: Alpha-Beta AI vs Alpha-Beta AI")
    mode = input("Enter mode number (1-3): ").strip()
    while mode not in {'1', '2', '3'}:
        mode = input("Please enter 1, 2, or 3: ").strip()
    mode = int(mode)

    humanIsWhite = True if mode != 3 else None

    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                p.quit()
                sys.exit()

            elif e.type == p.MOUSEBUTTONDOWN:
                # Only allow human moves in mode 1 & 2 and only if it's human's turn
                if humanIsWhite is not None:
                    isHumanTurn = (gs.whiteToMove and humanIsWhite) or (not gs.whiteToMove and not humanIsWhite)
                    if isHumanTurn:
                        location = p.mouse.get_pos()
                        col = location[0] // SQ_SIZE
                        row = location[1] // SQ_SIZE
                        if sqSelected == (row, col):
                            sqSelected = ()
                            playerClicks = []
                        else:
                            sqSelected = (row, col)
                            playerClicks.append((row, col))
                        if len(playerClicks) == 2:
                            move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    gs.makeMove(move)
                                    moveMade = True
                                    sqSelected = ()
                                    playerClicks = []
                                    break
                            if not moveMade:
                                playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                elif e.key == p.K_r:
                    gs.resetGame()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        # AI turns depending on mode
        if not gs.checkmate and not gs.stalemate:
            if mode == 1:
                # Human vs Random AI
                if humanIsWhite and not gs.whiteToMove or (not humanIsWhite and gs.whiteToMove):
                    aiValidMoves = gs.getValidMoves()
                    if aiValidMoves:
                        aiMove = getRandomMove(aiValidMoves)
                        gs.makeMove(aiMove)
                        moveMade = True
                        sqSelected = ()
                        playerClicks = []
            elif mode == 2:
                # Human vs Alpha-Beta AI
                if humanIsWhite and not gs.whiteToMove or (not humanIsWhite and gs.whiteToMove):
                    aiValidMoves = gs.getValidMoves()
                    if aiValidMoves:
                        aiMove = getAlphaBetaMove(gs, aiValidMoves)
                        gs.makeMove(aiMove)
                        moveMade = True
                        sqSelected = ()
                        playerClicks = []
            elif mode == 3:
                # Alpha-Beta AI vs Alpha-Beta AI
                aiValidMoves = gs.getValidMoves()
                if aiValidMoves:
                    aiMove = getAlphaBetaMove(gs, aiValidMoves)
                    gs.makeMove(aiMove)
                    moveMade = True
                    sqSelected = ()
                    playerClicks = []

        drawGameState(gs, screen, validMoves, sqSelected)

        if gs.checkmate:
            drawEndGameText(screen, "Checkmate! Game over.")
        elif gs.stalemate:
            drawEndGameText(screen, "Stalemate! Game over.")

        clock.tick(MAX_FPS)
        p.display.flip()

def drawGameState(gs, screen, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(gs, screen)

def drawBoard(screen):
    colors = [p.Color("white"), p.Color("blueviolet")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(gs, screen):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = gs.board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('yellow'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(p.Color('lime'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

if __name__ == "__main__":
    main()
