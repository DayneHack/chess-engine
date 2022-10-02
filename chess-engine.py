import chess
import random
import sys
import enum
from stockfish import Stockfish
import time

def getPieceValue(piece):

    if piece == None:
        return 0
    if piece == 'p' or piece == 'P':
        return 10
    if piece == 'n' or piece == 'N':
        return 30
    if piece == 'b' or piece == 'B':
        return 30
    if piece == 'r' or piece == 'R':
        return 50
    if piece == 'q' or piece == 'Q':
        return 90
    if piece == 'k' or piece == 'K':
        return 900
    return 0

def getColorScore(board, color):

    score = 0
    for i in range(64):
        if color == 'white':
            if not str(board.piece_at(i)).islower():
                score += getPieceValue(str(board.piece_at(i)))
        else:
            if str(board.piece_at(i)).islower():
                score += getPieceValue(str(board.piece_at(i)))
    return score

def evaluate(board, maximizingColor):

    whiteScore = getColorScore(board, 'white')
    blackScore = getColorScore(board, 'black')

    if maximizingColor == 'white':
        return whiteScore - blackScore
    else:
        return blackScore - whiteScore

def makeNullMove(board):
    move = chess.Move.null()
    board.push(move)

def undoNullMove(board):
    board.pop()

def miniMax(board, depth, maximizingPlayer, maximizingColor):

    if depth == 0 or board.is_game_over():
        return None, evaluate(board, maximizingColor)

    moves = list(board.legal_moves)
    bestMove = random.choice(moves)

    if maximizingPlayer:
        maxEval = -9999
        for move in moves:
            board.push_san(str(move))
            currEval = miniMax(board, depth-1, False, maximizingColor)[1]
            board.pop()
            if currEval > maxEval:
                maxEval = currEval
                bestMove = move
        return bestMove, maxEval
    else:
        minEval = 9999
        for move in moves:
            board.push_san(str(move))
            currEval = miniMax(board, depth-1, True, maximizingColor)[1]
            board.pop()
            if currEval < minEval:
                minEval = currEval
                bestMove = move
        return bestMove, minEval

def miniMaxAlphaBeta(board, depth, alpha, beta, maximizingPlayer, maximizingColor):

    if depth == 0 or board.is_game_over():
        return None, evaluate(board, maximizingColor)

    moves = list(board.legal_moves)
    bestMove = random.choice(moves)

    if maximizingPlayer:
        maxEval = -9999
        for move in moves:
            board.push_san(str(move))
            currEval = miniMaxAlphaBeta(board, depth-1, alpha, beta, False, maximizingColor)[1]
            board.pop()
            if currEval > maxEval:
                maxEval = currEval
                bestMove = move
            alpha = max(alpha, currEval)
            if beta <= alpha:
                break
        return bestMove, maxEval
    else:
        minEval = 9999
        for move in moves:
            board.push_san(str(move))
            currEval = miniMaxAlphaBeta(board, depth-1, alpha, beta, True, maximizingColor)[1]
            board.pop()
            if currEval < minEval:
                minEval = currEval
                bestMove = move
            beta = min(beta, currEval)
            if beta <= alpha:
                break
        return bestMove, minEval

def miniMaxNullMove(board, depth, alpha, beta, maximizingPlayer, maximizingColor, r):

    if depth == 0 or board.outcome():
        return None, evaluate(board, maximizingColor)

    if depth >= 3 and not board.is_check():
        makeNullMove(board)
        currEval = -miniMaxNullMove(board, depth - r - 1, -beta, -beta + 1, True, maximizingColor, r)[1]
        undoNullMove(board)
        if currEval >= beta:
            return beta

    moves = list(board.legal_moves)
    bestMove = random.choice(moves)

    if maximizingPlayer:
        maxEval = -9999
        for move in moves:
            board.push_san(str(move))
            currEval = miniMaxNullMove(board, depth-1, alpha, beta, False, maximizingColor, r)[1]
            board.pop()
            if currEval > maxEval:
                maxEval = currEval
                bestMove = move
            alpha = max(alpha, currEval)
            if beta <= alpha:
                break
        return bestMove, maxEval
    else:
        minEval = 9999
        for move in moves:
            board.push_san(str(move))
            currEval = miniMaxNullMove(board, depth-1, alpha, beta, True, maximizingColor, r)[1]
            board.pop()
            if currEval < minEval:
                minEval = currEval
                bestMove = move
            beta = min(beta, currEval)
            if beta <= alpha:
                break
        return bestMove, minEval


class Status(enum.IntFlag):
    VALID = 0
    NO_WHITE_KING = 1 << 0
    NO_BLACK_KING = 1 << 1
    OPPOSITE_CHECK = 1 << 10


STATUS_VALID = Status.VALID
STATUS_NO_WHITE_KING = Status.NO_WHITE_KING
STATUS_NO_BLACK_KING = Status.NO_BLACK_KING
STATUS_OPPOSITE_CHECK = Status.OPPOSITE_CHECK


def main():
    playerTurn = True
    alpha = -9999
    beta = 9999
    counter = 0
    timeList = []
    stockfishList = []

    stockfish = Stockfish('C:\Program Files\Stockfish\stockfish.exe')

    board = chess.Board()
    print(board)

    while(True):
        print('# of turns: ', counter)
        if board.status() == STATUS_NO_WHITE_KING:
            print('Game Over, black wins!')
            print('Average turn time: ', sum(timeList)/len(timeList))
            print('Average turn time Stockfish: ', sum(stockfishList)/len(stockfishList))
            sys.exit(0)
        if  board.status() == STATUS_NO_BLACK_KING:
            print('Game Over, white wins!')
            print('Average turn time: ', sum(timeList)/len(timeList))
            print('Average turn time Stockfish: ', sum(stockfishList)/len(stockfishList))
            sys.exit(0)
        if board.is_stalemate():
            print('It is a draw!')
            print('Average turn time: ', sum(timeList)/len(timeList))
            print('Average turn time Stockfish: ', sum(stockfishList)/len(stockfishList))
            sys.exit(0)

        if playerTurn:

            print('Stockfish turn:')
            start = time.time()
            fen = board.fen()
            stockfish.set_fen_position(fen)
            move = stockfish.get_best_move()
            #move = miniMaxNullMove(board, 4, alpha, beta, True, 'black', 2)
            move = chess.Move.from_uci(str(move))
            board.push(move)
            end = time.time()
            print(end-start)
            stockfishList.append(end-start)
            playerTurn = False
            counter += 1

        else:

            print('Minimax turn:')
            start = time.time()

            #move = miniMax(board, 3, True, 'black')                          #miniMax
            #move = miniMaxAlphaBeta(board, 4, alpha, beta, True, 'black')    #miniMaxAlphaBeta
            move = miniMaxNullMove(board, 4, alpha, beta, True, 'black', 2)   #miniMaxNullMove

            if move[0] == None:
                print('No more moves! White wins!:')
                print('Average turn time: ', sum(timeList)/len(timeList))
                print('Average turn time Stockfish: ', sum(stockfishList)/len(stockfishList))
                sys.exit(0)
            move = chess.Move.from_uci(str(move[0]))

            board.push(move)
            end = time.time()
            print(end-start)
            timeList.append(end-start)
            playerTurn = True
        print(board)

    
main()