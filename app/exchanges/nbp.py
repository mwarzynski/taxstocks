import csv
from datetime import datetime, timedelta
from typing import Dict
from decimal import Decimal
from os import listdir
from os.path import isfile, join


from app.exchange import Currency, Exchange


class NBP(Exchange):
    """
    NBP Exchange stands for "National Bank of Poland" exchange.
    It provides the 'standard' exchange rates for currencies (applicable for Polish citizens).
    """

    _day_currency_ratio: Dict[datetime, Dict[Currency, Decimal]]

    def __init__(self, folder: str = "data/nbp"):
        files = [f for f in listdir(folder) if isfile(join(folder, f))]
        self._day_ratio: Dict[datetime, Dict[Currency, Decimal]] = {}
        for file in files:
            self._load(join(folder, file))

    def _load(self, file_name: str):
        with open(file_name, "r") as f:
            reader = csv.reader(f, delimiter=";")
            currencies = next(reader)  # skip header row (which contains description of columns)
            index_eur, index_usd = 0, 0
            for i, currency in enumerate(currencies):
                if currency == "1USD":
                    index_usd = i
                elif currency == "1EUR":
                    index_eur = i
            for row in reader:
                date = datetime.strptime(row[0], "%Y%m%d")
                ratios = {
                    Currency.EUR: Decimal(row[index_eur].replace(",", ".")),
                    Currency.USD: Decimal(row[index_usd].replace(",", ".")),
                }
                self._day_ratio[date] = ratios

    def ratio(
        self,
        day: datetime,
        c_from: Currency,
        c_to: Currency,
        max_days_prior_to_check: int = 5,
    ) -> Decimal:
        if c_from is Currency.PLN:
            return Decimal(1)
        day = day - timedelta(days=1)
        try:
            return self._day_ratio[day.replace(hour=0, minute=0)][c_from]
        except KeyError as e:
            if max_days_prior_to_check <= 0:
                raise e
            return self.ratio(day, c_from, c_to, max_days_prior_to_check=max_days_prior_to_check - 1)
