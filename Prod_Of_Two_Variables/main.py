from prodOfTwoVariables import ProdOfNormalRVs

if __name__ == "__main__":

    muX = 100.0        
    sigmaX = 35.8305     
    muY = 30.0      
    sigmaY = 1.6433    
    c = 3633.0      
    n_samples_mc = 1000000 
    
    try:
     
        analyzer = ProdOfNormalRVs(muX, sigmaX, muY, sigmaY, c)

        analyzer.run_analysis(n_samples=n_samples_mc)

        analyzer.print_results()

        #analyzer.plot_cdfs_and_pdfs()
        
    except Exception as e:
        print(f"\nErro: {e}")