import pandas as pd
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
class NEPriceCalculator(object):

    def __init__(self, price_factor=1):
        self._priceDF = pd.read_excel(os.path.join(dir_path, "prix_fictifs.xlsx"))
        self.priceFactor = price_factor
    def price(self, dbh, species):
        temporary_DF = pd.DataFrame(self._priceDF)
        temporary_DF['dif'] = (temporary_DF.d - dbh).abs()
        temporary_DF.sort_values(['dif','d'], ascending=[True,False], inplace=True)
        if species in temporary_DF.columns.values:
            return temporary_DF.iloc[0][species]*self.priceFactor
        return 0

