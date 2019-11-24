import pandas as pd
import numpy as np
import random
import string
import matplotlib.pyplot as plt

threshold = 20
k = 5
N = 200

#http://docs.scipy.org/doc/numpy/reference/generated/numpy.random.randint.html
#http://stackoverflow.com/a/2257449/2901002

df = pd.DataFrame(index=  np.arange(threshold, N ,k)   )

def y(di):
    a = 1.3
    b = 4
    return a*np.exp(-b*(di/100))

def increase(di):
    a = 0.01
    b = 3
    return a*np.exp(b*(di/100))


# df['increase'] = increase(df.index)
df['y'] = y(df.index)
df.plot()