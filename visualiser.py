from re import X
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os


class Visualiser:
    def __init__(self):
        self.script_path, _ = os.path.split(os.path.abspath(__file__))

    def max_occupancy_heatmap(self, mo_list, drop_empty=True):
        mo_array = []
        x_axis_labels = []
        y_axis_labels = []
        # Initial array
        for df in mo_list:
            mo = df['maxOccupants'].to_numpy()[11:-3].astype(np.float)
            date = df['timeStart'][0].strftime("%y-%m-%d")
            y_axis_labels.append(date)
            mo_array.append(mo)

        x_axis_labels = np.array(list(range(24)))[11:-3] # Hardcoded for testing purposes
        self.create_heatmap(mo_array, x_axis_labels, y_axis_labels, "Max Occupants Per Timeslot")

    def customer_staff_ratio_heatmap(self, csr_list, drop_empty=True):
        csr_array = []
        x_axis_labels = []
        y_axis_labels = []
        # Initial array
        for df in csr_list:
            csr = df['customerStaffRatio'].to_numpy()[11:-3]
            date = df['timeStart'][0].strftime("%y-%m-%d")
            y_axis_labels.append(date)
            csr_array.append(csr)

        x_axis_labels = np.array(list(range(24)))[11:-3] # Hardcoded for testing purposes
        self.create_heatmap(csr_array, x_axis_labels, y_axis_labels, "Customer to Staff Ratio")

    def create_heatmap(self, array, x_axis_labels, y_axis_labels, title):
        sns.heatmap(array, xticklabels=x_axis_labels, yticklabels=y_axis_labels,
                         cbar=False, cmap = sns.cm.rocket_r, annot=True, fmt=".3g", annot_kws={"size":16})
        plt.gcf().set_size_inches(10, 4)
        plt.xlabel("Time - 24h")
        plt.title(title)
        plt.yticks(rotation=45)

        # Define save path and create output folder if it doesn't exist
        save_dir = os.path.join(self.script_path, "visualisations")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir) 

        plt.savefig(os.path.join(self.script_path, "visualisations", title.replace(" ", "_") + ".png"))

        plt.figure().clear()
        plt.close()
        plt.cla()
        plt.clf()