from app.json_manager import JSONManager
from app.trade import Trade



class TradeRepository:


    def __init__(self, file_path):

        self.json_manager = JSONManager(
            file_path
        )



    # Save Trade objects into JSON
    def save_trades(self, trades):

        trade_data = []


        for trade in trades:

            trade_data.append(
                trade.to_dict()
            )


        self.json_manager.save_data(
            trade_data
        )



    # Load JSON and convert into Trade objects
    def load_trades(self):

        saved_data = self.json_manager.load_trades()


        trades = []


        for data in saved_data:

            trade = Trade.from_dict(
                data
            )


            trades.append(
                trade
            )


        return trades





# =====================================
# Test Repository
# =====================================

if __name__ == "__main__":


    repository = TradeRepository(
        "data/trades.json"
    )


    trades = repository.load_trades()


    print("\n===== Repository Test =====")



    for trade in trades:

        print(
            trade.trade_id,
            trade.symbol,
            trade.status
        )