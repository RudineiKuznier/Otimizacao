
from math import sqrt
import numpy as np
from scipy.stats import norm,gaussian_kde
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Inverse_Prod_Two_Variables.Inverse_ProdOfTwoVariables_version8 import compute_product_cdf_1d
import matplotlib.pyplot as plt

# [VERIFICAR] - Comentários com essa marcação precisa ser revisado, talzaer não tenha uma conversão direta

def radicandVersion1(muX : float , sigmaX : float, muY : float , sigmaY : float, c : float ) :
    # Product of Normal RVs - CDF Computation for W = sqrt(14.4 * X * Y)
    # Compute P(W ≤ k) where W = sqrt(14.4 * X * Y) and X, Y are independent normal variables

    # ____________________ CÉLULA (2,1)

    # Parameters (radicand 2,1) {S2 * RLT} radicand para 5 vezes o quadrado da variância

    

    #******************************************************************


    # Calculate k from equation 3: k = sqrt(c * 14.4)
    k = sqrt(c * 14.4)

    # Compute P(W ≤ k) = P(sqrt(14.4 * X * Y) ≤ k) = P(X*Y ≤ k^2/14.4)
    # From equation 2: P(W ≤ k) = P(X*Y ≤ k^2/14.4)
    c_target = (k*k) / 14.4

    # Monte Carlo Simulation for P(X*Y ≤ c_target)
    n_samples = 1000000

    # Generate samples for Z = X*Y
    X_samples = muX + sigmaX * np.random.randn(n_samples)
    Y_samples = muY + sigmaY * np.random.randn(n_samples)
    Z_samples = X_samples * Y_samples

    # Compute Monte Carlo result for P(X*Y ≤ c_target)
    mc_result_z = np.mean(Z_samples <= c_target)
    
    # Numerical Integration for P(X*Y ≤ c_target)
    numerical_result = compute_product_cdf_1d(c_target, muX, sigmaX, muY, sigmaY);

    # Calculate Moments for Z = X*Y and W = sqrt(14.4 * X * Y)
    # Theoretical moments for Z = X*Y (exact formulas for product of independent normals)
    theoretical_mean_z = muX * muY;
    theoretical_variance_z = muX^2 * sigmaY^2 + muY^2 * sigmaX^2 + sigmaX^2 * sigmaY^2;
    theoretical_std_z = sqrt(theoretical_variance_z);

    # Check if Z = X*Y is approximately normal using coefficient of variation
    cv_X = sigmaX / muX;
    cv_Y = sigmaY / muY;

    # Theoretical moments for W = sqrt(14.4 * X * Y) assuming Z = X*Y ~ N(μ_z, σ_z²)
    # Using the delta method for transformation g(Z) = sqrt(14.4 * Z)

    # First-order delta method (simple approximation)
    theoretical_mean_w_1st = sqrt(14.4 * theoretical_mean_z)
    theoretical_variance_w_1st = 14.4 * theoretical_variance_z/(4 * theoretical_mean_z)
    theoretical_std_w_1st = sqrt(theoretical_variance_w_1st)

    # Second-order delta method (more accurate)
    theoretical_mean_w_2nd = sqrt(14.4 * theoretical_mean_z) * (1 - theoretical_variance_z/(8 * theoretical_mean_z^2))
    theoretical_variance_w_2nd = 14.4 * theoretical_variance_z/(4 * theoretical_mean_z) * (1 - theoretical_variance_z/(8 * theoretical_mean_z^2))
    theoretical_std_w_2nd = sqrt(theoretical_variance_w_2nd)

    # Empirical moments from Monte Carlo (only for Z)
    empirical_mean_z = np.mean(Z_samples)
    empirical_variance_z = np.var(Z_samples)
    empirical_std_z = np.std(Z_samples)


    if theoretical_std_w_1st > 0 :
        p_w_normal_1st = norm.cdf(k, theoretical_mean_w_1st, theoretical_std_w_1st)

    if theoretical_std_w_2nd > 0 :
        p_w_normal_2nd = norm.cdf(k, theoretical_mean_w_2nd, theoretical_std_w_2nd)


    # Create CDF and PDF Plots for Z = X*Y
    # Set automatic range based on theoretical properties
    z_range_factor = 4; # Number of standard deviations to show
    z_center = theoretical_mean_z
    z_half_range = z_range_factor * theoretical_std_z

    # Create range for plotting that ensures c_target is visible
    z_min_auto = min(z_center - z_half_range, c_target - z_half_range/2)
    z_max_auto = max(z_center + z_half_range, c_target + z_half_range/2)
    z_range = np.linspace(z_min_auto, z_max_auto, 1000)

    # Compute CDF values using numerical integration
    cdf_integration = np.zeros(len(z_range))
    for i in range(len(z_range)):
        cdf_integration[i] = compute_product_cdf_1d(z_range[i], muX, sigmaX, muY, sigmaY)

    # Compute empirical CDF from Monte Carlo samples
    cdf_empirical = np.zeros(len(z_range))
    for i in range(len(z_range)):
        cdf_empirical[i] = np.mean(Z_samples <= z_range[i])

    # Create PDF using theoretical approximation
    pdf_values = norm.pdf(z_range, theoretical_mean_z, theoretical_std_z)

    # Get empirical PDF from Monte Carlo for reference  
    # [VERIFICAR] PARECE QUE PODE SER UM POUCO DIFERENTE
    kde = gaussian_kde(Z_samples)
    pdf_empirical_kde = kde.evaluate(z_range)
    pdf_points = z_range  # equivalente ao segundo output

    # Figure 1: CDF Plot for Z = X*Y with both integration and empirical
    plt.figure(figsize=(8, 5))
    plt.plot(z_range, cdf_integration, 'b-', linewidth=2, label='CDF (Integration)')
    plt.plot(z_range, cdf_empirical, 'r--', linewidth=1.5, label='CDF (Monte Carlo)')
    plt.axvline(c_target, color='k', linestyle='--', linewidth=2, label=f'c = k²/14.4 = {c_target:.2f}')
    plt.axhline(numerical_result, color='g', linestyle='--', linewidth=1.5, label=f'P(Z ≤ c) = {numerical_result:.3f}')
    plt.xlabel('z (X*Y)')
    plt.ylabel('CDF')
    plt.title('Cumulative Distribution Function of Z = X*Y')
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.xlim([z_min_auto, z_max_auto])
    plt.ylim([0, 1])
    plt.tight_layout()
    plt.show()


    # Figure 2: PDF Plot for Z = X*Y


    # Figure 3: Theoretical distribution of W = sqrt(14.4 * X * Y)

    # Generate theoretical range for W based on normal approximation
    w_min = max(0, min(theoretical_mean_w_1st - 4*theoretical_std_w_1st, theoretical_mean_w_2nd - 4*theoretical_std_w_2nd))
    w_max = max(theoretical_mean_w_1st + 4*theoretical_std_w_1st, theoretical_mean_w_2nd + 4*theoretical_std_w_2nd)
    w_range = np.linspace(w_min, w_max, 1000)
    w_pdf_1st = norm.pdf(w_range, theoretical_mean_w_1st, theoretical_std_w_1st)
    w_pdf_2nd = norm.pdf(w_range, theoretical_mean_w_2nd, theoretical_std_w_2nd)

    # Add CDF difference analysis
    cdf_difference = abs(cdf_integration - cdf_empirical)
    max_diff = max(cdf_difference)
    mean_diff = np.mean(cdf_difference)

    # Plot the difference


muX = 282.9083;       # Mean of X
sigmaX = 160.9752;    # Std dev of X
muY = 13.11;      # Mean of Y
sigmaY = 0.4786;   # Std dev of Y
c = 8074.181162;      # Value for c in P(XY ≤ c)

# teste

radicandVersion1(muX=muX,sigmaX=sigmaX,muY=muY,sigmaY=sigmaY,c=c)