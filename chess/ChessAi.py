import time
import random

def getRandomMove(gs):
    """Return a random move from the valid moves in the GameState gs."""
    validMoves = gs.getValidMoves()
    return random.choice(validMoves) if validMoves else None

class getSimpleAlphaBetaMove:
    def __init__(self, depth=3, time_limit=2.0):
        self.max_depth = depth
        self.time_limit = time_limit
        self.nodes_evaluated = 0
        self.piece_values = {'P': 100, 'N': 300, 'B': 300, 'R': 500, 'Q': 900, 'K': 10000}
        self.start_time = 0

    def __call__(self, gs, validMoves):
        self.nodes_evaluated = 0
        self.start_time = time.time()

        best_move = None
        best_score = float('-inf')
        alpha, beta = float('-inf'), float('inf')

        for move in validMoves:
            if time.time() - self.start_time > self.time_limit:
                break
            gs.makeMove(move)
            score = -self.alpha_beta(gs, self.max_depth - 1, -beta, -alpha, False)
            gs.undoMove()
            if score > best_score or best_move is None:
                best_score = score
                best_move = move
            alpha = max(alpha, score)
        return best_move

    def alpha_beta(self, gs, depth, alpha, beta, maximizing_player):
        self.nodes_evaluated += 1
        if time.time() - self.start_time > self.time_limit:
            return self.evaluatePosition(gs)

        if gs.checkmate:
            return -1000 - depth if maximizing_player else 1000 + depth
        if gs.stalemate:
            return 0
        if depth == 0:
            return self.evaluatePosition(gs)

        moves = gs.getValidMoves()
        if not moves:
            if gs.inCheck():
                return -1000 - depth
            return 0

        if maximizing_player:
            max_eval = float('-inf')
            for move in moves:
                gs.makeMove(move)
                eval_score = self.alpha_beta(gs, depth - 1, alpha, beta, False)
                gs.undoMove()
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in moves:
                gs.makeMove(move)
                eval_score = self.alpha_beta(gs, depth - 1, alpha, beta, True)
                gs.undoMove()
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def evaluatePosition(self, gs):
        score = 0
        for r in range(8):
            for c in range(8):
                piece = gs.board[r][c]
                if piece != "--":
                    value = self.piece_values.get(piece[1], 0)
                    if piece[0] == 'w':
                        score += value
                    else:
                        score -= value
        # Score from perspective of player to move
        return score if gs.whiteToMove else -score

class getAlphaBetaMove:
    def __init__(self, depth=4, time_limit=3.0):
        self.max_depth = depth
        self.time_limit = time_limit
        self.nodes_evaluated = 0
        self.piece_values = {'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000}
        self.start_time = 0

    def __call__(self, gs, validMoves):
        self.nodes_evaluated = 0
        self.start_time = time.time()

        ordered_moves = self.orderMoves(gs, validMoves)
        best_move = None
        best_score = float('-inf')
        alpha, beta = float('-inf'), float('inf')

        for move in ordered_moves:
            if time.time() - self.start_time > self.time_limit:
                break
            gs.makeMove(move)
            score = -self.alpha_beta(gs, self.max_depth - 1, -beta, -alpha, False)
            gs.undoMove()
            if score > best_score or best_move is None:
                best_score = score
                best_move = move
            alpha = max(alpha, score)

        return best_move

    def alpha_beta(self, gs, depth, alpha, beta, maximizing_player):
        self.nodes_evaluated += 1
        if time.time() - self.start_time > self.time_limit:
            return self.evaluatePosition(gs)

        if gs.checkmate:
            return -10000 - depth if maximizing_player else 10000 + depth
        if gs.stalemate:
            return 0
        if depth == 0:
            return self.evaluatePosition(gs)

        moves = gs.getValidMoves()
        if not moves:
            if gs.inCheck():
                return -10000 - depth
            return 0

        moves = self.orderMoves(gs, moves)

        if maximizing_player:
            max_eval = float('-inf')
            for move in moves:
                gs.makeMove(move)
                eval_score = self.alpha_beta(gs, depth - 1, alpha, beta, False)
                gs.undoMove()
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in moves:
                gs.makeMove(move)
                eval_score = self.alpha_beta(gs, depth - 1, alpha, beta, True)
                gs.undoMove()
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def evaluatePosition(self, gs):
        white_material = 0
        black_material = 0
        for r in range(8):
            for c in range(8):
                piece = gs.board[r][c]
                if piece != "--":
                    value = self.piece_values.get(piece[1], 0)
                    if piece[0] == 'w':
                        white_material += value
                    else:
                        black_material += value
        score = white_material - black_material

        material_diff = abs(white_material - black_material)
        if material_diff > 500:
            enemy_color = 'b' if gs.whiteToMove else 'w'
            try:
                enemy_king = gs.blackKingLocation if enemy_color == 'b' else gs.whiteKingLocation
                my_king = gs.whiteKingLocation if gs.whiteToMove else gs.blackKingLocation
                king_dist = abs(my_king[0] - enemy_king[0]) + abs(my_king[1] - enemy_king[1])
                edge_dist = min(enemy_king[0], 7 - enemy_king[0], enemy_king[1], 7 - enemy_king[1])
                score += (10 - king_dist) * 30
                score += (4 - edge_dist) * 50
                for r in range(8):
                    for c in range(8):
                        piece = gs.board[r][c]
                        if piece != "--" and piece[0] == ('w' if gs.whiteToMove else 'b') and piece[1] == 'Q':
                            q_dist = abs(r - enemy_king[0]) + abs(c - enemy_king[1])
                            score += (8 - q_dist) * 40
            except:
                pass
        score += len(gs.getValidMoves()) * 5
        return score if gs.whiteToMove else -score

    def orderMoves(self, gs, moves):
        def move_score(move):
            score = 0
            if move.pieceCaptured != "--":
                score += self.piece_values.get(move.pieceCaptured[1], 0) * 10
            if move.isPawnPromotion:
                score += 800
            gs.makeMove(move)
            if gs.inCheck():
                score += 100
                if len(gs.getValidMoves()) == 0:
                    score += 50000
            gs.undoMove()
            return score

        return sorted(moves, key=move_score, reverse=True)
