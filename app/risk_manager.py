class RiskManager:

    @staticmethod
    def calculate_risk_amount(account_balance, risk_percent):
        if account_balance <= 0:
            raise ValueError("Account balance must be greater than zero.")

        if risk_percent <= 0 or risk_percent > 100:
            raise ValueError("Risk percentage must be between 0 and 100.")

        return account_balance * risk_percent / 100

    @staticmethod
    def calculate_position_size(risk_amount, stop_loss_distance):
        if stop_loss_distance <= 0:
            raise ValueError("Stop loss distance must be greater than zero.")

        return risk_amount / stop_loss_distance

    @staticmethod
    def get_pip_size(symbol):
        normalized_symbol = symbol.replace("/", "").upper()

        if normalized_symbol.endswith("JPY"):
            return 0.01

        return 0.0001

    @staticmethod
    def calculate_pips(symbol, price_distance):
        pip_size = RiskManager.get_pip_size(symbol)

        return price_distance / pip_size
