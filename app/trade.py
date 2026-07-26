from datetime import datetime



class Trade:

    trade_counter = 1


    def __init__(
        self,
        symbol,
        direction,
        entry_price,
        lot_size,
        stop_loss,
        take_profit
    ):

        if lot_size <= 0:
            raise ValueError(
                "Lot size must be greater than zero."
            )


        if direction not in ["Buy", "Sell"]:
            raise ValueError(
                "Direction must be either 'Buy' or 'Sell'."
            )


        if direction == "Buy":

            if stop_loss >= entry_price:
                raise ValueError(
                    "For a Buy trade, stop loss must be below the entry price."
                )


            if take_profit <= entry_price:
                raise ValueError(
                    "For a Buy trade, take profit must be above the entry price."
                )


        if direction == "Sell":

            if stop_loss <= entry_price:
                raise ValueError(
                    "For a Sell trade, stop loss must be above the entry price."
                )


            if take_profit >= entry_price:
                raise ValueError(
                    "For a Sell trade, take profit must be below the entry price."
                )


        self.trade_id = f"TRD{Trade.trade_counter:04d}"

        Trade.trade_counter += 1


        self.symbol = symbol
        self.direction = direction
        self.entry_price = entry_price
        self.exit_price = None
        self.lot_size = lot_size
        self.stop_loss = stop_loss
        self.take_profit = take_profit

        self.status = "Open"

        self.open_time = datetime.now()
        self.close_time = None


        self.strategy = ""
        self.reason = ""
        self.emotion = ""
        self.lesson_learned = ""



    @classmethod
    def from_dict(cls, data):

        trade = cls(
            data["symbol"],
            data["direction"],
            data["entry_price"],
            data["lot_size"],
            data["stop_loss"],
            data["take_profit"]
        )


        trade.trade_id = data["trade_id"]


        # Update counter after loading existing trades

        number = int(
            trade.trade_id.replace("TRD", "")
        )


        if number >= cls.trade_counter:

            cls.trade_counter = number + 1



        trade.exit_price = data["exit_price"]

        trade.status = data["status"]



        if data.get("open_time"):

            trade.open_time = datetime.fromisoformat(
                data["open_time"]
            )



        if data.get("close_time") and data["close_time"] != "None":

            trade.close_time = datetime.fromisoformat(
                data["close_time"]
            )

        else:

            trade.close_time = None



        trade.strategy = data.get(
            "strategy",
            ""
        )

        trade.reason = data.get(
            "reason",
            ""
        )

        trade.emotion = data.get(
            "emotion",
            ""
        )

        trade.lesson_learned = data.get(
            "lesson_learned",
            ""
        )


        return trade