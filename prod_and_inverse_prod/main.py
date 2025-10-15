from inverseProdOfTwoVariables import InverseProdOfTwoVariables
from prodOfTwoVariables import ProdOfNormalRVs

if __name__ == "__main__":
    #================== Inverse ==========================
    muX_inv = 20.0        
    sigmaX_inv = 30.0     
    muY_inv = 300.0      
    sigmaY_inv = 150.0    
    target_p_inv = 0.95   
    
    try:
        print("f\n ---------- InverseProdOfTwoVariables -----------\n")
        solver = InverseProdOfTwoVariables(muX_inv, sigmaX_inv, muY_inv, sigmaY_inv, target_p_inv)
      
        c_solution, mc_p = solver.solve_inverse_cdf(n_samples=5000000)

        solver._print_verification_results()

        solver.plot_cdf()
        
    except Exception as e:
        print(f"\nErro: {e}")


    #============== Prod ==================
    muX_prod = 100.0        
    sigmaX_prod = 35.8305     
    muY_prod = 30.0      
    sigmaY_prod = 1.6433    
    c = 3633.0      
    n_samples_mc = 1000000 
    
    try:
        print("f\n ---------- ProdOFTwoVariables -----------\n")

        analyzer = ProdOfNormalRVs(muX_prod, sigmaX_prod, muY_prod, sigmaY_prod, c)

        analyzer.run_analysis(n_samples=n_samples_mc)

        analyzer.print_results()

        analyzer.plot_cdfs_and_pdfs()
        
    except Exception as e:
        print(f"\nErro: {e}")
