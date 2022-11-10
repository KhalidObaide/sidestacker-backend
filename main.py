from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from handler import GameHandler

# application setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
socketio = SocketIO(app, cors_allowed_origins="*")
db = SQLAlchemy(app)
app.app_context().push()

# models
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player1 = db.Column(db.String(80), unique=False, nullable=False)
    player2 = db.Column(db.String(80), unique=False, nullable=True)
    moves = db.Column(db.String(500), unique=False, nullable=False)
    status = db.Column(db.Integer, unique=False, nullable=False)
    # Game status
    # 0 = waiting for player 2
    # 1, 2 = player 1, 2 turn
    # 3, 4 = player 1, 2 wins
    # 5 = draw
    # 6 cancelled

    def __repr__(self):
        return '<Game %r>' % self.id


class GameMessage():
    def __init__(self, game, player):
        self.status = game.status
        self.game_id = game.id
        self.moves = game.moves
        self.player = player

    def to_dict(self):
        return {
            'game_id': self.game_id,
            'status': self.status,
            'moves': self.moves,
            'player': self.player
        }


@socketio.on('match')
def matchmaking():
    player = request.sid
    game = Game.query.filter(Game.status == 0).first()
    if game is None:
        game = Game(player1=player, player2=None, moves='', status=0)
        db.session.add(game)
        db.session.commit()
        emit('game', GameMessage(game, 1).to_dict())
    else:
        game.player2 = player
        game.status = 1
        db.session.commit()
        emit('game', GameMessage(game, 1).to_dict(), room=game.player1)
        emit('game', GameMessage(game, 2).to_dict(), room=game.player2)


@socketio.on('leave')
def leave():
    player = request.sid
    games = Game.query.filter((Game.player1 == player) | (Game.player2 == player)).all()
    for game in games:
        game.status = 6
        db.session.commit()
        emit('game', GameMessage(game, 1).to_dict(), room=game.player1)
        emit('game', GameMessage(game, 2).to_dict(), room=game.player2)


@socketio.on('move')
def move(data):
    player = request.sid
    game = Game.query.filter((Game.status == 1) | (Game.status == 2)).filter(
        (Game.player1 == player) | (Game.player2 == player)).first()
    if game is None:
        return
    valid, status = GameHandler.handle_move(game, data['move'], player)
    if valid:
        game.status = status
        game.moves += data['move'] + '/'
        db.session.commit()
        emit('game', GameMessage(game, 1).to_dict(), room=game.player1)
        emit('game', GameMessage(game, 2).to_dict(), room=game.player2)

if __name__ == '__main__':
    db.create_all()
    socketio.run(app, host='0.0.0.0')


