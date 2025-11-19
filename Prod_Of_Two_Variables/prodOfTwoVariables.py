import numpy as np
from typing import Tuple
from scipy.stats import norm, kstest
from scipy.integrate import quad
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt

class ProdOfNormalRVs:
    
    def __init__(
        self,
        muX: float,
        sigmaX: float,
        muY: float,
        sigmaY: float,
        c = None
    ):
        
        self.muX: float = muX
        self.sigmaX: float = sigmaX
        self.muY: float = muY
        self.sigmaY: float = sigmaY
        self.percent_mc = 0.01
        
        if c is None:
            self.c: float = muX * muY
        else:
            self.c: float = c
            
        self.quad_limit: int = 500
        self.quad_err_tol: float = 1e-10
        
        self.theoretical_mean: float = muX * muY
        self.theoretical_variance: float = muX**2 * sigmaY**2 + muY**2 * sigmaX**2 + sigmaX**2 * sigmaY**2
        self.theoretical_std: float = np.sqrt(self.theoretical_variance)
        
        self.mc_result = None
        self.numerical_result = None
        self.Z_samples = None
        self.n_samples = None
        self.empirical_mean = None
        self.empirical_variance = None
        self.empirical_std = None

    @staticmethod
    def _integrand(x:float, c:float, muX:float, sigmaX:float, muY:float, sigmaY:float, positive_x:bool) -> float:
        if np.abs(x) < 1e-12:
            return 0.0
        if np.abs(x) > 1e6:
            return 0.0
            
        if positive_x:
            prob_Y = norm.cdf(c / x, loc=muY, scale=sigmaY)
        else:
            prob_Y = 1 - norm.cdf(c / x, loc=muY, scale=sigmaY)
            
        return prob_Y * norm.pdf(x, loc=muX, scale=sigmaX)

    def compute_product_cdf_1d(self, c_val: float) -> float:
        x_lower = self.muX - 10 * self.sigmaX
        x_upper = self.muX + 10 * self.sigmaX
        x_lower = max(x_lower, -1e6)
        x_upper = min(x_upper, 1e6)
        
        try:
            part1, _ = quad(ProdOfNormalRVs._integrand, x_lower, 0,
                          args=(c_val, self.muX, self.sigmaX, self.muY, self.sigmaY, False),
                          limit=self.quad_limit,
                          epsabs=1e-12,
                          epsrel=1e-10)
            
            part2, _ = quad(ProdOfNormalRVs._integrand, 0, x_upper,
                          args=(c_val, self.muX, self.sigmaX, self.muY, self.sigmaY, True),
                          limit=self.quad_limit,
                          epsabs=1e-12,
                          epsrel=1e-10)
            
            return part1 + part2
            
        except Exception as e:
            print(f'Integration failed: {str(e)}')
            print('Using fallback method (normal approximation)...')
            return norm.cdf(c_val, loc=self.theoretical_mean, scale=self.theoretical_std)

    def solve_cdf(self, n_samples=1000000) -> float:
        self.n_samples = n_samples
        
        X_samples = self.muX + self.sigmaX * np.random.randn(n_samples)
        Y_samples = self.muY + self.sigmaY * np.random.randn(n_samples)
        self.Z_samples = X_samples * Y_samples
        
        self.mc_result = np.mean(self.Z_samples <= self.c)
        self.numerical_result = self.compute_product_cdf_1d(self.c)
        
        self.empirical_mean = np.mean(self.Z_samples)
        self.empirical_variance = np.var(self.Z_samples)
        self.empirical_std = np.std(self.Z_samples)
        
        # Verificação de diferença
        abs_diff = np.abs(self.numerical_result - self.mc_result)
        rel_diff_percent = (abs_diff / self.numerical_result) * 100 if self.numerical_result != 0 else 0
        
        if rel_diff_percent > self.percent_mc:
            print("\n" + "="*100)
            print(f"Diferença acima de {self.percent_mc}% | Diferença Absoluta:{abs_diff:.8f} | Diferença Percentual: {rel_diff_percent:.4f}%")
            print("="*100)
        
        return self.theoretical_std

    def _print_verification_results(self) -> None:
        if self.Z_samples is None:
            print("ERRO: Execute solve_cdf() primeiro.")
            return
            
        c = self.c
        k = np.sqrt(c * 14.4)
        
        print('## Distribution Moments Comparison\n')
        print('Theoretical Moments:')
        print(f'  Mean: {self.theoretical_mean:.4f}')
        print(f'  Variance: {self.theoretical_variance:.4f}')
        print(f'  Std Dev: {self.theoretical_std:.4f}\n')
        
        print('Empirical Moments (Monte Carlo):')
        mean_err = self.empirical_mean - self.theoretical_mean
        mean_err_perc = np.abs(mean_err) / self.theoretical_mean * 100
        print(f'  Mean: {self.empirical_mean:.4f} (Error: {mean_err:.4f}, {mean_err_perc:.4f}%)')
        
        var_err = self.empirical_variance - self.theoretical_variance
        var_err_perc = np.abs(var_err) / self.theoretical_variance * 100
        print(f'  Variance: {self.empirical_variance:.4f} (Error: {var_err:.4f}, {var_err_perc:.4f}%)')
        
        std_err = self.empirical_std - self.theoretical_std
        std_err_perc = np.abs(std_err) / self.theoretical_std * 100
        print(f'  Std Dev: {self.empirical_std:.4f} (Error: {std_err:.4f}, {std_err_perc:.4f}%)\n')
        
        print('## Probability Results')
        print(f'Numerical Integration: {self.numerical_result:.6f}')
        print(f'Monte Carlo Simulation: {self.mc_result:.6f}')
        abs_diff = np.abs(self.numerical_result - self.mc_result)
        print(f'Absolute Difference (Int vs MC): {abs_diff:.6f}')
        print(f'Relative Difference (Int vs MC): {abs_diff * 100:.4f}%')
        print(f'\nk = sqrt(c * 14.4) = {k:.6f}')

    def plot_cdfs(self) -> None:
        if self.Z_samples is None:
            print("ERRO: Execute solve_cdf() primeiro.")
            return
            
        c = self.c
        z_range_factor = 4
        z_center = self.theoretical_mean
        z_half_range = z_range_factor * self.theoretical_std
        z_min_auto = min(z_center - z_half_range, c - z_half_range / 2)
        z_max_auto = max(z_center + z_half_range, c + z_half_range / 2)
        z_range = np.linspace(z_min_auto, z_max_auto, 1000)
        
        print("\nCalculando valores da CDF para o plot (Integração)...")
        cdf_integration = np.array([
            self.compute_product_cdf_1d(z) for z in z_range
        ])
        
        print("Calculando valores da CDF para o plot (Monte Carlo)...")
        cdf_empirical = np.array([
            np.mean(self.Z_samples <= z) for z in z_range
        ])
        
        kde = gaussian_kde(self.Z_samples)
        pdf_empirical_kde = kde.evaluate(z_range)
        pdf_values = norm.pdf(z_range, loc=self.theoretical_mean, scale=self.theoretical_std)
        
        # Figura 1: CDF
        plt.figure(figsize=(8, 6))
        plt.plot(z_range, cdf_integration, 'b-', linewidth=2, label='CDF (Integração)')
        plt.plot(z_range, cdf_empirical, 'r--', linewidth=1.5, label='CDF (Monte Carlo)')
        plt.axvline(x=c, color='k', linestyle='--', linewidth=2, label=f'c = {c:.2f}')
        plt.axhline(y=self.numerical_result, color='m', linestyle='--', linewidth=1.5,
                   label=f'P(Z <= c) = {self.numerical_result:.3f}')
        plt.xlabel('z')
        plt.ylabel('CDF')
        plt.title('Cumulative Distribution Function of Z = X*Y')
        plt.legend(loc='upper left')
        plt.grid(True)
        plt.xlim([z_min_auto, z_max_auto])
        plt.ylim([0, 1])
        plt.show()
        
        # Figura 2: PDF
        plt.figure(figsize=(8, 6))
        plt.plot(z_range, pdf_values, 'b-', linewidth=2, label='Aprox. Normal Teórica')
        plt.plot(z_range, pdf_empirical_kde, 'm:', linewidth=1.5, label='Empírica (KDE)')
        plt.axvline(x=c, color='r', linestyle='--', linewidth=2, label=f'c = {c:.2f}')
        plt.axvline(x=self.theoretical_mean, color='g', linestyle='--', linewidth=1.5,
                   label='Média Teórica')
        plt.axvline(x=self.empirical_mean, color='c', linestyle='--', linewidth=1.5,
                   label='Média Empírica')
        plt.xlabel('z')
        plt.ylabel('PDF')
        plt.title('Probability Density Function of Z = X*Y')
        plt.legend(loc='upper left')
        plt.grid(True)
        plt.xlim([z_min_auto, z_max_auto])
        plt.show()
        
        # Figura 3: Diferença entre CDFs
        cdf_difference = np.abs(cdf_integration - cdf_empirical)
        max_diff = np.max(cdf_difference)
        mean_diff = np.mean(cdf_difference)
        
        print('\n## CDF Comparison:')
        print(f'Maximum absolute difference: {max_diff:.6f}')
        print(f'Mean absolute difference: {mean_diff:.6f}')
        print(f'Maximum relative difference: {max_diff * 100:.4f}%')
        
        plt.figure(figsize=(8, 6))
        plt.plot(z_range, cdf_difference, 'k-', linewidth=2)
        plt.xlabel('z')
        plt.ylabel('Absolute Difference')
        plt.title('Difference between Integration and Monte Carlo CDFs')
        plt.grid(True)
        plt.show()