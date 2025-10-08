from parallel_Inverse_ProdOfTwoVariables_version1 import InverseProdOfTwoVariables

if __name__ == "__main__":
    
    muX = 20.0        
    sigmaX = 30.0     
    muY = 300.0      
    sigmaY = 150.0    
    target_p = 0.95   
    
    try:
        solver = InverseProdOfTwoVariables(muX, sigmaX, muY, sigmaY, target_p)
        print("\n--- Executando o Cálculo da CDF Inversa ---")
        c_solution, mc_p = solver.solve_inverse_cdf(n_samples=5000000)
        solver._print_verification_results()
        print("\n--- Gerando Visualização Gráfica ---")
        #solver.plot_cdf()
        
    except Exception as e:
        print(f"\nErro: {e}")
