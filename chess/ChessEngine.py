class GameState():
    def __init__(self):
        #8x8 board 2d list 2 chars first: color, second:type of piece, --:blank space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],  
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],  
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],  
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]   
        ]
        self.moveFunctions = {
            'P': self.getPawnMoves,
            'R': self.getRookMoves,
            'N': self.getKnightMoves,
            'B': self.getBishopMoves,
            'Q': self.getQueenMoves,
            'K': self.getKingMoves
        }
        self.whiteToMove = True
        self.movelog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.whitePieces = self.getAllPieces("w")
        self.blackPieces = self.getAllPieces("b")
        self.checkmate = False
        self.stalemate = False
        self.enPassantPossible = ()  # coordinates for en passant

    def resetGame(self):
        self.__init__()  # Reinitialize the game state

    
    def getAllPieces(self, color):
        pieces = []
        for r in range(8):
            for c in range(8):
                if self.board[r][c][0] == color:
                    pieces.append((r, c, self.board[r][c]))
        return pieces
    
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.movelog.append(move)
        self.whiteToMove = not self.whiteToMove # switch turns
        #if king moves
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        #if pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        # En passant
        if move.isEnPassantMove:
            # print("En passant triggered!")
            self.board[move.startRow][move.endCol] = "--"
       
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.endRow + move.startRow) // 2, move.endCol)  # set en passant square
        else:
            self.enPassantPossible = ()


    def undoMove(self):
        if len(self.movelog) != 0:
            move = self.movelog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            # update king location
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            # undo en passant
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured



    def getValidMoves(self):
        tempEnPassantPossible = self.enPassantPossible  # save current en passant state
        # Get all possible moves
        moves = self.getAllPossibleMoves()
        #make the move
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            #generate opp moves
            #check for checks for every op 
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                #if in check -> not valid
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()  # undo the move to restore the board state
        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        self.enPassantPossible = tempEnPassantPossible  # restore en passant state
        return moves

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(*self.whiteKingLocation)
        else:
            return self.squareUnderAttack(*self.blackKingLocation)

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True 
        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]     
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]  # get the piece type
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r-1][c] == "--":  # move forward
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":  
                    moves.append(Move((r, c), (r-2, c), self.board))  # double move
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b':  # capture left
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enPassantPossible:  # en passant left
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnPassantMove=True))
            if c+1 < 8:
                if self.board[r-1][c+1][0] == 'b':  # capture right
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enPassantPossible:  # en passant right
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnPassantMove=True))
        else:
            if self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w':  # capture left
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enPassantPossible:  # en passant left
                    moves.append(Move((r, c), (r+1, c-1), self.board, isEnPassantMove=True))
            if c+1 < 8:
                if self.board[r+1][c+1][0] == 'w':  # capture right
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enPassantPossible:  # en passant right
                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnPassantMove=True))

    def getRookMoves(self, r, c, moves):
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]  # up, left, down, right
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):  # up to 7 squares in each direction
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # inside board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break  # capture and stop
                    else:
                        break  # blocked by own piece
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        knight_moves = [
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2), (1, 2),
            (2, -1), (2, 1)
        ]
        ally_color = "w" if self.whiteToMove else "b"
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # diagonal
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break
   
    def getKingMoves(self, r, c, moves):
        king_moves = [
            (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)
        ]
        ally_color = "w" if self.whiteToMove else "b"
        for m in king_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()} # reverse mapping

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnPassantMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = (self.pieceMoved[1] == 'P' and (self.endRow == 0 or self.endRow == 7))
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = 'bP' if self.pieceMoved[0] == 'w' else 'wP'
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getchessnotion(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]