import hh
import experiments as expy
import validation as vali
import tools
import os
import csv
import matplotlib.pyplot as plt
import numpy as np

### SIMULATION OF MODEL FOR MULTIPLE TEMPS
# model = hh.HodgkinHuxley()
# curr_params = expy.CurrentParameters()
# temp_exp = expy.TempExperiment()

# # Set parameters2
# temp_exp.set_temp_exp_data(0, 60, 100, 1, model, curr_params)
# curr_params.set_curr_data(50, 0, 1, 0, 0)
# model.set_run_time(20)

# # Simulate model and show plot.
# temp_exp.run(1)
# temp_exp.store_csv("results_100_deter_1.csv")
# temp_exp.plot()

### LOAD RESULTS AND SHOW
file_name = "results_100_deter_1.csv"
assert os.path.isfile(file_name)

ts = []
ys = []

with open(file_name, newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        ts.append(float(row[0]))
        ys.append(float(row[1]))

# tot de 48ste gaat ie omlaat
ts = ts[7:77]
ys = ys[7:77]

ts_interp = ts[:48]
ys_interp = ys[:48]
z2 = np.polyfit(ts_interp, ys_interp, 2)
z3 = np.polyfit(ts_interp, ys_interp, 3)
z4 = np.polyfit(ts_interp, ys_interp, 4)
p2 = np.poly1d(z2)
p3 = np.poly1d(z3)
p4 = np.poly1d(z4)

print("MS2: ", np.mean(np.square(ys_interp - p2(ts_interp))))
print("MS3: ", np.mean(np.square(ys_interp - p3(ts_interp))))
print("MS4: ", np.mean(np.square(ys_interp - p4(ts_interp))))

plt.scatter(ts, ys, label="datapoints")
plt.plot(ts, p2(ts), label="Quadratic fit: $0.022T^2 - 1.33T + 22.6$", color='green', linestyle='-.')
plt.plot(ts, p3(ts), label="Cubic fit: $-0.0013T^3 + 0.095T^2 - 2.5T + 27.8$", color='black', linestyle='-.')
plt.title("Duration of action potential for 70 temperatures between 0 and 45 degrees Celcius\nwith injected current of 50 $\mu$A/cm$^2$.")
plt.ylabel("t (ms)")
plt.xlabel("T (°C)")
plt.ylim((0, 20))
plt.axvline(ts[47], linestyle=':', color='red')
plt.legend()
plt.show()
