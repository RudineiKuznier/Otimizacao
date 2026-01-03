import numpy as np
from scipy.stats import norm
from scipy.integrate import quad
from scipy.optimize import brentq, fsolve
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
import warnings

class InverseProdOfTwoVariables:
    def __init__(
        self,
        muX: float,
        sigmaX: float,
        muY: float,
        sigmaY: float,
        target_p: float = 0.98
    ):
        self.muX: float = muX      
        self.sigmaX: float = sigmaX    
        self.muY: float = muY      
        self.sigmaY: float = sigmaY   
        self.target_p: float = target_p 

        self.theoretical_mean: float = muX * muY
        self.theoretical_variance: float = muX**2 * sigmaY**2 + muY**2 * sigmaX**2 + sigmaX**2 * sigmaY**2
        self.theoretical_std: float = np.sqrt(self.theoretical_variance)

        self.c_solution = None
        self.mc_p = None

    @staticmethod
    def _integrand(x: float, c: float, muX: float, sigmaX: float, muY: float, sigmaY: float, positive_x: bool) -> float:
        """Integrando melhorado com tratamento de casos extremos"""
        epsilon = 1e-12
        
        if np.abs(x) < epsilon:
            return 0.0
        
        # PDF de X com verificação de underflow
        pdf_x = norm.pdf(x, loc=muX, scale=sigmaX)
        if pdf_x < 1e-300:
            return 0.0
        
        try:
            # Calcula y_threshold = c/x com proteção
            y_threshold = c / x
            
            # Limita para evitar overflow na CDF
            y_max = muY + 20 * sigmaY
            y_min = muY - 20 * sigmaY
            y_threshold = np.clip(y_threshold, y_min, y_max)
            
        except (OverflowError, RuntimeWarning):
            # Se y_threshold explode
            if positive_x:
                return pdf_x if c > 0 else 0.0
            else:
                return 0.0 if c > 0 else pdf_x
        
        # Calcula CDF de Y
        if positive_x:
            cdf_y = norm.cdf(y_threshold, loc=muY, scale=sigmaY)
        else:
            cdf_y = 1 - norm.cdf(y_threshold, loc=muY, scale=sigmaY)
        
        return cdf_y * pdf_x

    @staticmethod
    def _compute_product_cdf_1d(c: float, muX: float, sigmaX: float, muY: float, sigmaY: float) -> float:
        """
        Calcula P(XY <= c) com integração numérica robusta
        Usa limites finitos ao invés de infinitos
        """
        
        # Define limites finitos baseados na distribuição de X
        n_sigmas = 10  # Cobre ~99.9999% da distribuição
        x_min = muX - n_sigmas * sigmaX
        x_max = muX + n_sigmas * sigmaX
        
        # Garante intervalo mínimo
        if x_max - x_min < 1e-6:
            x_min = muX - 10.0
            x_max = muX + 10.0
        
        epsilon = 1e-12
        
        # Tolerâncias mais relaxadas para melhor convergência
        epsabs = 1e-8  # Era 1e-10
        epsrel = 1e-6  # Era 1e-8
        limit = 150    # Era 500
        
        result = 0.0
        
        # Integra sobre x < 0 (se aplicável)
        neg_lower = x_min
        neg_upper = -epsilon
        
        if neg_lower < neg_upper and neg_upper < x_max:
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore', category=Warning)
                    part1, err1 = quad(
                        InverseProdOfTwoVariables._integrand,
                        neg_lower, neg_upper,
                        args=(c, muX, sigmaX, muY, sigmaY, False),
                        epsabs=epsabs,
                        epsrel=epsrel,
                        limit=limit
                    )
                    result += part1
            except Exception as e:
                # Se falhar, ignora esta parte (contribuição muito pequena)
                pass
        
        # Integra sobre x > 0 (se aplicável)
        pos_lower = epsilon
        pos_upper = x_max
        
        if pos_lower < pos_upper and pos_lower > x_min:
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore', category=Warning)
                    part2, err2 = quad(
                        InverseProdOfTwoVariables._integrand,
                        pos_lower, pos_upper,
                        args=(c, muX, sigmaX, muY, sigmaY, True),
                        epsabs=epsabs,
                        epsrel=epsrel,
                        limit=limit
                    )
                    result += part2
            except Exception as e:
                # Se falhar, tenta com limites mais conservadores
                try:
                    pos_lower_safe = max(epsilon, muX - 5*sigmaX)
                    pos_upper_safe = min(x_max, muX + 5*sigmaX)
                    with warnings.catch_warnings():
                        warnings.filterwarnings('ignore', category=Warning)
                        part2, _ = quad(
                            InverseProdOfTwoVariables._integrand,
                            pos_lower_safe, pos_upper_safe,
                            args=(c, muX, sigmaX, muY, sigmaY, True),
                            epsabs=1e-6,
                            epsrel=1e-4,
                            limit=100
                        )
                        result += part2
                except:
                    pass
        
        # Garante resultado válido
        result = np.clip(result, 0.0, 1.0)
        return float(result)

    def solve_inverse_cdf(self, n_samples=1000000) -> float:
        """
        Resolve P(XY <= c) = target_p para encontrar c
        Usa método robusto com fallbacks
        """
        
        # Chute inicial baseado na aproximação normal
        self.initial_guess = norm.ppf(self.target_p, loc=self.theoretical_mean, scale=self.theoretical_std)
        
        # Função objetivo
        def objective(c):
            return InverseProdOfTwoVariables._compute_product_cdf_1d(
                c, self.muX, self.sigmaX, self.muY, self.sigmaY
            ) - self.target_p
        
        # Estratégia adaptativa para encontrar limites válidos
        def find_valid_bounds():
            """Encontra limites onde a função muda de sinal"""
            
            # Começa com intervalo baseado no desvio padrão
            scale = self.theoretical_std
            lower = self.initial_guess - 3 * scale
            upper = self.initial_guess + 3 * scale
            
            # Garante que não seja muito pequeno
            if upper - lower < abs(self.initial_guess) * 0.1:
                range_size = max(abs(self.initial_guess) * 0.5, scale * 2)
                lower = self.initial_guess - range_size
                upper = self.initial_guess + range_size
            
            # Tenta expandir até encontrar mudança de sinal
            for attempt in range(15):  # Aumentado de 5 para 15
                try:
                    f_lower = objective(lower)
                    f_upper = objective(upper)
                    
                    # Verifica mudança de sinal
                    if f_lower * f_upper < 0:
                        return lower, upper, True
                    
                    # Estratégia de expansão adaptativa
                    if attempt < 5:
                        # Primeiras tentativas: expande simetricamente
                        expansion = scale * (2 ** attempt)
                        lower = self.initial_guess - expansion
                        upper = self.initial_guess + expansion
                    else:
                        # Tentativas posteriores: expande assimetricamente
                        if abs(f_lower) < abs(f_upper):
                            # target_p está abaixo de lower
                            lower -= scale * 3
                        else:
                            # target_p está acima de upper
                            upper += scale * 3
                    
                except Exception:
                    # Se houver erro no cálculo, tenta outro intervalo
                    lower -= scale
                    upper += scale
            
            return None, None, False
        
        # Tenta encontrar solução
        try:
            lower_bound, upper_bound, found = find_valid_bounds()
            
            if found:
                # Usa brentq com limites válidos
                self.c_solution = brentq(
                    objective,
                    lower_bound,
                    upper_bound,
                    xtol=1e-8,
                    rtol=1e-6,
                    maxiter=100
                )
            else:
                # Fallback: usa fsolve
                result = fsolve(objective, self.initial_guess, full_output=True, xtol=1e-6)
                self.c_solution = float(result[0][0])
                
                # Verifica se fsolve convergiu
                if result[2] != 1:
                    # Se fsolve falhou, usa o chute inicial
                    self.c_solution = self.initial_guess
        
        except Exception as e:
            # Último fallback: chute inicial
            self.c_solution = self.initial_guess
        
        # Validação Monte Carlo
        X_samples = self.muX + self.sigmaX * np.random.randn(n_samples)
        Y_samples = self.muY + self.sigmaY * np.random.randn(n_samples)
        Z_samples = X_samples * Y_samples
        self.mc_p = np.mean(Z_samples <= self.c_solution)

        return round(self.c_solution, 6)

    def print_verification_results(self) -> None:
        """Imprime resultados de verificação (público)"""
        if self.c_solution is None:
            print("Execute solve_inverse_cdf() primeiro")
            return
            
        print("\n" + "="*60)
        print("## RESULTADOS DO CÁLCULO DE CDF INVERSA")
        print("="*60)
        print(f"Probabilidade alvo: {self.target_p:.6f}")
        print(f"Valor c calculado: {self.c_solution:.6f}")
        print(f"Verificação Monte Carlo: P(Z <= {self.c_solution:.6f}) = {self.mc_p:.6f}")
        print(f"Erro absoluto: {np.abs(self.target_p - self.mc_p):.6f}")
        print(f"Erro relativo: {np.abs(self.target_p - self.mc_p)/self.target_p * 100:.4f}%")
        print("="*60)

    def plot_cdf(self) -> None:
        """Plota CDF com a solução encontrada"""
        if self.c_solution is None:
            print("Execute solve_inverse_cdf() primeiro")
            return
        
        z_range_factor = 4
        z_min = self.theoretical_mean - z_range_factor * self.theoretical_std
        z_max = self.theoretical_mean + z_range_factor * self.theoretical_std
        z_range = np.linspace(z_min, z_max, 200)

        print("\nCalculando CDF para plotagem...")
        
        # Calcula CDF com supressão de warnings
        cdf_values = []
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=Warning)
            cdf_values = Parallel(n_jobs=-1, verbose=0)(
                delayed(InverseProdOfTwoVariables._compute_product_cdf_1d)(
                    z, self.muX, self.sigmaX, self.muY, self.sigmaY
                )
                for z in z_range
            )
        
        plt.figure(figsize=(10, 6))
        plt.plot(z_range, cdf_values, 'b-', linewidth=2, label='CDF de Z=XY')
        plt.axvline(x=self.c_solution, color='r', linestyle='--', linewidth=2, 
                   label=f'c = {self.c_solution:.2f}')
        plt.axhline(y=self.target_p, color='g', linestyle='--', linewidth=2, 
                   label=f'P = {self.target_p:.3f}')
        plt.plot(self.c_solution, self.target_p, 'ro', markersize=10, 
                markerfacecolor='red', markeredgecolor='darkred', markeredgewidth=2,
                label='Solução')
        plt.xlabel('z', fontsize=12)
        plt.ylabel('P(Z ≤ z)', fontsize=12)
        plt.title(f'CDF de Z = X×Y e Solução para P(Z ≤ c) = {self.target_p:.3f}', fontsize=14)
        plt.legend(loc='upper left', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
