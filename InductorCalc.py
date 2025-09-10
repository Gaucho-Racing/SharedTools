import math

def displayNum(num, n_digit = 3):
	units = ['f', 'p', 'n', 'μ', 'm', '', 'k', 'M', 'G', 'T', 'P']
	from math import log10
	idx = max(min(5, int(log10(num)//3)), -5)
	num /= 10**(idx * 3)
	if n_digit:
		return str(round(num, n_digit)) + units[idx + 5]
	return str(round(num)) + units[idx + 5]

mu_0 = 1.25663706212e-6

L = 12e-6
I = 1.42

############ Materials ############
# note: Bmax numbers are at 100C with additional safety margin
# note: frequency numbers are max recommended
# PC44 300k
# mu_r = 2400
# Bmax = 0.35
# PC95 800k
# mu_r = 3300
# Bmax = 0.35
# 3C96 400k
# mu_r = 2800
# Bmax = 0.3
# 3C94 300k
# mu_r = 2300
# Bmax = 0.3
# PC40 300k
mu_r = 2300
Bmax = 0.3
# PC200 3M
# mu_r = 800
# Bmax = 0.075
# 3F36 1M
# mu_r = 1600
# Bmax = 0.075
# Nanocrystaline
# mu_r = 80000
# Bmax = 1

isTransformer = True

############ Core shapes ############
# EPC17
# A_e = 22.8e-6
# l_m = 40.3e-3
# EPC13
# A_e = 12.5e-6
# l_m = 30.6e-3
# EE10
A_e = 10.9e-6
l_m = 26.3e-3
# EE19
# A_e = 23e-6
# l_m = 39.4e-3
# PQ50/50
# A_e = 328e-6
# l_m = 113e-3
# PQ40/40
# A_e = 201e-6
# l_m = 102e-3
# PQ26/25
# A_e = 122.2e-6
# l_m = 53.5e-3
# PQ20/20
# A_e = 62.6e-6
# l_m = 45.7e-3
# EL25X8.6
# A_e = 85.6e-6
# l_m = 30.0e-3
# E38/8/25
# A_e = 194e-6
# l_m = 52.4e-3
# some random toriod
# A_e = 85.5e-6
# l_m = 102e-3


if isTransformer:
	Bmax *= 0.666666666666666666667

N = I * L / (Bmax * A_e)
N_int = math.ceil(N - 0.2)
print("N:   " + displayNum(N) + " -> " + str(N_int))
N = N_int
mu_e = L * l_m / (N**2 * A_e)
l_g = (l_m * mu_r * mu_0 / mu_e - l_m) / mu_r
print("l_g: " + displayNum(l_g) + "m")