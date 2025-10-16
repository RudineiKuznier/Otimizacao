from inverseProdOfTwoVariables import InverseProdOfTwoVariables
from prodOfTwoVariables import ProdOfNormalRVs
from Tabela import Tabela, Parametros
import threading

mux_parametros = threading.Lock()

def calculaLB_thread(parametro: Parametros, index: int):
    try:
        print(f"Thread {index} iniciada - mux1: {parametro.mux1}, muy: {parametro.muy}")
        
        solver = InverseProdOfTwoVariables(parametro.mux1, parametro.sigmax1, 
                                         parametro.muy, parametro.sigmay, 0.98)
        c_solution = solver.solve_inverse_cdf()
        
        # Modifica diretamente o objeto Parametros
        with mux_parametros:
            parametro.lw = c_solution
            print(f"✓ Thread {index} concluída: lw = {c_solution}")
            
    except Exception as e:
        print(f"✗ Erro thread {index}: {e}")
        with mux_parametros:
            parametro.lw = 0.0
def calculaDESV_thread(parametro: Parametros, index: int):
    try:
        print(f"Thread {index} iniciada - mux1: {parametro.mux1}, muy: {parametro.muy}")
        
        solver = InverseProdOfTwoVariables(parametro.mux1, parametro.sigmax1, 
                                         parametro.muy, parametro.sigmay, 0.98)
        c_solution = solver.solve_inverse_cdf()
        
        # Modifica diretamente o objeto Parametros
        with mux_parametros:
            parametro.lw = c_solution
            print(f"✓ Thread {index} concluída: lw = {c_solution}")
            
    except Exception as e:
        print(f"✗ Erro thread {index}: {e}")
        with mux_parametros:
            parametro.lw = 0.0
def calculaPROB_thread(parametro: Parametros, index: int):
    try:
        print(f"Thread {index} iniciada - mux1: {parametro.mux1}, muy: {parametro.muy}")
        
        solver = InverseProdOfTwoVariables(parametro.mux1, parametro.sigmax1, 
                                         parametro.muy, parametro.sigmay, 0.98)
        c_solution = solver.solve_inverse_cdf()
        
        # Modifica diretamente o objeto Parametros
        with mux_parametros:
            parametro.lw = c_solution
            print(f"✓ Thread {index} concluída: lw = {c_solution}")
            
    except Exception as e:
        print(f"✗ Erro thread {index}: {e}")
        with mux_parametros:
            parametro.lw = 0.0





if __name__ == "__main__":
    THREAD_MODE = True
    tabela = Tabela(pagina='Main_variables', localENome='Stock_Data_in_days_cv_0,2_5V.xlsx', 
                   matriz_linha=0, matriz_coluna=0)
    parametros_originais = tabela.pegarParametros()

    # Filtrar e mostrar parâmetros válidos
    parametros_validos = [p for p in parametros_originais if p.mux1 > 0]
    print(f"Encontrados {len(parametros_validos)} parâmetros válidos para processamento")
    
    # Mostrar estado inicial
    for i, p in enumerate(parametros_validos):
        print(f"Parametro {i}: lw inicial = {p.lw}")

    # Processamento (threads ou sequencial)
    if THREAD_MODE:
        threads = []
        for i, param in enumerate(parametros_validos):
            threadlw = threading.Thread(target=calculaLB_thread, args=(param, i))
            threadlw.start()
            threads.append(threadlw)
            threaddesv = threading.Thread(target=calculaDESV_thread, args=(param, i))
            threaddesv.start()
            threads.append(threaddesv)
            threadprob = threading.Thread(target=calculaPROB_thread, args=(param, i))
            threadprob.start()
            threads.append(threadprob)
        
        # Aguardar conclusão
        for i, thread in enumerate(threads):
            thread.join()
    else:
        for i, param in enumerate(parametros_validos):
            calculaLB_thread(param, i)

    if parametros_validos:
        tabela.salvarEmLote(parametros=parametros_validos)
        print(f"\n✓ {len(parametros_validos)} resultados salvos com sucesso!")
    else:
        print("Nenhum resultado para salvar")

    print("Processo finalizado!")