import numpy as np
from scipy.stats import norm, gaussian_kde
from scipy.integrate import quad
import matplotlib.pyplot as plt
import warnings

class ProdOfNormalRVs:
    
    def __init__(self, muX: float, sigmaX: float, muY: float, sigmaY: float, c: float = None):
        self.muX = muX      
        self.sigmaX = sigmaX    
        self.muY = muY      
        self.sigmaY = sigmaY   

        if c is None:
            self.c = muX * muY
        else:
            self.c = c 

        self.theoretical_mean = muX * muY
        self.theoretical_variance = (muX**2 * sigmaY**2) + (muY**2 * sigmaX**2) + (sigmaX**2 * sigmaY**2)
        self.theoretical_std = np.sqrt(self.theoretical_variance)
        
        self.mc_result = None
        self.numerical_result = None
        self.Z_samples = None
        self.empirical_mean = None
        self.empirical_variance = None
        self.empirical_std = None

    def _integrand(self, x: float, c_val: float) -> float:
        """Calcula o integrando com tratamento robusto de casos extremos"""
        epsilon = 1e-10
        if np.abs(x) < epsilon:
            return 0.0
        
        pdf_x = norm.pdf(x, loc=self.muX, scale=self.sigmaX)
        if pdf_x < 1e-300:
            return 0.0

        try:
            y_threshold = c_val / x
            y_max = self.muY + 10 * self.sigmaY
            y_min = self.muY - 10 * self.sigmaY
            y_threshold = np.clip(y_threshold, y_min, y_max)
        except (OverflowError, RuntimeWarning):
            if x > 0:
                return pdf_x if c_val > 0 else 0.0
            else:
                return 0.0 if c_val > 0 else pdf_x

        if x > 0:
            prob_y = norm.cdf(y_threshold, loc=self.muY, scale=self.sigmaY)
        else:
            prob_y = 1 - norm.cdf(y_threshold, loc=self.muY, scale=self.sigmaY)

        return prob_y * pdf_x

    def compute_product_cdf_1d(self, c_val: float) -> float:
        """Calcula P(XY <= c) usando integração numérica robusta"""
        n_sigmas = 8
        x_min = self.muX - n_sigmas * self.sigmaX
        x_max = self.muX + n_sigmas * self.sigmaX
        
        if x_max - x_min < 1e-6:
            x_min = self.muX - 1.0
            x_max = self.muX + 1.0

        res = 0.0
        epsilon = 1e-10
        quad_opts = {'limit': 100, 'epsabs': 1e-6, 'epsrel': 1e-4}
        
        neg_lower = x_min
        neg_upper = min(x_max, -epsilon)
        
        if neg_lower < neg_upper:
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore', category=Warning)
                    part1, err1 = quad(self._integrand, neg_lower, neg_upper, args=(c_val,), **quad_opts)
                    res += part1
            except Exception as e:
                print(f"Aviso: Erro na integração negativa: {e}")

        pos_lower = max(x_min, epsilon)
        pos_upper = x_max
        
        if pos_lower < pos_upper:
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore', category=Warning)
                    part2, err2 = quad(self._integrand, pos_lower, pos_upper, args=(c_val,), **quad_opts)
                    res += part2
            except Exception as e:
                print(f"Aviso: Erro na integração positiva: {e}")

        res = np.clip(res, 0.0, 1.0)
        self.numerical_result = res
        return round(self.numerical_result, 6)

    def solve_cdf(self, n_samples=1_000_000) -> float:
        """Realiza simulação Monte Carlo"""
        X_samples = np.random.normal(self.muX, self.sigmaX, n_samples)
        Y_samples = np.random.normal(self.muY, self.sigmaY, n_samples)
        self.Z_samples = X_samples * Y_samples
        
        self.mc_result = np.mean(self.Z_samples <= self.c)
        self.empirical_mean = np.mean(self.Z_samples)
        self.empirical_variance = np.var(self.Z_samples)
        self.empirical_std = np.std(self.Z_samples)

        if self.numerical_result is None:
            self.compute_product_cdf_1d(self.c)
            
        return round(self.theoretical_std, 6)

    def get_relative_error(self) -> float:
        """Calcula erro relativo entre métodos"""
        if self.numerical_result is None or self.mc_result is None:
            return 0.0
        if self.numerical_result == 0:
            return 0.0 if self.mc_result == 0 else 100.0
        abs_diff = abs(self.numerical_result - self.mc_result)
        resultado = (abs_diff / abs(self.numerical_result)) * 100
        return round(resultado, 3)
            
    def print_verification_results(self):
        """Imprime resultados de verificação"""
        if self.Z_samples is None:
            print("Resultados de Monte Carlo não disponíveis. Execute solve_cdf() primeiro.")
            return

        k = np.sqrt(self.c * 14.4)
        print('\n' + '='*50)
        print('## COMPARAÇÃO DOS MOMENTOS DA DISTRIBUIÇÃO')
        print('='*50)
        print('Momentos Teóricos:')
        print(f'  Média:      {self.theoretical_mean:.4f}')
        print(f'  Variância:  {self.theoretical_variance:.4f}')
        print(f'  Desv. Pad.: {self.theoretical_std:.4f}\n')

        print('Momentos Empíricos (Monte Carlo):')
        denom_mean = self.theoretical_mean if abs(self.theoretical_mean) > 1e-9 else 1e-9
        denom_var = self.theoretical_variance if abs(self.theoretical_variance) > 1e-9 else 1e-9
        denom_std = self.theoretical_std if abs(self.theoretical_std) > 1e-9 else 1e-9
        
        mean_err = self.empirical_mean - self.theoretical_mean
        mean_err_perc = np.abs(mean_err) / np.abs(denom_mean) * 100
        print(f'  Média:      {self.empirical_mean:.4f} (Erro: {mean_err:.4f}, {mean_err_perc:.4f}%)')
        
        var_err = self.empirical_variance - self.theoretical_variance
        var_err_perc = np.abs(var_err) / np.abs(denom_var) * 100
        print(f'  Variância:  {self.empirical_variance:.4f} (Erro: {var_err:.4f}, {var_err_perc:.4f}%)')
        
        std_err = self.empirical_std - self.theoretical_std
        std_err_perc = np.abs(std_err) / np.abs(denom_std) * 100
        print(f'  Desv. Pad.: {self.empirical_std:.4f} (Erro: {std_err:.4f}, {std_err_perc:.4f}%)\n')

        print('## RESULTADOS DE PROBABILIDADE P(XY <= c)')
        print(f' Integração Numérica (c={self.c:.2f}): {self.numerical_result:.6f}')
        print(f' Simulação Monte Carlo (c={self.c:.2f}): {self.mc_result:.6f}')
        
        abs_diff = np.abs(self.numerical_result - self.mc_result)
        print(f' Diferença Absoluta: {abs_diff:.6f}')
        
        denom_num = self.numerical_result if abs(self.numerical_result) > 1e-9 else 1e-9
        rel_diff = (abs_diff / np.abs(denom_num) * 100)
        print(f' Diferença Relativa: {rel_diff:.4f}%')
        print(f'\nk = sqrt(c * 14.4) = {k:.6f}')

    def plot_cdfs(self):
        """Plota CDFs e PDFs"""
        if self.Z_samples is None:
            print("ERRO: Execute solve_cdf() primeiro.")
            return

        z_range_factor = 4
        z_center = self.theoretical_mean
        z_half_range = z_range_factor * self.theoretical_std

        z_min_auto = min(z_center - z_half_range, self.c - z_half_range / 2)
        z_max_auto = max(z_center + z_half_range, self.c + z_half_range / 2)
        z_range = np.linspace(z_min_auto, z_max_auto, 200)

        print("\nCalculando integral para curva CDF...")
        cdf_integration = [self.compute_product_cdf_1d(z) for z in z_range]
        cdf_integration = np.array(cdf_integration)

        sorted_samples = np.sort(self.Z_samples)
        cdf_empirical = np.searchsorted(sorted_samples, z_range, side='right') / len(sorted_samples)
        
        kde = gaussian_kde(self.Z_samples)
        pdf_empirical_kde = kde.evaluate(z_range)
        pdf_values_normal = norm.pdf(z_range, loc=self.theoretical_mean, scale=self.theoretical_std)

        plt.figure(figsize=(10, 6))
        plt.plot(z_range, cdf_integration, 'b-', linewidth=2, label='CDF (Integração)')
        plt.plot(z_range, cdf_empirical, 'r--', linewidth=1.5, label='CDF (Monte Carlo)')
        plt.axvline(x=self.c, color='k', linestyle='--', linewidth=2, label=f'c = {self.c:.2f}')
        plt.axhline(y=self.numerical_result, color='g', linestyle=':', linewidth=2, label=f'P = {self.numerical_result:.3f}')
        plt.xlabel('z')
        plt.ylabel('Probabilidade Acumulada')
        plt.title('CDF de Z = X*Y')
        plt.legend(loc='best')
        plt.grid(True, alpha=0.3)
        plt.xlim([z_min_auto, z_max_auto])
        plt.ylim([-0.05, 1.05])
        plt.tight_layout()
        plt.show()

        plt.figure(figsize=(10, 6))
        plt.plot(z_range, pdf_values_normal, 'b-', linewidth=2, label='Aprox. Normal Teórica')
        plt.plot(z_range, pdf_empirical_kde, 'm:', linewidth=2, label='Empírica (KDE)')
        plt.axvline(x=self.c, color='r', linestyle='--', linewidth=2, label=f'c = {self.c:.2f}')
        plt.axvline(x=self.theoretical_mean, color='g', linestyle='--', linewidth=1.5, label='Média Teórica')
        plt.xlabel('z')
        plt.ylabel('Densidade de Probabilidade')
        plt.title('PDF de Z = X*Y')
        plt.legend(loc='best')
        plt.grid(True, alpha=0.3)
        plt.xlim([z_min_auto, z_max_auto])
        plt.tight_layout()
        plt.show()

        cdf_difference = np.abs(cdf_integration - cdf_empirical)
        plt.figure(figsize=(10, 6))
        plt.plot(z_range, cdf_difference, 'k-', linewidth=2)
        plt.xlabel('z')
        plt.ylabel('Diferença Absoluta')
        plt.title('Erro Absoluto (Integração vs Monte Carlo)')
        plt.grid(True, alpha=0.3)
        plt.xlim([z_min_auto, z_max_auto])
        plt.tight_layout()
        plt.show()

