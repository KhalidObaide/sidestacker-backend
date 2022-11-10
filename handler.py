import re

class GameHandler():
    @staticmethod
    def handle_move(game, move, player):
        turn_condition = (game.status == 1 and game.player1 == player) or (game.status == 2 and game.player2 == player)
        if not turn_condition:
            return False
        if not re.match(r'^[RL][0-9][0-9]?$', move):
            return False
        moves = game.moves + move + '/'
        board = GameHandler.setup_board()
        valid = GameHandler.run_moves(board, moves)
        return valid, GameHandler.get_status(board, game)

    @staticmethod
    def setup_board(row=7, cols=7):
        board = [[0 for i in range(cols)] for j in range(row)]
        return board

    @staticmethod
    def print_board(board):
        for row in board:
            print(row)

    @staticmethod
    def find_spot(board, direction, row):
        if direction == 'L':
            for i in range(len(board[row])):
                if board[row][i] == 0:
                    return (row, i)
        else:
            for i in range(len(board[row]) - 1, -1, -1):
                if board[row][i] == 0:
                    return (row, i)
        return None

    @staticmethod
    def make_move(board, direction, row, player):
        spot = GameHandler.find_spot(board, direction, row)
        if spot is None:
            return False
        board[spot[0]][spot[1]] = player
        return True

    @staticmethod
    def run_moves(board, moves):
        moves = moves.split('/')[0:-1]
        for i in range(len(moves)):
            move = moves[i]
            direction, row = move[0], int(move[1:])
            valid = GameHandler.make_move(board, direction, row, i % 2 + 1)
            if not valid:
                return False
        return True

    @staticmethod
    def get_status(board, game):
        winner = 0
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] != 0:
                    # check horizontal
                    if j <= len(board[i]) - 4:
                        if board[i][j] == board[i][j + 1] == board[i][j + 2] == board[i][j + 3]:
                            winner = board[i][j]
                    # check vertical
                    if i <= len(board) - 4:
                        if board[i][j] == board[i + 1][j] == board[i + 2][j] == board[i + 3][j]:
                            winner = board[i][j]
                    # check diagonal
                    if i <= len(board) - 4 and j <= len(board[i]) - 4:
                        if board[i][j] == board[i + 1][j + 1] == board[i + 2][j + 2] == board[i + 3][j + 3]:
                            winner = board[i][j]
                    # check anti-diagonal
                    if i <= len(board) - 4 and j >= 3:
                        if board[i][j] == board[i + 1][j - 1] == board[i + 2][j - 2] == board[i + 3][j - 3]:
                            winner = board[i][j]
        if winner == 0:
            if len(game.moves.split('/')) == 49:
                return 5
            else:
                return 1 if game.status == 2 else 2
        else:
            return winner + 2
