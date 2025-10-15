from inverseProdOfTwoVariables import InverseProdOfTwoVariables
from prodOfTwoVariables import ProdOfNormalRVs
from Tabela import Tabela,Parametros
import threading
import time

def processoA_thread(parametro : Parametros):
    muX_inv = parametro.mux1     
    sigmaX_inv = parametro.sigmax1 
    muY_inv = parametro.muy    
    sigmaY_inv = parametro.sigmay
    target_p_inv = 0.98

    try:
        # print("f\n ---------- InverseProdOfTwoVariables -----------\n")
        solver = InverseProdOfTwoVariables(muX_inv, sigmaX_inv, muY_inv, sigmaY_inv, target_p_inv)
    
        c_solution, mc_p = solver.solve_inverse_cdf(n_samples=5000000)

        # solver._print_verification_results()

        tabela.salvarColunaSaida(valor=c_solution,parametro=i,linha_lwb=0)
        # solver.plot_cdf()
            
    except Exception as e:
        print(f"\nErro: {e}")


if __name__ == "__main__":
    THREAD_MODE = True
    #================== Inverse ==========================

    tabela = Tabela(pagina='Matlab_Data',localENome='Stock_Data_in_days_cv_0,2_5V.xlsx')
    parametros = tabela.pegarParametros()


    for i in parametros :
        if (i.mux1 > 0) :
            if THREAD_MODE :
                threading.Thread(target=processoA_thread, args=(i,)).start()
            else :
                processoA_thread(parametro=i)
            
        

    exit(0)
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
