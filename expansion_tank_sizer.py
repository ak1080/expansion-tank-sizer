"""
Description: Program for sizing expansion tanks in closed loop hydronic systems. The result is a minimum tank acceptance
volume based on user input parameters related to the hydronic system.
By: Alex Kalmbach
Date: 12/06/2024
Source: This data has been excerpted from AMTROL’s Engineering Handbook - Chapter Two, Section B, “Hydro-pneumatics in
Hot Water Heating Systems”.

Critical Sizing Test Case (from Amtrol article):
system volume = 4400
max avg op temp = 230°F
min tank pressure = 50 psig
max tank pressure = 110 psig
fill temperature = 70°F
--> Min calculated tank volume = 421.6 gallons
"""

import tkinter as tk
from tkinter import ttk, messagebox
from expansion_data import get_net_expansion, get_acceptance_factor

ATM_PRESS = 14.7  # Atmospheric pressure in PSI


def ASHRAE_sizing_method(avg_operating_temp, sys_vol, min_tank_psig, max_tank_psig):
    """ASHRAE's Equation for determining the expansion tank volume for a diaphragm tank."""
    return (0.00041 * avg_operating_temp - 0.0466) * sys_vol / (
            1 - (min_tank_psig + ATM_PRESS) / (max_tank_psig + ATM_PRESS)
    )

def critical_sizing_method(sys_vol, init_temp, max_temp, min_tank_psig, max_tank_psig):
    """Preferred method for expansion tank sizing."""
    net_exp_factor = get_net_expansion(initial_temp=init_temp, max_temp=max_temp)
    if isinstance(net_exp_factor, str):
        return net_exp_factor  # Return error message if temperature is out of range
    accept_factor = get_acceptance_factor(min_pressure=min_tank_psig, max_pressure=max_tank_psig)
    if isinstance(accept_factor, str):
        return accept_factor  # Return error message if pressure is out of range
    return sys_vol * net_exp_factor / accept_factor


def calculate_tank_volumes():
    """Calculate tank volumes using both methods."""
    try:
        # Shared Parameters
        sys_vol = float(shared_sys_vol_entry.get())  # User input required
        min_tank_psig = int(shared_min_pressure_var.get())
        max_tank_psig = int(shared_max_pressure_var.get())

        # ASHRAE Method Inputs
        avg_operating_temp = int(ashrae_avg_temp_var.get())

        # Critical Method Inputs
        init_temp = int(critical_init_temp_var.get())
        max_temp = int(critical_max_temp_var.get())
    except ValueError:
        messagebox.showerror("Input Error", "Please provide valid inputs.")
        return

    # ASHRAE method
    ashrae_volume = ASHRAE_sizing_method(avg_operating_temp, sys_vol, min_tank_psig, max_tank_psig)

    # Critical method
    critical_volume = critical_sizing_method(sys_vol, init_temp, max_temp, min_tank_psig, max_tank_psig)

    # Display results
    results_text.set(
        f"ASHRAE Method Min Tank Volume: {ashrae_volume:.2f} gallons\n"
        f"Critical Method Min Tank Volume: {critical_volume:.2f} gallons"
        if isinstance(critical_volume, float) else f"Critical Method Error: {critical_volume}"
    )


# GUI Setup
root = tk.Tk()
root.title("Expansion Tank Sizing Calculator")


# Create a consistent grid layout helper function
def add_row(frame, label_text, widget, row):
    label = tk.Label(frame, text=label_text, anchor="w")
    label.grid(row=row, column=0, sticky="w", padx=5, pady=5)
    widget.grid(row=row, column=1, sticky="ew", padx=5, pady=5)


# Shared Parameters Section
shared_frame = tk.LabelFrame(root, text="Shared Parameters", padx=10, pady=10)
shared_frame.pack(padx=10, pady=5, fill="x")

shared_sys_vol_entry = tk.Entry(shared_frame)
shared_min_pressure_var = tk.StringVar()
shared_max_pressure_var = tk.StringVar()

shared_pressure_options = [5, 10, 12, 15, 20, 30, 40, 50, 60, 70, 80]
max_pressure_options = [27, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 100, 110]

add_row(shared_frame, "Total System Volume (gal):", shared_sys_vol_entry, row=0)
add_row(shared_frame, "Min Tank Pressure (psig):",
        ttk.Combobox(shared_frame, textvariable=shared_min_pressure_var, values=shared_pressure_options,
                     state="readonly"), row=1)
add_row(shared_frame, "Max Tank Pressure (psig):",
        ttk.Combobox(shared_frame, textvariable=shared_max_pressure_var, values=max_pressure_options, state="readonly"),
        row=2)

# ASHRAE Method Section
ashrae_frame = tk.LabelFrame(root, text="ASHRAE Method Inputs", padx=10, pady=10)
ashrae_frame.pack(padx=10, pady=5, fill="x")

ashrae_avg_temp_var = tk.StringVar()
avg_temp_options = range(160, 281, 10)

add_row(ashrae_frame, "Average Operating Temp (°F):",
        ttk.Combobox(ashrae_frame, textvariable=ashrae_avg_temp_var, values=list(avg_temp_options), state="readonly"),
        row=0)

# Critical Method Section
critical_frame = tk.LabelFrame(root, text="Critical Method Inputs", padx=10, pady=10)
critical_frame.pack(padx=10, pady=5, fill="x")

critical_init_temp_var = tk.StringVar()
critical_max_temp_var = tk.StringVar()

init_temp_options = [40, 50, 60, 70, 80, 90, 100, 110, 120]
max_temp_options = [120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240]

add_row(critical_frame, "Initial Water Temp (°F):",
        ttk.Combobox(critical_frame, textvariable=critical_init_temp_var, values=init_temp_options, state="readonly"),
        row=0)
add_row(critical_frame, "Max Water Temp (°F):",
        ttk.Combobox(critical_frame, textvariable=critical_max_temp_var, values=max_temp_options, state="readonly"),
        row=1)

# Calculate Button
calculate_btn = tk.Button(root, text="Calculate", command=calculate_tank_volumes)
calculate_btn.pack(pady=10)

# Results Display
results_text = tk.StringVar()
results_label = tk.Label(root, textvariable=results_text, justify="left", font=("Arial", 10), wraplength=400)
results_label.pack(pady=10)

# Configure grid for consistent layout
for frame in [shared_frame, ashrae_frame, critical_frame]:
    frame.grid_columnconfigure(1, weight=1)

# Start the GUI loop
root.mainloop()

