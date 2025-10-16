from prodOfTwoVariables import ProdOfNormalRVs

if __name__ == "__main__":

    muX = 70.27       
    sigmaX = 16.8196    
    muY = 13.11      
    sigmaY = 0.4786   

    n_samples_mc = 1000000 
    
    try:
     
        analyzer = ProdOfNormalRVs(muX, sigmaX, muY, sigmaY)

        std_dev, probability = analyzer.solve_cdf(n_samples=n_samples_mc)
        print(f"{std_dev} -- {probability}")
        #analyzer._print_verification_results()
        #analyzer.plot_cdfs()
        

        analyzer2 = ProdOfNormalRVs(muX, sigmaX, muY, sigmaY, 2000)
        std_dev, probability = analyzer2.solve_cdf(n_samples=n_samples_mc)
        print(f"{std_dev} -- {probability}")
        #analyzer._print_verification_results()
        #analyzer.plot_cdfs()

    except Exception as e:
        print(f"\nErro: {e}")