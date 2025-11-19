from prodOfTwoVariables import ProdOfNormalRVs

if __name__ == "__main__":

    muX = 317.95       
    sigmaX = 11.79    
    muY = 10.11      
    sigmaY = 2.6320   
    
    try:
        analyzer = ProdOfNormalRVs(muX, sigmaX, muY, sigmaY)
        std_dev = analyzer.solve_cdf()
        probability = analyzer.compute_product_cdf_1d(4705.83) #c 4705.83
        print(f"{std_dev} -- {probability}")
        #analyzer._print_verification_results()
        #analyzer.plot_cdfs()

    except Exception as e:
        print(f"\nErro: {e}")