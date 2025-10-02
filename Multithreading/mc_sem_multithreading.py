import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, gaussian_kde
from scipy.integrate import quad

muX, sigmaX = 1000, 100
muY, sigmaY = 5000, 500
c = 7_000_000

n_samples = 1_000_000
X_samples = np.random.normal(muX, sigmaX, n_samples)
Y_samples = np.random.normal(muY, sigmaY, n_samples)
Z_samples = X_samples * Y_samples

mc_result = np.mean(Z_samples <= c)

def integrand_positive_c(x, c, muX, sigmaX, muY, sigmaY, positive_x):
    if positive_x:
        val = norm.cdf(c / x, muY, sigmaY) * norm.pdf(x, muX, sigmaX)
    else:
        val = (1 - norm.cdf(c / x, muY, sigmaY)) * norm.pdf(x, muX, sigmaX)
    return 0 if abs(x) < 1e-12 else val

def integrand_negative_c(x, c, muX, sigmaX, muY, sigmaY, positive_x):
    if positive_x:
        val = norm.cdf(c / x, muY, sigmaY) * norm.pdf(x, muX, sigmaX)
    else:
        val = (1 - norm.cdf(c / x, muY, sigmaY)) * norm.pdf(x, muX, sigmaX)
    return 0 if abs(x) < 1e-12 else val

def compute_product_cdf_1d(c, muX, sigmaX, muY, sigmaY):
    if c >= 0:
        part1, _ = quad(lambda x: integrand_positive_c(x, c, muX, sigmaX, muY, sigmaY, False), -np.inf, 0)
        part2, _ = quad(lambda x: integrand_positive_c(x, c, muX, sigmaX, muY, sigmaY, True), 0, np.inf)
        return part1 + part2
    else:
        part1, _ = quad(lambda x: integrand_negative_c(x, c, muX, sigmaX, muY, sigmaY, False), -np.inf, 0)
        part2, _ = quad(lambda x: integrand_negative_c(x, c, muX, sigmaX, muY, sigmaY, True), 0, np.inf)
        return part1 + part2

numerical_result = compute_product_cdf_1d(c, muX, sigmaX, muY, sigmaY)

theoretical_mean = muX * muY
theoretical_variance = muX**2 * sigmaY**2 + muY**2 * sigmaX**2 + sigmaX**2 * sigmaY**2
theoretical_std = np.sqrt(theoretical_variance)

empirical_mean = np.mean(Z_samples)
empirical_variance = np.var(Z_samples)
empirical_std = np.std(Z_samples)

print("## Distribution Moments Comparison\n")
print("Theoretical Moments:")
print(f"  Mean: {theoretical_mean:.4f}")
print(f"  Variance: {theoretical_variance:.4f}")
print(f"  Std Dev: {theoretical_std:.4f}\n")

print("Empirical Moments (Monte Carlo):")
print(f"  Mean: {empirical_mean:.4f} (Error: {empirical_mean - theoretical_mean:.4f}, "
      f"{abs(empirical_mean - theoretical_mean) / theoretical_mean * 100:.4f}%)")
print(f"  Variance: {empirical_variance:.4f} (Error: {empirical_variance - theoretical_variance:.4f}, "
      f"{abs(empirical_variance - theoretical_variance) / theoretical_variance * 100:.4f}%)")
print(f"  Std Dev: {empirical_std:.4f} (Error: {empirical_std - theoretical_std:.4f}, "
      f"{abs(empirical_std - theoretical_std) / theoretical_std * 100:.4f}%)\n")

print("## Probability Results")
print(f"Numerical Integration: {numerical_result:.6f}")
print(f"Monte Carlo Simulation: {mc_result:.6f}")
print(f"Absolute Difference: {abs(numerical_result - mc_result):.6f}")
print(f"Relative Difference: {abs(numerical_result - mc_result) * 100:.4f}%")


k = np.sqrt(c * 14.4)
print(f"\nk = sqrt(c * 14.4) = {k:.6f}")


z_range_factor = 4
z_center = theoretical_mean
z_half_range = z_range_factor * theoretical_std
z_min_auto = min(z_center - z_half_range, c - z_half_range / 2)
z_max_auto = max(z_center + z_half_range, c + z_half_range / 2)
z_range = np.linspace(z_min_auto, z_max_auto, 1000)

# CDF via integration (loop simples)
cdf_integration = [compute_product_cdf_1d(z, muX, sigmaX, muY, sigmaY) for z in z_range]

# CDF empírica
cdf_empirical = np.searchsorted(np.sort(Z_samples), z_range, side="right") / len(Z_samples)

# PDF approx (Gaussiana)
pdf_values = norm.pdf(z_range, theoretical_mean, theoretical_std)

# PDF empírica KDE
kde = gaussian_kde(Z_samples)
pdf_empirical_kde = kde(z_range)


plt.figure(figsize=(8,5))
plt.plot(z_range, cdf_integration, 'b-', lw=2, label="CDF (Integration)")
plt.plot(z_range, cdf_empirical, 'r--', lw=1.5, label="CDF (Monte Carlo)")
plt.axvline(c, color='k', linestyle='--', lw=2, label=f"c = {c:.2f}")
plt.axhline(numerical_result, color='g', linestyle='--', lw=1.5,
            label=f"P(Z <= c) = {numerical_result:.3f}")
plt.xlabel("z")
plt.ylabel("CDF")
plt.title("Cumulative Distribution Function of Z = X*Y")
plt.legend(loc="upper left")
plt.grid(True)
plt.xlim([z_min_auto, z_max_auto])
plt.ylim([0, 1])


plt.figure(figsize=(8,5))
plt.plot(z_range, pdf_values, 'b-', lw=2, label="Theoretical Approx.")
plt.plot(z_range, pdf_empirical_kde, 'm:', lw=1.5, label="Empirical (KDE)")
plt.axvline(c, color='r', linestyle='--', lw=2, label=f"c = {c:.2f}")
plt.axvline(theoretical_mean, color='g', linestyle='--', lw=1.5, label="Theo Mean")
plt.axvline(empirical_mean, color='c', linestyle='--', lw=1.5, label="Emp Mean")
plt.xlabel("z")
plt.ylabel("PDF")
plt.title("Probability Density Function of Z = X*Y")
plt.legend(loc="upper left")
plt.grid(True)
plt.xlim([z_min_auto, z_max_auto])

cdf_difference = np.abs(np.array(cdf_integration) - np.array(cdf_empirical))
max_diff = np.max(cdf_difference)
mean_diff = np.mean(cdf_difference)

print("\n## CDF Comparison:")
print(f"Maximum absolute difference: {max_diff:.6f}")
print(f"Mean absolute difference: {mean_diff:.6f}")
print(f"Maximum relative difference: {max_diff * 100:.4f}%")

plt.figure(figsize=(8,5))
plt.plot(z_range, cdf_difference, 'k-', lw=2)
plt.xlabel("z")
plt.ylabel("Absolute Difference")
plt.title("Difference between Integration and Monte Carlo CDFs")
plt.grid(True)

plt.show()
