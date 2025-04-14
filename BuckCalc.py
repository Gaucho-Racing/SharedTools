def displayNum(num, n_digit = 3):
	units = ['f', 'p', 'n', 'μ', 'm', '', 'k', 'M', 'G', 'T', 'P']
	from math import log10
	idx = max(min(5, int(log10(num)//3)), -5)
	num /= 10**(idx * 3)
	if n_digit:
		return str(round(num, n_digit)) + units[idx + 5]
	return str(round(num)) + units[idx + 5]

V_in = 600
V_out = 5
I_out = 0.05
f_sw = 66e3
K_v_ripple = 0.01
K_v_in_ripple = 0.01
K_i_ccm = 0.5

V_ripple = V_out * K_v_ripple
I_ripple = I_out * K_i_ccm * 2
I_pk = I_out + I_ripple * 0.5
D = V_out / V_in
L = 1 / f_sw * (1 - D) * V_out / I_ripple
C_out = 0.5 * I_ripple / f_sw / V_ripple
C_in = D * (1 - D) / f_sw * I_out / (V_in * K_v_in_ripple)

print("L:    " + displayNum(L) + "H")
print("Ipk:  " + displayNum(I_pk) + "A")
print("Cin:  " + displayNum(C_in) + "F")
print("Cout: " + displayNum(C_out) + "F")