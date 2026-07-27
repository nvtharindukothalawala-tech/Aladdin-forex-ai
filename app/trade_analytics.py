class TradeAnalytics:

    def __init__(self, trades):

        self.trades = trades

    def total_trades(self):

        return len(self.trades)

    def winning_trades(self):

        count = 0

        for trade in self.trades:

            profit = trade.calculate_profit()

            if profit is not None and profit > 0:

                count += 1

        return count

    def losing_trades(self):

        count = 0

        for trade in self.trades:

            profit = trade.calculate_profit()

            if profit is not None and profit < 0:

                count += 1

        return count

    def open_trades(self):

        count = 0

        for trade in self.trades:

            if trade.status == "Open":

                count += 1

        return count

    def win_rate(self):

        closed_trades = self.winning_trades() + self.losing_trades()

        if closed_trades == 0:

            return 0

        return (self.winning_trades() / closed_trades) * 100

    def total_profit(self):

        total = 0

        for trade in self.trades:

            profit = trade.calculate_profit()

            if profit is not None:

                total += profit

        return total

    def average_profit(self):

        closed = []

        for trade in self.trades:

            profit = trade.calculate_profit()

            if profit is not None:

                closed.append(profit)

        if len(closed) == 0:

            return 0

        return sum(closed) / len(closed)

    def gross_profit(self):

        total = 0

        for trade in self.trades:

            profit = trade.calculate_profit()

            if profit is not None and profit > 0:

                total += profit

        return total

    def gross_loss(self):

        total = 0

        for trade in self.trades:

            profit = trade.calculate_profit()

            if profit is not None and profit < 0:

                total += abs(profit)

        return total

    def profit_factor(self):

        loss = self.gross_loss()

        if loss == 0:

            return 0

        return self.gross_profit() / loss
