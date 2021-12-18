from flask import Flask, jsonify
import  requests
from flask_cors import CORS
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from db import create_table, insert_data, read_data
app = Flask(__name__)
CORS(app)
@app.route('/api/createdb', methods=['GET'])
def createTable():
    data = create_table()
    return jsonify({"data":data})


@app.route('/api/submit/<string:fname>/<string:lname>/<string:pet>',methods = ["GET"])
def submit(fname,lname,pet):
    status = insert_data(fname,lname,pet)
    return jsonify({"status":status})

@app.route('/api/get_data',methods = ["GET"])
def get_request():
    data = read_data()
    return jsonify({"data":data})




































































@app.route('/api/get-message', methods=['GET'])
def getMessage():
    data = {'message': 'Hello World Again ss'}
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
@app.route('/api/getflightstatus',methods=["GET"])
def get_board():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path = ChromeDriverManager.install(),options=options)
    driver.maximize_window()
    driver.get('https://www.bangaloreairport.com/kempegowda-departures')
    items = driver.find_elements_by_xpath('.//div[@class = "flight-row"]')
    data = []
    for item in items:
        try:
            k = {}
            k['departure'] = item.find_element_by_xpath('.//div[1]').text
            k['time'] = item.find_element_by_xpath('.//div[2]//div[1]').text
            k['flight'] = item.find_element_by_xpath('.//div[2]//div[2]').text
            k['airline'] = item.find_element_by_xpath('.//div[2]//div[3]').text
            k['info_url'] = item.find_element_by_xpath('.//div[2]').find_element_by_tag_name('a').get_attribute('href')
            k['status'] = item.find_element_by_xpath('.//div[contains(@class ,"flight-col flight-col__status")]').text
            data.append(k)
        except:
            pass
    df = pd.DataFrame(data)
    driver.close()
    data = [df.T.to_dict()[i] for i in df.T.to_dict()]
    return jsonify({"data":data})


app.config["DEBUG"] = True