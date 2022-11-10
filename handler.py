import re

class GameHandler():
    @staticmethod
    def handle_move(game, move, player):
        print("handling")
        if game.status != player:
            return False
        if not re.match(r'^[RL][0-9][0-9]?$', move):
            return False

        direction, distance = move[0], int(move[1:])
        print(direction, distance)
        return True
