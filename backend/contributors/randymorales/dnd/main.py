

from flask import Flask
from service import RandymoralesMonsterProxyService
from endpoints import MonsterListAPI, MonsterGetAPI

app = Flask(__name__)
service = RandymoralesMonsterProxyService()

app.add_url_rule('/list', view_func=MonsterListAPI.as_view('monster_list'))
app.add_url_rule('/get', view_func=MonsterGetAPI.as_view('monster_get'))

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=4000)
