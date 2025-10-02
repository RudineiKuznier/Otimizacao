import numpy as np
from scipy.stats import norm
from scipy.integrate import quad
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
import time
# Parâmetros
muX = 20      
sigmaX = 30    
muY = 300      
sigmaY = 150   
target_p = 0.95 

# %% Teórico
theoretical_mean = muX * muY
theoretical_variance = muX**2 * sigmaY**2 + muY**2 * sigmaX**2 + sigmaX**2 * sigmaY**2
theoretical_std = np.sqrt(theoretical_variance)

# %% Funções auxiliares e de CDF (mantidas)
def integrand_positive_c(x, c, muX, sigmaX, muY, sigmaY, positive_x):
    if np.abs(x) < 1e-12:
        return 0.0
    if positive_x:
        return norm.cdf(c / x, loc=muY, scale=sigmaY) * norm.pdf(x, loc=muX, scale=sigmaX)
    else:
        return (1 - norm.cdf(c / x, loc=muY, scale=sigmaY)) * norm.pdf(x, loc=muX, scale=sigmaX)

def integrand_negative_c(x, c, muX, sigmaX, muY, sigmaY, positive_x):
    if np.abs(x) < 1e-12:
        return 0.0
    if positive_x:
        return norm.cdf(c / x, loc=muY, scale=sigmaY) * norm.pdf(x, loc=muX, scale=sigmaX)
    else:
        return (1 - norm.cdf(c / x, loc=muY, scale=sigmaY)) * norm.pdf(x, loc=muX, scale=sigmaX)

def compute_product_cdf_1d(c, muX, sigmaX, muY, sigmaY):
    if c >= 0:
        part1, _ = quad(integrand_positive_c, -np.inf, 0, args=(c, muX, sigmaX, muY, sigmaY, False), limit=200)
        part2, _ = quad(integrand_positive_c, 0, np.inf, args=(c, muX, sigmaX, muY, sigmaY, True), limit=200)
        return part1 + part2
    else:
        part1, _ = quad(integrand_negative_c, -np.inf, 0, args=(c, muX, sigmaX, muY, sigmaY, False), limit=200)
        part2, _ = quad(integrand_negative_c, 0, np.inf, args=(c, muX, sigmaX, muY, sigmaY, True), limit=200)
        return part1 + part2

# %% Inverte a CDF (mantida)
initial_guess = norm.ppf(target_p, loc=theoretical_mean, scale=theoretical_std)
func = lambda c: compute_product_cdf_1d(c, muX, sigmaX, muY, sigmaY) - target_p
c_solution, info, ier, msg = fsolve(func, initial_guess, full_output=True, xtol=1e-6)
c_solution = c_solution[0]

# %% Verificação Monte Carlo (mantida)
n_samples = 1000000
X_samples = muX + sigmaX * np.random.randn(n_samples)
Y_samples = muY + sigmaY * np.random.randn(n_samples)
Z_samples = X_samples * Y_samples
mc_p = np.mean(Z_samples <= c_solution)

# %% Exibe resultados (mantida)
print("## Inverse CDF Calculation Results")
print(f"Target probability: {target_p:.6f}")
print(f"Calculated c value: {c_solution:.6f}")
print(f"Monte Carlo verification: P(Z <= {c_solution:.6f}) = {mc_p:.6f}")
print(f"Absolute error: {np.abs(target_p - mc_p):.6f}")
print(f"Relative error: {np.abs(target_p - mc_p)/target_p * 100:.4f}%")

# %% Plotar o CDF com paralelização 🚀
z_range_factor = 4
z_min = theoretical_mean - z_range_factor * theoretical_std
z_max = theoretical_mean + z_range_factor * theoretical_std
z_range = np.linspace(z_min, z_max, 1000)

print("Calculando CDF paralelizado...")
start_time_par = time.perf_counter()
# Paraleliza o cálculo dos valores do CDF usando joblib
# O `n_jobs=-1` usa todos os núcleos disponíveis
cdf_values = Parallel(n_jobs=-1)(delayed(compute_product_cdf_1d)(z, muX, sigmaX, muY, sigmaY) for z in z_range)
end_time_par = time.perf_counter()
elapsed_time_par = end_time_par - start_time_par
print(f"Tempo de execução (Paralelo): {elapsed_time_par:.4f} segundos")
# Plota o gráfico (mantido)
plt.figure(figsize=(8, 6))
plt.plot(z_range, cdf_values, 'b-', linewidth=2, label='CDF')
plt.axvline(x=c_solution, color='r', linestyle='--', linewidth=2, label=f'c = {c_solution:.2f}')
plt.axhline(y=target_p, color='g', linestyle='--', linewidth=2, label=f'P = {target_p:.3f}')
plt.plot(c_solution, target_p, 'ro', markersize=8, markerfacecolor='r')
plt.xlabel('z')
plt.ylabel('CDF')
plt.title(f'CDF of Z = X*Y and Solution for P(Z ≤ c) = {target_p:.3f}')
plt.legend(loc='upper left')
plt.grid(True)
plt.show()