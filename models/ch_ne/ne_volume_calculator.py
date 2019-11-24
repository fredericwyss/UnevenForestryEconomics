from simulator import VolumeCalculator
import pandas as pd
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
class NEVolumeCalculator(VolumeCalculator):
    def __init__(self):
        self._volumeDF = pd.read_excel(os.path.join(dir_path,"tarif_ne.xlsx"))

    def volumeForDBH(self,dbh):
        temporary_DF = pd.DataFrame(self._volumeDF)
        temporary_DF['dif'] = (temporary_DF.CAT_DIAMETRE_MOYEN - dbh/100.).abs()
        temporary_DF.sort_values(['dif','CAT_DIAMETRE_MOYEN'], ascending=[True,False], inplace=True)
        return temporary_DF.CAT_VOLUME.iloc[0]

    def __call__(self, trees):
        trees['v']=trees.apply(lambda x : self.volumeForDBH(x['DBH']),axis=1)
        return trees['v'].sum()

if __name__ == "__main__":
    NeVC = NEVolumeCalculator()
    print("Volume:%s"%NeVC.volumeForDBH(32.5))