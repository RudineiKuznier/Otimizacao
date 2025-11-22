from prodOfTwoVariables import ProdOfNormalRVs

if __name__ == "__main__":

    muX = 70.27;        # Mean of X
    sigmaX = 40.77;     # Std dev of X
    muY = 13.11;        # Mean of Y
    sigmaY = 0.4786;    # Std dev of Y
    c = 1591.3746;      # Single value for computation

    try:
        analyzer = ProdOfNormalRVs(muX, sigmaX, muY, sigmaY, c)
        std_dev = analyzer.solve_cdf()
        probability = analyzer.compute_product_cdf_1d(c)
        erro_percentual = analyzer.get_relative_error()

        print(f"{std_dev} -- {probability} -- {erro_percentual}%")
        #analyzer._print_verification_results()
        #analyzer.plot_cdfs()

    except Exception as e:
        print(f"\nErro: {e}")