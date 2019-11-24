

class SPLPV(object):
    """
    Return object class of the stand profit computation
    """
    def __init__(self, splpv, roi_rate):
        self._splpv = splpv
        self._roi_rate = roi_rate

    @property
    def roi_rate(self):
        return self._roi_rate


    @property
    def splpv(self):
        return self._splpv


def stand_profit(cuts_gain, potential_value_increase, expenses, standing_value, number_of_years=1):
    """
    Compute the Stand rofite & loss potential value, it corresponds
    to the net income from a stand over a given period plus the corresponding
    increase in the potential capital value.
    :param cuts_gain: Sum of the gains realised on the cuts (standing value of cut trees)
    :param potential_value_increase: The potential value is obtained by dividing the annual yield by a discount rate
    :param expenses: This is all expenses needed to executes cuts and forest care
    :param standing_value: Current value of the standing trees
    :param number_of_years: Number of years concerned by the calculus, default is 1
    :return: The net income of the stand given a period plus the increase in the potential capital value
    """
    splpv = cuts_gain + potential_value_increase - expenses
    roi_rate = splpv/standing_value/number_of_years*100
    return SPLPV(splpv, roi_rate)