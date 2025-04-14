def displayNum(num, n_digit = 3):
	units = ['f', 'p', 'n', 'μ', 'm', '', 'k', 'M', 'G', 'T', 'P']
	from math import log10
	idx = max(min(5, int(log10(num)//3)), -5)
	num /= 10**(idx * 3)
	if n_digit:
		return str(round(num, n_digit)) + units[idx + 5]
	return str(round(num)) + units[idx + 5]

V_in = 12
V_out = 24
I_out = 0.05
f_sw = 300e3
K_v_ripple = 0.01
K_v_in_ripple = 0.01
K_i_ccm = 1
current_mode = True
R_esr = 3e-3
R_fbt = 10e3
# f_p0 = 30 # for UCx84x, estimated from TI datasheet graph
f_p0 = 88.91 # for MCP1632, estimated from open loop gain and GBWP

V_ripple = V_out * K_v_ripple
D = 1 - V_in / V_out
I_ripple = I_out * K_i_ccm * 2 / (1 - D)
I_pk = I_out / (1 - D) + I_ripple * 0.5
L = 1 / f_sw * D * V_in / I_ripple
C_out = I_out * D / V_ripple / f_sw
C_in = I_ripple * 0.5 / (V_in * K_v_in_ripple) / f_sw

print("D:    " + str(D))
print("L:    " + displayNum(L) + "H")
print("Ipk:  " + displayNum(I_pk) + "A")
print("Cin:  " + displayNum(C_in) + "F")
print("Cout: " + displayNum(C_out) + "F")

print()
f_rhp = (V_out / I_out) * (1 - D)**2 / 6.2832 / L
if current_mode:
	f_esr = 1 / (6.2832 * R_esr * C_out)
	f_cross = min(f_sw / 10, f_rhp / 5)
	f_z1 = f_cross / 5
	f_p1 = min(f_esr, f_rhp) * 2
	# print(f_esr, f_rhp, f_p0, f_z1, f_p1)
	print("Ccomp1: " + displayNum(f_z1 / (6.2832 * R_fbt * f_p0 * f_p1)) + "F")
	print("Ccomp2: " + displayNum(1 / (6.2832 * R_fbt * f_p0)) + "F")
	print("Rcomp2: " + displayNum(f_p0 * R_fbt / f_z1) + "Ω")
else:
	# TODO
	print("f_bw: " + displayNum(min(f_rhp / 5, f_sw / 10), 1) + "Hz")

# Feedback network:
#       |\
#       |+\
#       |  >-------|
#   |---|-/        |
#   |   |/         |
#   -------||-------
#   |    Ccomp1    |
#   ---||-----/\/\--
#    Ccomp2  Rcomp2