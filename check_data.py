from app import create_app
from app.extensions import db
from app.models.player import Player
from app.models.match import PlayerPerformance

app = create_app()

with app.app_context():
    print('Total players:', Player.query.count())
    print('Total performances:', PlayerPerformance.query.count())
    print('\nSample players with their performance counts:')
    for player in Player.query.limit(5).all():
        print(f'{player.name}: {len(player.performances)} performances') 