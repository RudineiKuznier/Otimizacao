from prodOfTwoVariables import ProdOfNormalRVs

if __name__ == "__main__":

    muX = 70.27       
    sigmaX = 16.8196    
    muY = 13.11      
    sigmaY = 0.4786   
    
    try:
        analyzer = ProdOfNormalRVs(muX, sigmaX, muY, sigmaY)
        std_dev = analyzer.solve_cdf()
        probability = analyzer.compute_product_cdf_1d(1000)
        print(f"{std_dev} -- {probability}")
        #analyzer._print_verification_results()
        #analyzer.plot_cdfs()

    except Exception as e:
        print(f"\nErro: {e}")