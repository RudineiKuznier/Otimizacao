from bivariate_analyzer import BivariateCDFAnalyzer
import config

if __name__ == "__main__":

    analyzer = BivariateCDFAnalyzer(
        config.MU_VECTOR,
        config.SIGMA_MATRIX,
        config.X1_LIMITS,
        config.X2_LIMITS,
        config.NUM_GRID_POINTS
    )

    analyzer.export_to_excel(
        file_name=config.EXCEL_FILE_NAME,
        sheet_name=config.EXCEL_SHEET_NAME
    )

    closest_results = analyzer.find_closest_cdf_values(
        config.INPUT_VALUE_TO_FIND,
        config.NUM_RESULTS_DESIRED
    )

    print(f"\nOs {config.NUM_RESULTS_DESIRED} valores da CDF mais próximos (onde X1*X2 <= {config.INPUT_VALUE_TO_FIND}):")
    if closest_results:
        for res in closest_results:
            print(f"  CDF: {res['cdf_value']:.9f}, Produto (X1*X2): {res['product_X1X2']:.3f}, X1: {res['X1']:.4f}, X2: {res['X2']:.4f}")
    else:
        print("Nenhum produto de X1*X2 foi encontrado que seja menor ou igual ao valor de entrada.")

    analyzer.plot_cdf_3d()