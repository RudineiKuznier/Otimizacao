import numpy as np
from scipy.stats import norm
from scipy.integrate import quad
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from scipy.optimize import brentq
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
        if np.abs(x) < 1e-12:
            return 0.0
        if positive_x:
            return norm.cdf(c / x, loc=muY, scale=sigmaY) * norm.pdf(x, loc=muX, scale=sigmaX)
        else:
            return (1 - norm.cdf(c / x, loc=muY, scale=sigmaY)) * norm.pdf(x, loc=muX, scale=sigmaX)

    @staticmethod
    def _compute_product_cdf_1d(c: float, muX: float, sigmaX: float, muY: float, sigmaY: float) -> float:
        epsabs = 1e-10
        epsrel = 1e-8
        limit = 500

        if c >= 0:
            part1, _ = quad(InverseProdOfTwoVariables._integrand, -np.inf, 0, args=(c, muX, sigmaX, muY, sigmaY, False), epsabs=epsabs, epsrel=epsrel, limit=limit)
            part2, _ = quad(InverseProdOfTwoVariables._integrand, 0, np.inf, args=(c, muX, sigmaX, muY, sigmaY, True), epsabs=epsabs, epsrel=epsrel, limit=limit)
            return float(part1 + part2)
        else:
            part1, _ = quad(InverseProdOfTwoVariables._integrand, -np.inf, 0, args=(c, muX, sigmaX, muY, sigmaY, False), epsabs=epsabs, epsrel=epsrel, limit=limit)
            part2, _ = quad(InverseProdOfTwoVariables._integrand, 0, np.inf, args=(c, muX, sigmaX, muY, sigmaY, True), epsabs=epsabs, epsrel=epsrel, limit=limit)
            return float(part1 + part2)


    def solve_inverse_cdf(self, n_samples=1000000) -> float:
        self.initial_guess = norm.ppf(self.target_p, loc=self.theoretical_mean, scale=self.theoretical_std)
        self.func = lambda c: InverseProdOfTwoVariables._compute_product_cdf_1d(c, self.muX, self.sigmaX, self.muY, self.sigmaY) - self.target_p
        
        #self.c_solution, self.info, self.ier, self.msg = fsolve(self.func, self.initial_guess, full_output=True, xtol=1e-6)
        #self.c_solution = self.c_solution[0]

        # Zero modificado
        self.c_solution = brentq(
            self.func,
            self.initial_guess - 3 * self.theoretical_std,
            self.initial_guess + 3 * self.theoretical_std,
            xtol=1e-8
        )

        X_samples = self.muX + self.sigmaX * np.random.randn(n_samples)
        Y_samples = self.muY + self.sigmaY * np.random.randn(n_samples)
        Z_samples = X_samples * Y_samples
        self.mc_p = np.mean(Z_samples <= self.c_solution)

        return round(self.c_solution, 6)
        

    def _print_verification_results(self) -> None:
        print("## Inverse CDF Calculation Results")
        print(f"Target probability: {self.target_p:.6f}")
        print(f"Calculated c value: {self.c_solution:.6f}")
        print(f"Monte Carlo verification: P(Z <= {self.c_solution:.6f}) = {self.mc_p:.6f}")
        print(f"Absolute error: {np.abs(self.target_p - self.mc_p):.6f}")
        print(f"Relative error: {np.abs(self.target_p - self.mc_p)/self.target_p * 100:.4f}%")
    

    def plot_cdf(self) -> None:
        if self.c_solution is None:
            return
        
        z_range_factor = 4
        z_min = self.theoretical_mean - z_range_factor * self.theoretical_std
        z_max = self.theoretical_mean + z_range_factor * self.theoretical_std
        z_range = np.linspace(z_min, z_max, 1000)

        print("CDF:")
        cdf_values = Parallel(n_jobs=-1)(
            delayed(InverseProdOfTwoVariables._compute_product_cdf_1d)(z, self.muX, self.sigmaX, self.muY, self.sigmaY)
            for z in z_range
        )
        
        plt.figure(figsize=(8, 6))
        plt.plot(z_range, cdf_values, 'b-', linewidth=2, label='CDF')
        plt.axvline(x=self.c_solution, color='r', linestyle='--', linewidth=2, label=f'c = {self.c_solution:.2f}')
        plt.axhline(y=self.target_p, color='g', linestyle='--', linewidth=2, label=f'P = {self.target_p:.3f}')
        plt.plot(self.c_solution, self.target_p, 'ro', markersize=8, markerfacecolor='r')
        plt.xlabel('z')
        plt.ylabel('CDF')
        plt.title(f'CDF of Z = X*Y and Solution for P(Z ≤ c) = {self.target_p:.3f}')
        plt.legend(loc='upper left')
        plt.grid(True)
        plt.show()