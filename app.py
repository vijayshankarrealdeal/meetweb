from flask import Flask, jsonify
import  requests
#from werkzeug.exceptions import HTTPException
from flask_cors import CORS
import pandas as pd
import psycopg2
#from selenium import webdriver
#from selenium.webdriver import ChromeOptions
import os
app = Flask(__name__)
CORS(app)

host = "meetwebflask-server"
dbname = "postgres"
user = "ncgfeatlso"
password = "PGO0637ETON66601$"
sslmode = "require"
conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)





@app.route('/api/submit/<string:fname>/<string:lname>/<string:pet>',methods = ["GET"])
def submit(fname,lname,pet):
    conn = psycopg2.connect(conn_string) 
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE TABLE student (id serial PRIMARY KEY, fname VARCHAR(50), lname VARCHAR(50),pet VARCHAR(50));")
    except:
        pass
    cursor.execute("INSERT INTO inventory (fname, lname,pet) VALUES (%s, %s,%s);", (fname, lname,pet))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status":"Done"})

@app.route('/api/get_data',methods = ["GET"])
def get_request():
    conn = psycopg2.connect(conn_string) 
    cursor = conn.cursor()
    data = []
    rows = cursor.fetchall()
    for row in rows:
        k = {}
        k['fname'] = str(row[0])
        k['lname'] = str(row[1])
        k['pet'] = str(row[2])
        data.append(k)
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"data":data})




































































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