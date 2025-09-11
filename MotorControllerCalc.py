from math import pi
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Settings
V_in = 3.6 * 140
I_out_max = 240
D_arr = np.linspace(0, 1, 101) # ratio of motor rpm to max rpm
I_out_arr = np.linspace(0, I_out_max, I_out_max+1)
f_sw = 40e3
V_ripple = 10
T_a = 40
L_motor = 183e-6
n_steps = 100 # number of integration steps over 90 deg

# https://www.infineon.com/dgdl/Infineon-IMDQ75R007M2H-DataSheet-v02_00-EN.pdf?fileId=8ac78c8c95d1335f0195eb5bad7f665c
# Electrical info
# Q_g = 171e-9
# V_f = 4.1
# V_g = 18
# R_on = 8e-3
# E_on = 0.264e-3
# E_off = 0.508e-3
# E_recov = 0.263e-3
# # Thermal info
# T_Jmax = 150
# R_thJC = 0.14

# https://www.infineon.com/dgdl/Infineon-IMDQ75R007M2H-DataSheet-v02_00-EN.pdf?fileId=8ac78c8c95d1335f0195eb5bad7f665c x2
# Electrical info
# Q_g = 171e-9 * 2
# V_f = 4.1
# V_g = 18
# R_on = 8e-3 / 2
# E_on = 0.264e-3 * 2
# E_off = 0.508e-3 * 2
# E_recov = 0.263e-3 * 2
# # Thermal info
# T_Jmax = 125
# R_thJC = 0.07

# https://semiq.com/wp-content/uploads/2024/06/gcmx005a120s3b1-n.pdf
# Electrical info
Q_g = 901e-9
V_f = 3.6
V_g = 25
R_on = 6e-3
E_on = 2.71e-3
E_off = 1.23e-3
E_recov = 1.92e-3
# Thermal info
T_Jmax = 125
R_thJC = 0.083

# https://semiq.com/wp-content/uploads/2023/09/GCMX010A120B2B1P.pdf
# Electrical info
# Q_g = 476e-9
# V_f = 3.6
# V_g = 25
# R_on = 12e-3
# E_on = 1.54e-3
# E_off = 0.49e-3
# E_recov = 0.53e-3
# # Thermal info
# T_Jmax = 175
# R_thJC = 0.2

# https://semiq.com/wp-content/uploads/2023/09/GCMX020A120B2B1P.pdf
# Electrical info
# Q_g = 241e-9
# V_f = 3.9
# V_g = 25
# R_on = 25e-3
# E_on = 0.72e-3
# E_off = 0.16e-3
# E_recov = 0.31e-3
# # Thermal info
# T_Jmax = 175
# R_thJC = 0.39

P_sw_arr = np.zeros((len(D_arr), len(I_out_arr)), dtype = float)
P_cond_arr = np.zeros((len(D_arr), len(I_out_arr)), dtype = float)
P_out_arr = np.zeros((len(D_arr), len(I_out_arr)), dtype = float)

I_ripple_max = 0 # for calculating C_in

for i in range(len(D_arr)):
	D_pk = D_arr[i]
	for j in range(len(I_out_arr)):
		I_out_pk = I_out_arr[j] * 1.4142
		sin90 = np.sin(np.linspace(0, pi/2, n_steps))
		V_back = V_in * D_pk * sin90 # motor back EMF assuming ideal circular motor
		I_out = I_out_pk * sin90 # motor current assuming ideal circular motor
		D = 0.5 + D_pk * sin90 / 2 # instantaneous real duty cycle
		P_out = abs(I_out * V_back)
		I_ripple = (V_in - V_back) / L_motor / f_sw * D / 2 # current ripple amplitude
		I_ripple_max = max(I_ripple_max, I_ripple.max())
		P_sw = ((I_out > I_ripple) * E_on + E_off) * f_sw
		P_cond = (I_out**2 + I_ripple**2/3) * R_on
		P_sw_arr[i][j] = np.mean(P_sw)
		P_cond_arr[i][j] = np.mean(P_cond)
		P_out_arr[i][j] = np.mean(P_out)
P_fet_arr = P_cond_arr + P_sw_arr
Eff_arr = 1 - (3*P_fet_arr / (P_out_arr+P_fet_arr*3))

I_C_rms = 0.65 * I_out_max
C_in = max(I_C_rms, I_ripple_max) / (2*pi * f_sw * V_ripple)

E_drv = V_g * Q_g
P_drv = f_sw * E_drv
P_fet = P_fet_arr.max()

T_Cmax = T_Jmax - R_thJC * P_fet
R_thCA = (T_Cmax - T_a) / P_fet

T_Cmax = round(T_Cmax, 1)
R_thCA = round(R_thCA, 3)
P_sw = round(P_sw_arr.max(), 3)
P_cond = round(P_cond_arr.max(), 3)
P_fet = round(P_fet, 3)
P_drv = round(P_drv, 3)

print("Switching loss: " + str(P_sw) + "W")
print("Conduction loss: " + str(P_cond) + "W")
print("Total: " + str(P_fet) + "W")
print()
print("Gate drive loss: " + str(P_drv) + "W")
print()
print("Input cap: " + str(round(C_in * 1e6)) + "uF " + str(round(max(I_C_rms, I_ripple_max), 1)) + "A")
print()
print("Max allowed case temperature: " + str(T_Cmax) + "℃")
print("Max allowed heatsink resistance: " + str(R_thCA) + "℃/W")

fig, axs = plt.subplots(2, 2)
images = []
images.append(axs[0][0].imshow(P_sw_arr, cmap='CMRmap', interpolation='bicubic', origin = 'lower'))
images.append(axs[0][1].imshow(P_cond_arr, cmap='CMRmap', interpolation='bicubic', origin = 'lower'))
images.append(axs[1][0].imshow(P_fet_arr, cmap='CMRmap', interpolation='bicubic', origin = 'lower'))
images.append(axs[1][1].imshow(Eff_arr, cmap='jet_r', interpolation='bicubic', origin = 'lower', norm='logit', vmin=0.7))

# images.append(axs[1][1].contour(Eff_arr, cmap='jet_r', interpolation='bicubic', origin = 'lower', norm='logit', locator=ticker.LogitLocator(nbins=10)))
for image in images:
	plt.colorbar(image, format='%4.2f')
for ax2 in axs:
	for ax in ax2:
		ax.set_xlabel("motor RMS current (A)")
		ax.set_xticks(np.linspace(0, I_out_max, 6))
		ax.set_ylabel("normalized motor speed (%)")
		ax.set_yticks(np.linspace(0, 100, 6))
plt.show()