from flask import Flask, jsonify
import  requests
from werkzeug.exceptions import HTTPException
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/get-message', methods=['GET'])
def getMessage():
    data = {'message': 'Hello World!'}
    return jsonify(data)


@app.route('/api/getmovies',methods=['GET'])
def get_movieList():
    api_key = '38f5b3c12b04920fbe5fd093187951af'
    url = 'https://api.themoviedb.org/3/trending/all/day?api_key='+api_key
    data = requests.get(url)
    return jsonify(data.to_json())

app.config["DEBUG"] = True