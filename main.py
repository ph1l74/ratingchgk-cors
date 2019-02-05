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
    return '<html><head><meta charset=utf-8" /></head><body><ul><li><a href="/rating">rating</a></li><li><a href="/tournaments">tournaments</a></li></ul></body></html>'


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


api.add_resource(Rating, '/rating')
api.add_resource(Tournaments, '/tournaments')

if __name__ == '__main__':
     app.run(host='0.0.0.0', port='5000')
