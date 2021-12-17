from flask_restful import Resource
import pandas as pd
from flask import jsonify


class Shopping(Resource):
    def get(self,type_of_shop):
        x = []
        if type_of_shop == 'n':
            df = pd.read_csv('data_shop_national.csv',index_col=0)
            
            x = [df.T.to_dict()[i] for i in df.T.to_dict()]
        else:
            df = pd.read_csv('data_shop_international.csv',index_col=0)
            x = [df.T.to_dict()[i] for i in df.T.to_dict()]
        return jsonify({"data":x})
