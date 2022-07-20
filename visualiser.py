from re import X
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import math


class Visualiser:
    def __init__(self):
        self.script_path, _ = os.path.split(os.path.abspath(__file__))

    def max_occupancy_heatmap(self, df_list, drop_empty=True):
        arr = [df['maxOccupants'].to_numpy()[11:-3].astype(np.float) for df in df_list]
        self.create_heatmap(arr, df_list, "Max Occupants Per Timeslot")

    def customer_staff_ratio_heatmap(self, df_list, drop_empty=True):
        arr = [df['customerStaffRatio'].to_numpy()[11:-3] for df in df_list]
        self.create_heatmap(arr, df_list, "Customer to Staff Ratio")

    def customer_staff_ratio_treshold_heatmap(self, df_list, drop_empty=True):
        # Get treshold
        tres = df_list[0]['csrThreshold'][0]
        arr = [df['interval'].to_numpy()[11:-3].astype(np.float) for df in df_list]
        format = lambda x: f"{math.ceil(x/60)}m" if x > 0 else ""
        format_v = np.vectorize(format)
        annots = format_v(arr)
        max_label = format(np.amax(arr))
        self.create_heatmap(arr, df_list, f"Customer to Staff Ratio at CSR >= {tres}", annots = annots, max_label=max_label)

    def create_heatmap(self, array, df_list, title, annots=None, max_label=None):

        y_axis_labels = [df['timeStart'][0].strftime("%m-%d (%a)") for df in df_list]
        x_axis_labels = np.array(list(range(24)))[11:-3] # Hardcoded for testing purposes
        annot = True if annots is None else annots
        ax = sns.heatmap(array, xticklabels=x_axis_labels, yticklabels=y_axis_labels, linewidths=.5,
                         cbar=True, cmap = sns.cm.mako_r, annot=annot, fmt="", annot_kws={"size":16 })
        c_bar = ax.collections[0].colorbar
        if max_label is not None:
            c_bar.set_ticks([0, np.amax(array)])
            c_bar.set_ticklabels(['0m', max_label])
            c_bar.set_label('# of minutes where CSR >= Treshold', rotation=270)


        plt.gcf().set_size_inches(16, len(df_list) * 1.25)
        plt.xlabel("Time - 24h")
        plt.title(title)
        plt.yticks(rotation=0)

        # Define save path and create output folder if it doesn't exist
        save_dir = os.path.join(self.script_path, "visualisations")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir) 

        plt.savefig(os.path.join(self.script_path, "visualisations", title.replace(">=", "gte").replace(" ", "_") + ".png"))
        plt.clf()