from flask import Flask, jsonify
import  requests
#from werkzeug.exceptions import HTTPException
from flask_cors import CORS
import pandas as pd
from flask_sqlalchemy import SQLAlchemy

#from selenium import webdriver
#from selenium.webdriver import ChromeOptions
import os
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ncgfeatlso:Google@990@meetwebflask-server.postgres.database.azure.com/postgres?sslmode=require"

# 'host=meetwebflask-server.postgres.database.azure.com port=5432 dbname=postgres user=ncgfeatlso password=Google@990 sslmode=require'
db = SQLAlchemy(app)
try:
    db.create_all()
except:
    pass
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(40))
    lname = db.Column(db.String(40))
    pet = db.Column(db.String(40))

    def __init__(self,fname,lname,pet):
        self.fname = fname
        self.lname =lname
        self.pet = pet
@app.route('/api/submit/<string:fname>/<string:lname>/<string:pet>',methods = ["GET"])
def submit(fname,lname,pet):

    try:
        student = Student(fname,lname,pet)
        db.session.add(student)
        db.session.commit()
        return jsonify({"status":"Success"})
    except  Exception as e:
        return jsonify({"excepection":str(e)})

@app.route('/api/get_data',methods = ["GET"])
def get_request():

    student_result = db.session.query(Student).filter(Student.id  == 1)
    return jsonify({"fname":student_result.fname,"lname":student_result.lname,"pet":student_result.pet})




































































@app.route('/api/get-message', methods=['GET'])
def getMessage():
    data = {'message': 'Hello World!'}
    return jsonify(data)


@app.route('/api/getmovies',methods=['GET'])
def get_movieList():
    api_key = '38f5b3c12b04920fbe5fd093187951af'
    url = 'https://api.themoviedb.org/3/trending/all/day?api_key='+api_key
    data = requests.get(url)
    return data.json()


@app.route('/api/hotels/<int:checkin_day>/<int:checkin_month>/<int:checkin_year>/<int:checkout_day>/<int:checkout_month>/<int:checkout_year>',methods=["GET"])
def hotelAPi(checkin_day, checkin_month, checkin_year, checkout_day, checkout_month, checkout_year):
    days = abs(checkout_day - checkin_day)
    month = abs(checkin_month - checkout_month)
    yr = abs(checkin_year - checkout_year)
    total = (days+month+yr)/2
    df = pd.read_csv('hotels.csv')
    def spiltx(x):
        if 'km' in x:
            x = x.split('km')
            x = float(x[0])*1000
        else:
            x = x.split('m')
            x = x[0]
        return int(x)
    def format_price(x,total,lam):
        p = x.split("₹")[-1].split(',')
        rt = float(''.join(p))
        x = int(rt+total*lam)
        x = str(x)
        x = "₹ " + x[:-3] + ","+x[-3:]
        return x
    def money_numX(x):
        p = x.split("₹")[-1].split(',')
        rt = int(''.join(p))
        return rt
    df.money = df.money.apply(lambda x:format_price(x,total,0.2))
    df['distanceM'] = df.distance.apply(spiltx)
    df['money_num'] = df.money.apply(money_numX)
    hoteldata =  [df.T.to_dict()[i] for i in df.T.to_dict()]
    return jsonify({"data": hoteldata})    

"""
hotel api
"""
@app.route('/api/shop/<string:type_shop>',methods=["GET"])
def get(type_shop):
    x = []
    if type_shop == 'n':
        df = pd.read_csv('data_shop_national.csv',index_col=0)
        
        x = [df.T.to_dict()[i] for i in df.T.to_dict()]
    else:
        df = pd.read_csv('data_shop_international.csv',index_col=0)
        x = [df.T.to_dict()[i] for i in df.T.to_dict()]
    return jsonify({"data":x})
############################################### GEt status########################
# @app.route('/api/getflightstatus',methods=["GET"])
# def get_board():
#     url = 'https://mini-bell-bottom.herokuapp.com/getflightstatus/'
#     data = requests.get(url)
#     print(data)
#     return data.json()

app.config["DEBUG"] = True