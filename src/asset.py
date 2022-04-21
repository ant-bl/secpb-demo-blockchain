import logging


class AssetCreate:

    def __init__(self):
        self.name = ""
        self.open = True
        self.address = ""
        self.qty = 1
        self.min_amount = 0.01

    def asset_creation(self, access):
        asset_params = {"name": self.name, "open": self.open}
        try:
            transaction_id = access.issue(self.address, asset_params, self.qty, self.min_amount)
            logging.info(f"Transaction Id: {transaction_id}")
            return transaction_id
        except Exception:
            logging.error(f"asset already exists")

    def set_asset_params(self, target):
        self.name = target[0]
        self.open = target[1]
        self.address = target[2]
        self.qty = target[3]
        self.min_amount = 0.01

    def send_with_data(self, address, access, data):
        transaction_id = access.sendwithdata(address, {self.name: self.qty}, data)

        return transaction_id
