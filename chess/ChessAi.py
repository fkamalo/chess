import random
#random agent
def getRandomMove(validMoves):
   
    return random.choice(validMoves)

def evaluateBoard(board):
    #to give sense to the evaluation 
    values = {'P': 10, 'N': 30, 'B': 30, 'R': 50, 'Q': 90, 'K': 900}
    score = 0
    for row in board:
        for square in row:
            if square != "--":
                value = values.get(square[1], 0)
                if square == 'w':
                    score += value
                else:
                    score -= value
    return score

def orderMoves(gs, moves):
    """Move ordering: captures first, then others."""
    ordered = []
    captures = []
    noncaptures = []
    for move in moves:
        if move.pieceCaptured != "--":
            captures.append(move)
        else:
            noncaptures.append(move)
    # Optionally, order captures by value captured (most valuable first)
    captures.sort(key=lambda m: "PNBRQK".find(m.pieceCaptured[1]) if m.pieceCaptured != "--" else 0, reverse=True)
    ordered.extend(captures)
    ordered.extend(noncaptures)
    return ordered

def getAlphaBetaMove(gs, validMoves, depth=3):
    #Returns the best move using alpha-beta pruning up to given depth.
    #Move ordering: considers captures first.
    def alphaBeta(gs, depth, alpha, beta, maximizingPlayer):
        if depth == 0 or gs.checkmate or gs.stalemate:
            return evaluateBoard(gs.board)
        moves = orderMoves(gs, gs.getValidMoves())
        if maximizingPlayer:
            maxEval = float('-inf')
            for move in moves:
                gs.makeMove(move)
                eval = alphaBeta(gs, depth-1, alpha, beta, False)
                gs.undoMove()
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return maxEval
        else:
            minEval = float('inf')
            for move in moves:
                gs.makeMove(move)
                eval = alphaBeta(gs, depth-1, alpha, beta, True)
                gs.undoMove()
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return minEval

    bestMove = None
    if gs.whiteToMove:
        maxEval = float('-inf')
        for move in orderMoves(gs, validMoves):
            gs.makeMove(move)
            evaluation = alphaBeta(gs, depth-1, float('-inf'), float('inf'), False)
            gs.undoMove()
            if evaluation > maxEval or bestMove is None:
                maxEval = evaluation
                bestMove = move
    else:
        minEval = float('inf')
        for move in orderMoves(gs, validMoves):
            gs.makeMove(move)
            evaluation = alphaBeta(gs, depth-1, float('-inf'), float('inf'), True)
            gs.undoMove()
            if evaluation < minEval or bestMove is None:
                minEval = evaluation
                bestMove = move
    return bestMove if bestMove is not None else getRandomMove(validMoves)
