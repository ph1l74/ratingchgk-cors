import requests
from flask import Flask
from flask_restful import Api, Resource
from flask import json
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
api = Api(app)
CORS(app)


@app.route('/')
def index():
    return '<html><head><meta charset=utf-8" /></head>' \
           '<body><ul>' \
           '<li><a href="/rating">rating</a></li>' \
           '<li><a href="/tournaments">tournaments</a></li>' \
           '<li><a href="/teamrating">teamrating</a></li>' \
           '</ul>' \
           '</body></html>'


class Rating(Resource):

    def __init__(self):
        self.rating = []

    @staticmethod
    def convert_request(request_string):
        req = requests.get(request_string)
        result = req.json()
        return result

    def renew(self):
        return self.convert_request('http://rating.chgk.info/api/players/1683/rating.json')

    def filter(self):
        rating = self.renew()
        for game in rating:
            if (datetime.strptime(game['date'], '%Y-%m-%d') >= datetime(2018, 8, 26)):
                self.rating.append(game)

    def get(self):
        self.filter()
        response = app.response_class(
                response=json.dumps(self.rating),
                status=200,
                mimetype='application/json'
            )
        return response


class Tournaments(Resource):

    def __init__(self):
        self.tournaments = []
        self.tournaments_and_rating = []

    @staticmethod
    def convert_request(request):
        req = requests.get(request)
        result = req.json()
        return result

    def get_last_tournaments(self):
        return self.convert_request('http://rating.chgk.info/api/players/1683/tournaments/last.json')

    def get_tournament_name_by_id(self, id):
        return self.convert_request('http://rating.chgk.info/api/tournaments/{0}.json'.format(id))

    def get(self):
        response = self.get_last_tournaments()
        for tournament in response['tournaments']:
            tounrament_info = self.get_tournament_name_by_id(tournament['idtournament'])
            self.tournaments.append(tounrament_info[0]['name'])
        return self.tournaments


class TeamRating(Resource):
    def __init__(self):
        self.team_rating = {
            'current_rating': '',
            'current_rating_position' : '',
            'last_revision': '',
            'prev_rating': '',
            'prev_rating_position': ''
        }

    @staticmethod
    def convert_request(request_string):
        req = requests.get(request_string)
        result = req.json()
        return result

    def get_current_rating(self):
        last_b = self.convert_request('http://rating.chgk.info/api/teams/5723/rating/b.json')
        self.team_rating['current_rating'] = last_b['rating']
        self.team_rating['current_rating_position'] = last_b['rating_position']
        self.team_rating['last_revision'] = last_b['idrelease']
        return print('current rating got {0}, {1}, {2}'.format(self.team_rating['current_rating'],
                                                               self.team_rating['current_rating_position'],
                                                               self.team_rating['last_revision']))

    def get_prev_rating(self):
        prev_revision = int(self.team_rating['last_revision']) - 1
        prev_b = self.convert_request('http://rating.chgk.info/api/teams/5723/rating/{}.json'.format(prev_revision))
        self.team_rating['prev_rating'] = prev_b['rating']
        self.team_rating['prev_rating_position'] = prev_b['rating_position']
        return print('prev rating got: {0}, {1}'.format(self.team_rating['prev_rating'],
                                                        self.team_rating['prev_rating_position']))

    def get(self):
        self.get_current_rating()
        self.get_prev_rating()
        return self.team_rating


api.add_resource(Rating, '/rating')
api.add_resource(Tournaments, '/tournaments')
api.add_resource(TeamRating, '/teamrating')

if __name__ == '__main__':
     app.run(host='0.0.0.0', port='5000')
