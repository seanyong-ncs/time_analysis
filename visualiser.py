import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class Visualiser:
    def __init__(self):
        pass

    def customer_staff_ratio_heatmap(self, df, drop_empty=True):
        csr = df['customerStaffRatio'].to_numpy()[11:-3]
        csr = np.expand_dims(csr, axis=0)
        ax = sns.heatmap(csr, cmap = sns.cm.rocket_r, linewidths=.5, annot=True)
        plt.gcf().set_size_inches(16, 1)
        plt.xlabel("Time")
        plt.ylabel("Customer Staff Ratio")
        plt.show()