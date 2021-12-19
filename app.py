from flask import Flask, jsonify
#from flask import request
import  requests
from flask_cors import CORS
import pandas as pd
from time import sleep 
from selenium import webdriver
import sqlite3
import datetime
import jwt
import uuid
import re

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
app = Flask(__name__)
CORS(app)

try:
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE USERS (ID TEXT PRIMARY KEY NOT NULL,TOKEN TEXT  NOT NULL ,EMAIL  TEXT  NOT NULL, PASSWORD  TEXT NOT NULL)''')

except:
    pass

app.config['SECRET_KEY']= "004f2af45d3a4e161a7dd2d17fdae47f"

def genrate_token(key):
    token = jwt.encode({'id':key,'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=5)}, app.config['SECRET_KEY'], "HS256")
    return token

@app.route('/api/userreg/<string:email>/<string:password1>/<string:password2>',methods = ["GET","POST"])
def register(email,password1,password2):
    conn = sqlite3.connect("user.db")
    rows =  conn.execute("SELECT ID,TOKEN ,EMAIL, PASSWORD from USERS WHERE EMAIL = ?",(email,),).fetchall()
    for data in rows:
        if  email in data[2]: 
         return jsonify({"error":"user exits"})
    if(re.fullmatch(regex, email) and (password1 == password2)):   
        cursor = conn.cursor()
        id = str(uuid.uuid1())
        token = genrate_token(id)
        cursor.execute("""INSERT INTO USERS(ID,TOKEN ,EMAIL, PASSWORD) 
           VALUES (\"%s\",\"%s\",\"%s\",\"%s\")""" % (id, token,email, password1))
        conn.commit()
        return jsonify({'token':token,"userId":id})
    else:
        return jsonify({"data":'Invalid Email or Password'})


@app.route('/api/refresh_token/<string:token>/<string:uid>',methods=["GET","POST"])
def refresh_token(token,uid):
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()

    try:
        tmp_token = jwt.decode(token,app.config['SECRET_KEY'], algorithms=["HS256"])  
        return jsonify({"token":token})
    except Exception as e:
        rows =  conn.execute("SELECT ID,TOKEN ,EMAIL, PASSWORD from USERS WHERE ID = ?",(uid,),).fetchall()
        rows[0]
        new_token = genrate_token(uid)
        cursor.execute("UPDATE USERS SET TOKEN = ? WHERE ID = ?",(new_token, uid))

        return jsonify({"token":new_token})

@app.route('/api/login/<string:email>/<string:password>')
def login(email,password):
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    rows =  conn.execute("SELECT ID,TOKEN ,EMAIL, PASSWORD from USERS WHERE EMAIL = ?",(email,),).fetchall()
    db_password = rows[0][3]
    db_uid = rows[0][1]
    if(db_password == password): 
        token = genrate_token(db_uid)
        cursor.execute("UPDATE USERS SET TOKEN = ? WHERE ID = ?",(token, db_uid))
        return jsonify({'token':token,"userId":db_uid})
    else:
        return jsonify({'error':"Invalid Password"})


@app.route('/api/get_data',methods = ["GET"])
def get_request():
    conn = sqlite3.connect("user.db") 
    try:
        data = []
        rows =  conn.execute("SELECT ID, EMAIL, PASSWORD from USERS")
        for row in rows:
            k = {}
            k['id'] = str(row[0])
            k['email'] = str(row[1])
            k['password'] = str(row[2])
            data.append(k)
        conn.close()
        return jsonify({"data":data})
    except Exception as e:
        conn.close()
        return jsonify({"data":str(e)})
    


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
#getFlightChartBoard
@app.route('/api/getflightstatus',methods=["GET"])
def get_board():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome('./chromedriver', options=options)
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
        driver.quit()
        data = [df.T.to_dict()[i] for i in df.T.to_dict()]
        return jsonify({"data":data})
    except Exception as e:
    
        return jsonify({"data":str(e)})
##-----------------------------------------------------##
#########################################################
##GetFlights between Places
@app.route('/api/getflights/<string:orgin>/<string:destination>/<string:date>/<int:adults>/<int:children>/<int:infants>',methods=["GET"])
def get_flights(orgin, destination, date, adults, children, infants):
    try:
        date = date.split('-')
        date = date[-1]+date[1]+date[0]
        date = ''.join(date)
        url = f"https://www.ixigo.com/search/result/flight?from={orgin.upper()}&to={destination.upper()}&date={date}&returnDate=&adults={adults}&children={children}&infants={infants}&class=e&source=Search%20Form"
        print(url)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome('./chromedriver', options=options)
        driver.maximize_window()
        driver.get(url)
        sleep(2)
        total_items = []
        pages = driver.find_element_by_class_name('c-pagination') 
        all_pages = pages.find_elements_by_xpath('.//span[@class = "page-num"]')
        for page in all_pages:
            cards = driver.find_elements_by_class_name('c-flight-listing-row-v2')
            for card in cards:
                k = {}
                fight_img = card.find_element_by_xpath('.//div[@class = "logo"]').find_element_by_tag_name('img').get_attribute('src')
                fight_name = card.find_element_by_xpath('.//a[@class = "flight-name"]').text
                orgin_details = card.find_element_by_class_name('left-wing')
                orgin_code = orgin_details.find_element_by_class_name('airport-code').text
                orgin_date = orgin_details.find_element_by_class_name('date').text
                orgin_time = orgin_details.find_element_by_class_name('time').text
                orgin_city = orgin_details.find_element_by_xpath('.//div[4]').text
                ####
                destination_details = card.find_element_by_class_name('right-wing')
                dest_code = destination_details.find_element_by_class_name('airport-code').text
                dest_date = destination_details.find_element_by_class_name('date').text
                dest_time = destination_details.find_element_by_class_name('time').text
                dest_city = destination_details.find_element_by_xpath('.//div[4]').text
                ####
                duration_stops_div = card.find_element_by_class_name('flight-summary')
                duration_of_flight = duration_stops_div.find_element_by_xpath('.//div[2]//div[1]//div[2]').text
                duration_stops = duration_stops_div.find_element_by_xpath('.//div[2]//div[1]//div[6]').text

                flight_price = card.find_element_by_class_name('price-section').text
                discount_credit = card.find_element_by_class_name('dynot').text
                k['fight_img']  = fight_img 
                k['fight_name'] = fight_name
                k['orgin_code'] = orgin_code 
                k['orgin_date'] = orgin_date 
                k['orgin_time'] = orgin_time
                k['orgin_city'] = orgin_city
                k['dest_code']  = dest_code
                k['dest_date']  = dest_date
                k['dest_time']  = dest_time
                k['dest_city']  = dest_city
                k['duration_of_flight'] = duration_of_flight
                k['duration_stops'] = duration_stops
                k['flight_price'] = flight_price
                k['discount_credit'] = discount_credit
                total_items.append(k)
            sleep(2)
            page.click()
        data = pd.DataFrame(total_items)
        driver.close()
        return jsonify({"data":[data.T.to_dict()[i] for i in data.T.to_dict()]})
    except Exception as e:
        return jsonify({"error":e})


app.config["DEBUG"] = True