import json
import os

from app.trade import Trade



class JSONManager:


    def __init__(self, file_path):

        self.file_path = file_path



    def save_data(self, data):

        with open(
            self.file_path,
            "w"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )



    def load_data(self):

        if not os.path.exists(
            self.file_path
        ):

            return []


        with open(
            self.file_path,
            "r"
        ) as file:

            return json.load(
                file
            )



    def load_trades(self):

        data = self.load_data()

        return data



    def load_trade_objects(self):

        trade_objects = []


        data = self.load_data()


        for trade_data in data:


            trade = Trade.from_dict(
                trade_data
            )


            trade_objects.append(
                trade
            )


        return trade_objects