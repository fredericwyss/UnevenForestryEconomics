import math

import pandas as pd
from mpl_toolkits.axisartist.axis_artist import UnimplementedException

import stand_profit
from loss_potential_value import LossPotentialValue
from models.ch_ne.ne_price_calculator import NEPriceCalculator


def get_liocourt():
    return pd.read_excel("models/liocourt.xlsx",header=0)

class VolumeCalculator(object):
    def __init__(self):
        pass

    def volumeForDBH(self, dbh):
        raise UnimplementedException



class Simulator(object):
    def __init__(self, treesDF,  volumeCalculator, diameterIncreaseFunction, valueFunction,discount_rate=0.03):
        self._treesDF=pd.DataFrame(treesDF)
        self._volumeCalculator = volumeCalculator
        self._dbhIncFunction = diameterIncreaseFunction
        self.value4DBH_SpeciesFunction = valueFunction
        self._discount_rate = discount_rate
        self.computeValues()
    def computeValues(self):

        lpvCalculator = LossPotentialValue(self._volumeCalculator.volumeForDBH, self._dbhIncFunction, self.value4DBH_SpeciesFunction)
        self._treesDF['gain'] = self._treesDF.apply(lambda x: lpvCalculator.computeTreeGain(x['DBH'],x['SPECIES']),axis=1)
        self._treesDF['consumption_value'] = self._treesDF.apply(lambda x: lpvCalculator.computeConsumptionValue(x['DBH'], x['SPECIES']),
                                                    axis=1)
        self._treesDF['potential_value'] = self._treesDF["gain"]/self._discount_rate
        self._treesDF['volume_increase'] = self._treesDF.apply(lambda x: lpvCalculator.computeTreeVolumeIncrease(x['DBH'], x['SPECIES']),axis=1)

    def volume(self):
        self._treesDF['v']=self._treesDF.apply(lambda x : self._volumeCalculator.volumeForDBH(x['DBH']),axis=1)
        return self._treesDF['v'].sum()

    def standProfit(self,expenses):


        print("volume inc:%s, gain:%s,consumption_value:%s, ror:%s"%(self._treesDF['volume_increase'].sum(),self._treesDF['gain'].sum(),self._treesDF['consumption_value'].sum(),self._treesDF['gain'].sum()/0.03/self._treesDF['consumption_value'].sum()))

        # self._treesDF[['volume_increase','gain']].plot()

        splpv = stand_profit.stand_profit(self._treesDF['gain'].sum(), 0, expenses,self._treesDF['consumption_value'].sum())

        print("stand_profit:%s, roi_rate:%s"%(splpv.splpv,splpv.roi_rate))
        return splpv

    def targetDiameter(self):
        self._length = len(self._treesDF.index)
        self._treesDF['is_profitable'] = self._treesDF['potential_value'] >= self._treesDF['consumption_value']
        weighted_diameter = 0
        for species in self._treesDF['SPECIES'].unique():
            species_DF = self._treesDF[self._treesDF['SPECIES']==species]
            weight = len(species_DF.index)/self._length
            species_target_diameter = species_DF.loc[species_DF['is_profitable'] == False]['DBH'].min()
            print("specie:%s, target diameter:%s, weight:%s (%s,%s)"%(species,species_target_diameter,weight,len(species_DF.index), self._length))
            if not math.isfinite(species_target_diameter ):
                species_target_diameter = weighted_diameter
            weighted_diameter = weighted_diameter + species_target_diameter * weight
        print("discount_rate:%s"%(self._discount_rate))
        #print(self._treesDF[['DBH','potential_value','consumption_value','is_profitable']])
        print("Target diameter :%s"%(weighted_diameter))
        return weighted_diameter

class LiocourtNormId:
    N1_3=1
    N1_35=2
    N1_4=3
    N1_5=4
def computeLiocourtTreeStand(speciesMix, liocourtNormId ):
    liocourt_DF = get_liocourt()
    trees_DF =  pd.DataFrame(columns=['DBH', 'SPECIES'])
    for index, row in liocourt_DF.iterrows():
        if row.size <=1 :
            continue
        number_of_trees = row[liocourtNormId]
        if not number_of_trees or not math.isfinite(number_of_trees):
            continue
        remaining_nb_trees = int(number_of_trees)
        for species, percentage in species_mix_dict.items():
            species_nb_trees = math.ceil(percentage * number_of_trees)
            if species_nb_trees > remaining_nb_trees:
                species_nb_trees=remaining_nb_trees
            #remaining number of trees
            remaining_nb_trees = remaining_nb_trees - species_nb_trees
            if species_nb_trees <=0:
                continue
            new_trees = [[row.d, species]]*species_nb_trees
            trees_DF=trees_DF.append(pd.DataFrame(new_trees, columns=['DBH','SPECIES']), ignore_index = True)
    return trees_DF

legend_dict =  {"expenses":"Dépenses",
                           "standard_increase":"Accroissement",
                           "price_factor":"Prix du bois",
                           "discount_rate":"Taux d'intérêt",
                           "volume":"Volume sur pied"}
