print("Loading...")

scales_char = ['f',   'p',   'n',  'u',  'm',  ' ', 'k', 'M', 'G', 'T', 'P']
scales_num  = [1e-15, 1e-12, 1e-9, 1e-6, 1e-3, 1.0, 1e3, 1e6, 1e9, 1e12, 1e15]
# scales_map = map(scales_char, scales_num)

from PyLTSpice import SimRunner, SpiceEditor, LTspice
from PyLTSpice.LTSpice_RawRead import RawRead
from PyLTSpice import LTSpiceLogReader
import tkinter as tk
from tkinter import filedialog
import os
import math
import numpy as np
import itertools

step_param_names = []
step_param_values = []
meas_names = []
meas_values = []
meas_shape = []

def parse_LTspice_value(value_str: str):
    if value_str[0].isdigit():
        try:
            float(value_str)
            return float(value_str)
        except ValueError:
            index = 0
            while value_str[index].isdigit() or value_str[index] == '.':
                index += 1
            return float(value_str[:index]) * scales_num[scales_char.index(value_str[index])]
        
    else:
        return str

def displayNum(num, n_digit = 3):
    if num == 0.0:
        return "0.0"
    else:
        units = ['f', 'p', 'n', 'μ', 'm', '', 'k', 'M', 'G', 'T', 'P']
        idx = max(min(5, int(math.log10(num)//3)), -5)
        num /= 10**(idx * 3)
        if n_digit:
            return str(round(num, n_digit)) + units[idx + 5]
        return str(round(num)) + units[idx + 5]

def processing_data(raw_file, log_file):
    print("Simulation done: data file %s, log file %s" % (raw_file, log_file))
    # Read waveform and step data
    raw = RawRead(raw_file)

    # Collect wave traces if needed:
    # Example: extract time axis and another signal per step
    # time_trace = raw.get_trace('time')
    # signal_trace = raw.get_trace('V(out)')  # e.g. user-specified
    # time_data = np.stack([time_trace.get_wave(i) for i in steps])
    # signal_data = np.stack([signal_trace.get_wave(i) for i in steps])

    # Parse .meas results
    log = LTSpiceLogReader(log_file)
    idx = int(os.path.basename(log_file).split("__")[0])
    for i in range(len(meas_names)):
        meas_values[i][idx] = log.get_measure_value(meas_names[i])

root = tk.Tk()
root.withdraw()
print("Choose file")
file_path = filedialog.askopenfilename(
    title="Select a LTspice schematic",
    filetypes=[("LTspice schematics", "*.asc")],
)
print(file_path)

# Configures the simulator to use and output folder. Also defines the number of parallel simulations
cpu_cores = os.cpu_count()
print(f"{cpu_cores} cores detected.")
runner = SimRunner(output_folder=os.path.dirname(file_path), simulator=LTspice, parallel_sims=max(cpu_cores/2-1, 1))

print("Creating netlist")
runner.create_netlist(file_path)

print("Processing .step commands")  
netlist_path = file_path[:-4] + ".net"
with open(netlist_path, mode='r') as netlist_file:
    netlist_file_lines = netlist_file.readlines()
with open(netlist_path, mode='w') as netlist_file: 
    for line in netlist_file_lines:
        if line.startswith(".step"):
            # parse the .step statement into array of step values
            line_split = line.split()
            if line.find("oct") > 0: # octave mode
                start_val = parse_LTspice_value(line_split[4])
                stop_val  = parse_LTspice_value(line_split[5])
                n_val_step= parse_LTspice_value(line_split[6])
                step_param_names.append(line_split[3])
                base = 2 ** (1 / n_val_step)
                n_points = math.ceil(round(math.log2(stop_val / start_val) * n_val_step, 3)) + 1
                exponent = np.linspace(0, n_points-1, n_points)
                step_param_values.append(start_val * (np.pow(base, exponent)))
            elif line.find("dec") > 0: # decade mode
                start_val = parse_LTspice_value(line_split[4])
                stop_val  = parse_LTspice_value(line_split[5])
                n_val_step= parse_LTspice_value(line_split[6])
                step_param_names.append(line_split[3])
                base = 10 ** (1 / n_val_step)
                n_points = math.ceil(round(math.log10(stop_val / start_val) * n_val_step, 3)) + 1
                exponent = np.linspace(0, n_points-1, n_points)
                step_param_values.append(start_val * (np.pow(base, exponent)))
            elif line.find("list") > 0: # list mode
                step_param_names.append(line_split[2])
                values = []
                for value_str in line_split[4:]:
                    values.append(parse_LTspice_value(value_str))
                step_param_values.append(np.array(values))
            else: # linear mode
                start_val = parse_LTspice_value(line_split[3])
                stop_val  = parse_LTspice_value(line_split[4])
                increment = parse_LTspice_value(line_split[5])
                step_param_names.append(line_split[2])
                n_points = math.floor((stop_val - start_val) / increment)
                steps = np.linspace(start_val, start_val + n_points * increment, n_points + 1)
                if abs(steps[-1] - stop_val) > 1e-6:
                    steps = np.append(steps, stop_val)
                step_param_values.append(steps)

        else:
            # delete the .step statement to prevent duplicate stepping
            # (only write if this line isn't a .step statement)
            netlist_file.write(line)
            if line.startswith(".meas"):
                line_split = line.split()
                meas_names.append(line_split[1].lower())

meas_shape = [len(meas_names)]
for i in range(len(step_param_names)):
    meas_shape.append(len(step_param_values[i]))
    print("Stepping %s through:" % step_param_names[i])
    for j in range(len(step_param_values[i])):
        print("-> " + displayNum(step_param_values[i][j]))
print("Measuring:")
for i in meas_names:
    print("-> " + i)

# Generate all combinations of step values across parameters
combinations = list(itertools.product(*step_param_values))
# print(np.array(combinations).shape)
meas_values = np.ndarray(shape=(len(meas_names), len(combinations)), dtype=np.float64)

print("Loading netlist")
netlist = SpiceEditor(netlist_path)
netlist.add_instruction(".options threads=2")

print("Running simulation...")
for idx, combo in enumerate(combinations):
    # Set all parameters in the current combination
    for name, val in zip(step_param_names, combo):
        netlist.set_parameter(name, val)
    
    # Generate a unique filename suffix using all param values
    param_str = "_".join(f"{name}={displayNum(val)}" for name, val in zip(step_param_names, combo))
    run_netlist_file = f"{idx}__{netlist.netlist_file.name}_{param_str}.net"
    
    runner.run(netlist, run_filename=run_netlist_file, callback=processing_data)
    print(f"Starting {run_netlist_file} ({idx+1}/{len(combinations)})")
runner.wait_completion()
print("All done! Measurements:")
print(meas_names)
meas_values = meas_values.reshape(meas_shape)
print(meas_values)

print("Loading matplotlib...")
import matplotlib.pyplot as plt
print("plotting measurements")
meas_names_plot = []
meas_index_plot = []
for i in range(len(meas_names)):
    name = meas_names[i]
    if name.startswith("plot_"):
        meas_names_plot.append(name)
        meas_index_plot.append(i)
fig, ax = plt.subplots(len(meas_names_plot))
for i in range(len(meas_names_plot)):
    legend = []
    for j in range(meas_shape[2]):
        if len(meas_names_plot) > 1:
            ax[i].plot(step_param_values[0], meas_values[meas_index_plot[i]].transpose()[j])
            ax[i].set_title(meas_names_plot[i][5:])
            ax[i].set_xscale('log')
        else:
            ax.plot(step_param_values[0], meas_values[meas_index_plot[i]].transpose()[j])
            ax.set_title(meas_names_plot[i][5:])
            ax.set_xscale('log')
        legend.append(f"{step_param_names[1]}={step_param_values[1][j]}")
    fig.legend(legend)
plt.show()
