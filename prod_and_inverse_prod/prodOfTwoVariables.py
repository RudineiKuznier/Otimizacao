import numpy as np
from scipy.stats import norm, kstest 
from scipy.integrate import quad
from scipy.stats import gaussian_kde 
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
import os

class ProdOfNormalRVs:
    def __init__(self, muX, sigmaX, muY, sigmaY, c):
        self.muX = muX      
        self.sigmaX = sigmaX    
        self.muY = muY      
        self.sigmaY = sigmaY   
        self.c = c 

        self.quad_limit = 200 
        self.quad_err_tol = 1e-8 

        self.theoretical_mean = muX * muY
        self.theoretical_variance = muX**2 * sigmaY**2 + muY**2 * sigmaX**2 + sigmaX**2 * sigmaY**2
        self.theoretical_std = np.sqrt(self.theoretical_variance)
        
        self.mc_result = None
        self.numerical_result = None
        self.Z_samples = None
        self.n_samples = None
        self.empirical_mean = None
        self.empirical_variance = None
        self.empirical_std = None

    @staticmethod
    def _integrand(x, c, muX, sigmaX, muY, sigmaY, positive_x):
        if np.abs(x) < 1e-12:
            return 0.0
        
        if positive_x:
            # x > 0: P(Y <= c/x)
            prob_Y = norm.cdf(c / x, loc=muY, scale=sigmaY)
        else:
            # x < 0: P(Y*x <= c) <=> P(Y >= c/x) = 1 - P(Y <= c/x)
            prob_Y = 1 - norm.cdf(c / x, loc=muY, scale=sigmaY)
            
        return prob_Y * norm.pdf(x, loc=muX, scale=sigmaX)

    def compute_product_cdf_1d(self, c_val):
        part1, _ = quad(ProdOfNormalRVs._integrand, 
                        -np.inf, 0, 
                        args=(c_val, self.muX, self.sigmaX, self.muY, self.sigmaY, False), 
                        limit=self.quad_limit, 
                        epsrel=self.quad_err_tol)

        part2, _ = quad(ProdOfNormalRVs._integrand, 
                        0, np.inf, 
                        args=(c_val, self.muX, self.sigmaX, self.muY, self.sigmaY, True), 
                        limit=self.quad_limit, 
                        epsrel=self.quad_err_tol)
        
        return part1 + part2

    def run_analysis(self, n_samples=1000000):
        self.n_samples = n_samples

        X_samples = self.muX + self.sigmaX * np.random.randn(n_samples)
        Y_samples = self.muY + self.sigmaY * np.random.randn(n_samples)
        self.Z_samples = X_samples * Y_samples
        
        self.mc_result = np.mean(self.Z_samples <= self.c)
    
        self.numerical_result = self.compute_product_cdf_1d(self.c)

        self.empirical_mean = np.mean(self.Z_samples)
        self.empirical_variance = np.var(self.Z_samples)
        self.empirical_std = np.std(self.Z_samples)

    def print_results(self):
        """
        Exibe todos os resultados de momentos e probabilidades.
        """
        if self.Z_samples is None:
            print("ERRO: Execute run_analysis() primeiro.")
            return

        c = self.c
        k = np.sqrt(c * 14.4)

        print('Distribution Moments Comparison\n')
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

        print('Probability Results\n')
        print(f'Numerical Integration: {self.numerical_result:.6f}')
        print(f'Monte Carlo Simulation: {self.mc_result:.6f}')
        abs_diff = np.abs(self.numerical_result - self.mc_result)
        print(f'Absolute Difference: {abs_diff:.6f}')
        print(f'Relative Difference: {abs_diff / self.numerical_result * 100:.4f}%')
        
        print(f'\nk = sqrt(c * 14.4) = {k:.6f}')
        
    def plot_cdfs_and_pdfs(self, save_diretorio="./images_prodOfTwoVariables", image_format="png", dpi=300):
        """
        Gera os três gráficos: CDF, PDF e Diferença da CDF.
        """
        if self.Z_samples is None:
            print("ERRO: Execute run_analysis() primeiro.")
            return
        
        os.makedirs(save_diretorio, exist_ok=True)

        c = self.c
        
        z_range_factor = 4 
        z_center = self.theoretical_mean
        z_half_range = z_range_factor * self.theoretical_std

        z_min_auto = min(z_center - z_half_range, c - z_half_range / 2)
        z_max_auto = max(z_center + z_half_range, c + z_half_range / 2)
        z_range = np.linspace(z_min_auto, z_max_auto, 1000)

        print("\nCalculando valores da CDF para o plot (Integração)...")
        cdf_integration = np.array(
            Parallel(n_jobs=-1)(
                delayed(self.compute_product_cdf_1d)(z) for z in z_range
            )
        )

        print("Calculando valores da CDF para o plot (Monte Carlo)...")
        #cdf_empirical = np.array(
         #   Parallel(n_jobs=-1)(
          #      delayed(np.mean)(self.Z_samples <= z) for z in z_range
           # )
        #)
        cdf_empirical = np.mean(self.Z_samples[:, None] <= z_range[None, :], axis=0)

        kde = gaussian_kde(self.Z_samples)
        pdf_empirical_kde = kde.evaluate(z_range)
    
        pdf_values = norm.pdf(z_range, loc=self.theoretical_mean, scale=self.theoretical_std)

        plt.figure(figsize=(8, 6))
        plt.plot(z_range, cdf_integration, 'b-', linewidth=2, label='CDF (Integração)')
        plt.plot(z_range, cdf_empirical, 'r--', linewidth=1.5, label='CDF (Monte Carlo)')
        plt.axvline(x=c, color='k', linestyle='--', linewidth=2, label=f'c = {c:.2f}')
        plt.axhline(y=self.numerical_result, color='g', linestyle='--', linewidth=1.5, label=f'P(Z <= c) = {self.numerical_result:.3f}')
        plt.xlabel('z')
        plt.ylabel('CDF')
        plt.title('Cumulative Distribution Function of Z = X*Y')
        plt.legend(loc='upper left')
        plt.grid(True)
        plt.xlim([z_min_auto, z_max_auto])
        plt.ylim([0, 1])
        
        cdf_filename = f"cdf_plot_muX{self.muX}_sigmaX{self.sigmaX}_muY{self.muY}_sigmaY{self.sigmaY}_c{c}.{image_format}"
        cdf_filepath = os.path.join(save_diretorio, cdf_filename)
        plt.savefig(cdf_filepath, dpi=dpi, bbox_inches='tight')
        plt.close() 
        
    
        plt.figure(figsize=(8, 6))
        plt.plot(z_range, pdf_values, 'b-', linewidth=2, label='Aprox. Normal Teórica')
        plt.plot(z_range, pdf_empirical_kde, 'm:', linewidth=1.5, label='Empírica (KDE)')
        plt.axvline(x=c, color='r', linestyle='--', linewidth=2, label=f'c = {c:.2f}')
        plt.axvline(x=self.theoretical_mean, color='g', linestyle='--', linewidth=1.5, label='Média Teórica')
        plt.axvline(x=self.empirical_mean, color='c', linestyle='--', linewidth=1.5, label='Média Empírica')
        plt.xlabel('z')
        plt.ylabel('PDF')
        plt.title('Probability Density Function of Z = X*Y')
        plt.legend(loc='upper left')
        plt.grid(True)
        plt.xlim([z_min_auto, z_max_auto])
        
        pdf_filename = f"pdf_plot_muX{self.muX}_sigmaX{self.sigmaX}_muY{self.muY}_sigmaY{self.sigmaY}_c{c}.{image_format}"
        pdf_filepath = os.path.join(save_diretorio, pdf_filename)
        plt.savefig(pdf_filepath, dpi=dpi, bbox_inches='tight')
        plt.close()

        cdf_difference = np.abs(cdf_integration - cdf_empirical)
        max_diff = np.max(cdf_difference)
        mean_diff = np.mean(cdf_difference)

        print('\n## CDF Comparison:')
        print(f'Maximum absolute difference: {max_diff:.6f}')
        print(f'Mean absolute difference: {mean_diff:.6f}')
        print(f'Maximum relative difference: {max_diff / self.numerical_result * 100:.4f}%') # Usando o valor de c como referência
        
        plt.figure(figsize=(8, 6))
        plt.plot(z_range, cdf_difference, 'k-', linewidth=2)
        plt.xlabel('z')
        plt.ylabel('Absolute Difference')
        plt.title('Difference between Integration and Monte Carlo CDFs')
        plt.grid(True)
        
        diff_filename = f"cdf_diff_plot_muX{self.muX}_sigmaX{self.sigmaX}_muY{self.muY}_sigmaY{self.sigmaY}_c{c}.{image_format}"
        diff_filepath = os.path.join(save_diretorio, diff_filename)
        plt.savefig(diff_filepath, dpi=dpi, bbox_inches='tight')
        plt.close()


