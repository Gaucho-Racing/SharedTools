def displayNum(num):
	units = ['f', 'p', 'n', 'μ', 'm', '', 'k', 'M', 'G', 'T', 'P']
	from math import log10
	idx = max(min(5, int(log10(num)//3)), -5)
	num /= 10**(idx * 3)
	return str(round(num, 3)) + units[idx + 5]

VinMin = 120
Vout = 24
Vf = 0.6
D = 0.4
efcy = 0.85
Fsw = 600e3
Pout = 60
Bm = 0.2
Ae = 12.5e-6

Lp = efcy * D**2 * VinMin**2 / (2 * Fsw * Pout)
Ipk = 2*Pout / (efcy * VinMin * D)
N = VinMin / (Vout + Vf) * D / (1-D)
Np = Lp * Ipk / (Bm * Ae)
Ns = Np / N
if Np > Ns:
	Ns2 = max(round(Ns), 1)
	Np2 = round(Ns2 * N)
else:
	Np2 = max(round(Np), 1)
	Ns2 = round(Np2 / N)

VinRip = VinMin * 0.01
VoutRip = Vout * 0.01
N2 = Np2 / Ns2
Cin = Ipk/2 * (1/Fsw) * D / VinRip
Cout = Ipk*N2/2 * (1/Fsw) * (1-D) / VoutRip

print("N:     " + str(round(N, 3)))
print("Lp:    " + displayNum(Lp) + "H")
print("Ipk:   " + str(round(Ipk, 3)) + "A")
print("Np:    " + str(round(Np, 3)) + " -> " + str(Np2))
print("Ns:    " + str(round(Ns, 3)) + " -> " + str(Ns2))
print("Cin:   " + displayNum(Cin) + "F")
print("Cout:  " + displayNum(Cout) + "F")