import math

import stand_profit


class LossPotentialValue(object):

    def __init__(self, volume4DBHFunction, dbhIncreaseFunction, value4DBHFunction):
        self.volume4DBHFunction = volume4DBHFunction
        self.dbhIncreaseFunction = dbhIncreaseFunction
        self.value4DBHFunction = value4DBHFunction
        self.dbhClassWidth = 5

    def computeTreeGain(self,dbh, species):
        v = self.volume4DBHFunction(dbh)
        v2 = self.volume4DBHFunction(dbh+self.dbhClassWidth)
        iD = self.dbhIncreaseFunction(dbh)
        consumptionUnitValue = self.value4DBHFunction(dbh,species)
        consumptionUnitValue2 = self.value4DBHFunction(dbh+self.dbhClassWidth,species)

        consumptionValue = consumptionUnitValue*v
        gain =(consumptionValue * iD * (
                math.log(consumptionUnitValue2 / consumptionUnitValue) + math.log(v2 / v))) / ((dbh+self.dbhClassWidth)-dbh)
        return gain

    def computeTreeVolumeIncrease(self,dbh, species):
        v = self.volume4DBHFunction(dbh)
        v2 = self.volume4DBHFunction(dbh+self.dbhClassWidth)
        iD = self.dbhIncreaseFunction(dbh)

        volumeIncrease =(v*iD * (math.log(v2 / v))) / ((dbh+self.dbhClassWidth)-dbh)
        return volumeIncrease


    def computeConsumptionValue(self,dbh, species):
        v = self.volume4DBHFunction(dbh)
        consumptionUnitValue = self.value4DBHFunction(dbh,species)
        consumptionValue = consumptionUnitValue*v
        return consumptionValue

    def computeTreeInterest(self, dbh, species):
        gain = self.computeTreeGain(dbh, species)
        consumptionValue = self.computeConsumptionValue(dbh,species)
        return gain/consumptionValue

    def getTreeLPV(self,dbh, species):
        v = self.volume4DBHFunction(dbh)
        v2 = self.volume4DBHFunction(dbh)
        iD = self.dbhIncreaseFunction(dbh)
        consumptionValue = self.value4DBHFunction(dbh)

        return 0