from inverseProdOfTwoVariables import InverseProdOfTwoVariables

if __name__ == "__main__":
    
    muX = 467.0483        
    sigmaX = 278.6301   
    muY = 18.26     
    sigmaY = 0.6667      
    
    try:
        analyzer = InverseProdOfTwoVariables(muX, sigmaX, muY, sigmaY)
        c_solution = analyzer.solve_inverse_cdf()

        print(f"{c_solution}")
        #analyzer._print_verification_results()
        #solver.plot_cdf()
        
    except Exception as e:
        print(f"\nErro: {e}")
