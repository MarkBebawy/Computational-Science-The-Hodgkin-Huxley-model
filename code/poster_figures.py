import hh
import experiments as expy
import validation as vali
import tools


model = hh.HodgkinHuxley()
curr_params = expy.CurrentParameters()        
temp_exp = expy.TempExperiment()

# Set parameters2
temp_exp.set_temp_exp_data(0, 60, 100, 1, model, curr_params)
curr_params.set_curr_data(50, 0, 1, 0, 0)
model.set_run_time(20)

# Simulate model and show plot.
temp_exp.run(1)
temp_exp.store_csv("results_100_deter_1.csv")
temp_exp.plot()