def sensitivity_analysis(parameters, analysed_parameters, analyses_volume, analyses_splpv, analyses_roi_rate, analyses_target_diameter):
    analysis_range= range(-40, 50, 40)
    columns = list(analysed_parameters) + ["volume", ] if analyses_volume else list(analysed_parameters)

    sensitivityDF_roi_rate = pd.DataFrame(index=analysis_range, columns=columns)
    sensitivityDF_stand_profit = pd.DataFrame(index=analysis_range, columns=columns)
    sensitivityDF_target_diameter = pd.DataFrame(index=analysis_range, columns=columns)

    ## Volumes with liocourt
    if analyses_volume:
        liocourt1_3 = Simulator(computeLiocourtTreeStand(species_mix_dict, LiocourtNormId.N1_3), NEVolumeCalculator(),
                                lambda x: standard_increase*0.947713, NEPriceCalculator(price_factor).price,parameters["discount_rate"])
        liocourt1_35 = Simulator(computeLiocourtTreeStand(species_mix_dict, LiocourtNormId.N1_35), NEVolumeCalculator(),
                                 lambda x: standard_increase, NEPriceCalculator(price_factor).price,parameters["discount_rate"])
        liocourt1_4 = Simulator(computeLiocourtTreeStand(species_mix_dict, LiocourtNormId.N1_4), NEVolumeCalculator(),
                                lambda x: standard_increase*1.07656, NEPriceCalculator(price_factor).price,parameters["discount_rate"])
        liocourt1_5 = Simulator(computeLiocourtTreeStand(species_mix_dict, LiocourtNormId.N1_5), NEVolumeCalculator(),
                                lambda x: standard_increase*1.24699*0.942451, NEPriceCalculator(price_factor).price,parameters["discount_rate"])

        reference_volume = liocourt1_35.volume()
        for liocourt_DF in (liocourt1_3,liocourt1_35,liocourt1_4,liocourt1_5):
            volume=liocourt_DF.volume()
            index = [100*(volume/reference_volume-1)]
            if analyses_roi_rate or analyses_splpv:
                splpv =liocourt_DF.standProfit(parameters["expenses"])
                print("ref:%s,v:%s,f:%s"%(reference_volume,volume,reference_volume/volume))
                if analyses_splpv:
                    sensitivityDF_stand_profit= sensitivityDF_stand_profit.append(pd.DataFrame([splpv.splpv,],index=index, columns=['volume',]), ignore_index=False)
                if analyses_roi_rate:
                    sensitivityDF_roi_rate = sensitivityDF_roi_rate.append(pd.DataFrame([splpv.roi_rate,],index=index, columns=['volume',]), ignore_index=False)
            if analyses_target_diameter:
                sensitivityDF_target_diameter= sensitivityDF_target_diameter.append(pd.DataFrame([liocourt_DF.targetDiameter(),],index=index, columns=['volume',]), ignore_index=False)

        if analyses_roi_rate:
            sensitivityDF_roi_rate.sort_index(inplace=True)
            sensitivityDF_roi_rate=sensitivityDF_roi_rate.interpolate(method='slinear')

        if analyses_splpv:
            sensitivityDF_stand_profit.sort_index(inplace=True)
            sensitivityDF_stand_profit=sensitivityDF_stand_profit.interpolate(method='slinear')
        if analyses_target_diameter:
            sensitivityDF_target_diameter.sort_index(inplace=True)
            sensitivityDF_target_diameter=sensitivityDF_target_diameter.interpolate(method='slinear')

    ## Other factors
    indexes = sensitivityDF_roi_rate.index.tolist() if analyses_roi_rate else sensitivityDF_stand_profit.index.tolist()  if analyses_splpv else sensitivityDF_target_diameter.index.tolist()
    print("indexes:%s"%(indexes))
    for factor in indexes:

        print("sensivity analysis ... : %s",factor)
        for key in analysed_parameters:
            parameters[key]=parameters[key]*(1+factor/100)
            print("factor:%s"%(parameters[key]))
            liocourt1_35 = Simulator(computeLiocourtTreeStand(species_mix_dict, LiocourtNormId.N1_35), NEVolumeCalculator(),
                                    lambda x: parameters["standard_increase"],
                                     NEPriceCalculator(parameters["price_factor"]).price,
                                     parameters["discount_rate"])

            if analyses_splpv or analyses_roi_rate:
                splpv = liocourt1_35.standProfit(parameters["expenses"])
            if analyses_roi_rate:
                sensitivityDF_roi_rate.loc[factor,key]=splpv.roi_rate
            if analyses_splpv:
                sensitivityDF_stand_profit.loc[factor,key]=splpv.splpv
            if analyses_target_diameter and key != "expenses" :
                sensitivityDF_target_diameter.loc[factor,key]=liocourt1_35.targetDiameter()
            parameters[key] = parameters[key]/(1+factor/100)

    print(sensitivityDF_stand_profit)
    if analyses_roi_rate:
        sensitivityDF_roi_rate.rename(columns=legend_dict,
            inplace=True)
        ax = sensitivityDF_roi_rate.plot()
        ax.set_xlabel("Variation [%]")
        ax.set_ylabel("Taux de placement [%]")

    if analyses_splpv:
        sensitivityDF_stand_profit.rename(columns=legend_dict,
            inplace=True)
        ax = sensitivityDF_stand_profit.plot()
        ax.set_xlabel("Variation [%]")
        ax.set_ylabel("RNEVP [CHF/ha]")

    if analyses_target_diameter:
        sensitivityDF_target_diameter.rename(columns=legend_dict,
            inplace=True)
        ax = sensitivityDF_target_diameter.plot()
        ax.set_xlabel("Variation [%]")
        ax.set_ylabel("Diamètre cible moyen [cm]")



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

    standard_increase = 0.5
    expenses = 550
    price_factor= 0.5*0.7
    discount_rate= 0.02

    ## Sensitivity analysis
    parameters={
        "expenses" : expenses,
        "standard_increase" : standard_increase,
        "price_factor" : price_factor,
        "discount_rate" : discount_rate

    }
    analysed_parameters = ["expenses",
                           "standard_increase",
                           "price_factor",
                           "discount_rate"]
    sensitivity_analysis(parameters, analysed_parameters, analyses_volume=True, analyses_splpv=True, analyses_roi_rate=True, analyses_target_diameter=True)


