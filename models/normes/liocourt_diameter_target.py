import math

import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.axisartist.axis_artist import UnimplementedException
from pandas.core.computation.ops import MathCall

import stand_profit
from loss_potential_value import LossPotentialValue
from models.ch_ne.ne_price_calculator import NEPriceCalculator

class StandGenerator(object):
    def __init__(self, target_diameter, target_basal_area, **kwargs):
        self.target_diameter = target_diameter
        self.target_basal_area = target_basal_area

class LiocourtTargetDiameterGenerator(StandGenerator):
    def __init__(self, liocourt_factor=1.3, diameter_class_width=5.0, threshold=12.5, **stand_parameters):
        super(LiocourtTargetDiameterGenerator, self).__init__(**stand_parameters)
        self.liocourt_factor = liocourt_factor
        self.diameter_class_width = diameter_class_width
        self.threshold = threshold

    def plot_ideal_curve(self):
        trees = self.computeLiocourtTreeStand()
        print(trees.groupby('DBH').size())
        ax = trees.groupby('DBH').size().plot(x="DBH")

    def computeLiocourtTreeStand(self):
        trees_DF = pd.DataFrame(columns=['DBH', 'SPECIES'])
        nb_classes = int((self.target_diameter-self.threshold)/self.diameter_class_width)+1
        diameter_class = self.threshold

        N_4_norm_diameter_class= pd.DataFrame(columns=['DBH', 'N_norm', 'G_norm', 'N'])
        for i in range(0, nb_classes, 1):
            number_of_trees = 1*pow(self.liocourt_factor, nb_classes-i-1)
            if not number_of_trees or not math.isfinite(number_of_trees):
                continue
            new_line = [[(i*self.diameter_class_width+self.threshold+self.diameter_class_width/2),
                         number_of_trees]]
            N_4_norm_diameter_class=N_4_norm_diameter_class.append(pd.DataFrame(new_line, columns=['DBH','N_norm']), ignore_index = True)
            N_4_norm_diameter_class['G_norm'] = N_4_norm_diameter_class.apply(
                lambda x : pow(x['DBH']/100,2)/4 * math.pi *x['N_norm']
                , axis=1)

        G_basis = N_4_norm_diameter_class['G_norm'].sum()
        N_4_norm_diameter_class['N'] = N_4_norm_diameter_class.apply(
                lambda x : x['N_norm']*self.target_basal_area/G_basis
                , axis=1)
        print(N_4_norm_diameter_class)
            # remaining_nb_trees = int(number_of_trees)
            # species_nb_trees = number_of_trees
            # new_trees = [[(i*self.diameter_class_width+self.threshold+self.diameter_class_width/2), 'EP']]*species_nb_trees
            # trees_DF=trees_DF.append(pd.DataFrame(new_trees, columns=['DBH','SPECIES']), ignore_index = True)
            # diameter_class = diameter_class+self.diameter_class_width


        #trees_DF['volume_increase'] = self._treesDF.apply(lambda x: lpvCalculator.computeTreeVolumeIncrease(x['DBH'], x['SPECIES']),axis=1)
        return trees_DF


if __name__ == "__main__":

    ## Test 1
    species_mix_dict = {
        "EP" : 0.,
        "HE" : 0.,
        "CH" : 1.,
        "SA" : 0.,
        "ER" : 0.
    }

    from models.ch_ne.ne_volume_calculator import NEVolumeCalculator

    target_diameter = 60
    target_basal_area = 24
    stand_parameters = {
        "target_diameter" : target_diameter,
        "target_basal_area" : target_basal_area,
        "liocourt_factor" : 1.4
    }
    ## Sensitivity analysis
    liocourtGenerator = LiocourtTargetDiameterGenerator(**stand_parameters)
    liocourtGenerator.plot_ideal_curve()
    print(NEVolumeCalculator()(liocourtGenerator.computeLiocourtTreeStand()))


