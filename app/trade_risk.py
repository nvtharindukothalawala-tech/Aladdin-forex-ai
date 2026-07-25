class TradeRisk:

    def __init__(self, trades):

        self.trades = trades


    def largest_winning_trade(self):

        largest_profit = 0


        for trade in self.trades:

            profit = trade.calculate_profit()


            if profit is not None and profit > largest_profit:

                largest_profit = profit


        return largest_profit
    

    def largest_losing_trade(self):

        largest_loss = 0


        for trade in self.trades:

            profit = trade.calculate_profit()


            if profit is not None and profit < largest_loss:

                largest_loss = profit


        return largest_loss

    def average_risk_reward(self):

        total_ratio = 0

        count = 0


        for trade in self.trades:

            ratio = trade.calculate_risk_reward_ratio()


            if ratio is not None:

                total_ratio += ratio

                count += 1


        if count == 0:

            return 0


        return total_ratio / count

    def maximum_drawdown(self):

        balance = 0

        peak = 0

        max_drawdown = 0


        for trade in self.trades:

            profit = trade.calculate_profit()


            if profit is not None:

                balance += profit


                if balance > peak:

                    peak = balance


                drawdown = peak - balance


                if drawdown > max_drawdown:

                    max_drawdown = drawdown


        return max_drawdown

    def maximum_consecutive_wins(self):

        current_wins = 0

        maximum_wins = 0


        for trade in self.trades:

            result = trade.get_trade_result()


            if result == "Win":

                current_wins += 1


                if current_wins > maximum_wins:

                    maximum_wins = current_wins


            else:

                current_wins = 0


        return maximum_wins

    def maximum_consecutive_losses(self):

        current_losses = 0

        maximum_losses = 0


        for trade in self.trades:

            result = trade.get_trade_result()


            if result == "Loss":

                current_losses += 1


                if current_losses > maximum_losses:

                    maximum_losses = current_losses


            else:

                current_losses = 0


        return maximum_losses