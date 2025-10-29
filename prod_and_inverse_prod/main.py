from inverseProdOfTwoVariables import InverseProdOfTwoVariables
from prodOfTwoVariables import ProdOfNormalRVs
from Tabela import Tabela, Parametros
import threading

mux_parametros = threading.Lock()

def calculaLB_thread(parametro: Parametros, index: int):
    try:
        
        solver = InverseProdOfTwoVariables(parametro.mux1, parametro.sigmax1, 
                                         parametro.muy, parametro.sigmay)
        c_solution = solver.solve_inverse_cdf()
        
        # Modifica diretamente o objeto Parametros
        with mux_parametros:
            parametro.lw = c_solution
            
    except Exception as e:
        print(f"✗ Erro thread {index}: {e}")
        with mux_parametros:
            parametro.lw = 0.0


def calculaDESV_thread(parametro: Parametros, index: int):
    try:
        
        analyzer = ProdOfNormalRVs(muX=parametro.mux2,sigmaX=parametro.sigmax2,muY=parametro.muy,sigmaY=parametro.sigmay)
        std_dev = analyzer.solve_cdf()
        # Modifica diretamente o objeto Parametros
        with mux_parametros:
            parametro.desv = std_dev
            
    except Exception as e:
        print(f"✗ Erro thread {index}: {e}")
        with mux_parametros:
            parametro.lw = 0.0

def calculaPROB_thread(parametro: Parametros, index: int):
    try:
        
        analyzer = ProdOfNormalRVs(muX=parametro.mux2,sigmaX=parametro.sigmax2,muY=parametro.muy,sigmaY=parametro.sigmay)
        probabilidade = analyzer.compute_product_cdf_1d(parametro.reorder)
        
        probart = analyzer.compute_product_cdf_1d(c_val=parametro.constart,muX=parametro.muxart,sigmaX=parametro.sigxart,muY=parametro.muy,sigmaY=parametro.sigyart)
        # print(f"===== Calculo da probabilidade do estado da arte =====\n P(stado da art) = {probart}\n C = {parametro.constart} \n muX = {parametro.muxart} \n sigX = {parametro.sigxart} \n muY = {parametro.muy}\n sigY = {parametro.sigyart} \n")
        # Modifica diretamente o objeto Parametros
        with mux_parametros:
            parametro.prob = probabilidade
            parametro.probart = probart
            
    except Exception as e:
        print(f"✗ Erro thread {index}: {e}")
        with mux_parametros:
            parametro.lw = 0.0




if __name__ == "__main__":
    THREAD_MODE = True
    NUM_TABELAS = 9  # Número de tabelas a processar
    
    todas_threads = []  # Lista para todas as threads de todas as tabelas
    todas_tabelas = []  # Lista para guardar as tabelas
    todos_parametros_validos = []  # Lista para todos os parâmetros válidos
    
    # Criar todas as tabelas e coletar todos os parâmetros
    for j in range(NUM_TABELAS):
        print(f"=== CARREGANDO TABELA {j} ===")
        tabela = Tabela(pagina='Main_variables', 
                       localENome='Stock_Data_in_days_cv_0,2_5V_rev05.xlsx', 
                       matriz_linha=0, 
                       matriz_coluna=j)
        
        parametros_originais = tabela.pegarParametros()
        parametros_validos = [p for p in parametros_originais if p.mux2 > 0]
        print(f"Tabela {j}: {len(parametros_validos)} parâmetros válidos")
        
        # Guardar tabela e parâmetros para uso posterior
        todas_tabelas.append(tabela)
        todos_parametros_validos.extend([(j, i, param) for i, param in enumerate(parametros_validos)])

    print(f"\n=== TOTAL: {len(todos_parametros_validos)} parâmetros válidos em {NUM_TABELAS} tabelas ===")

    # Processamento (threads ou sequencial)
    if THREAD_MODE:
        # Disparar TODAS as threads de UMA VEZ
        for tabela_idx, param_idx, param in todos_parametros_validos:
            # Thread para LB
            thread_lb = threading.Thread(
                target=calculaLB_thread, 
                args=(param, tabela_idx * 1000 + param_idx),  # ID único
                name=f"T{tabela_idx}-P{param_idx}-LB"
            )
            thread_lb.start()
            todas_threads.append(thread_lb)
            
            # Thread para DESV
            thread_desv = threading.Thread(
                target=calculaDESV_thread, 
                args=(param, tabela_idx * 1000 + param_idx),
                name=f"T{tabela_idx}-P{param_idx}-DESV"
            )
            thread_desv.start()
            todas_threads.append(thread_desv)

        print(f"Lançadas {len(todas_threads)} threads simultaneamente!")
        print("Aguardando todas as threads terminarem...")

        # Aguardar conclusão de TODAS as threads
        for i, thread in enumerate(todas_threads):
            thread.join()
            if (i + 1) % 10 == 0:  # Log a cada 10 threads
                print(f"Concluídas {i + 1}/{len(todas_threads)} threads")
        
        todas_threads.clear()

        # Disparar TODAS as threads de PROBABILIDADES
        for tabela_idx, param_idx, param in todos_parametros_validos:
            # Thread para LB
            thread_lb = threading.Thread(
                target=calculaPROB_thread, 
                args=(param, tabela_idx * 1000 + param_idx),  # ID único
                name=f"T{tabela_idx}-P{param_idx}-LB"
            )
            thread_lb.start()
            todas_threads.append(thread_lb)


        for i, thread in enumerate(todas_threads):
            thread.join()
            if (i + 1) % 10 == 0:  # Log a cada 10 threads
                print(f"Concluídas {i + 1}/{len(todas_threads)} threads")
                
    else:
        # Execução sequencial
        for tabela_idx, param_idx, param in todos_parametros_validos:
            calculaLB_thread(param, tabela_idx * 1000 + param_idx)
            calculaDESV_thread(param, tabela_idx * 1000 + param_idx)
            calculaPROB_thread(param, tabela_idx * 1000 + param_idx)

    # Salvar resultados por tabela
    print("\n=== SALVANDO RESULTADOS ===")
    
    # Agrupar parâmetros por tabela
    parametros_por_tabela = [[] for _ in range(NUM_TABELAS)]
    
    for tabela_idx, param_idx, param in todos_parametros_validos:
        parametros_por_tabela[tabela_idx].append(param)
    
    # Salvar cada tabela
    for j in range(NUM_TABELAS):
        parametros_tabela = parametros_por_tabela[j]
        if parametros_tabela:
            todas_tabelas[j].salvarEmLote(parametros=parametros_tabela)
            print(f"✓ Tabela {j}: {len(parametros_tabela)} resultados salvos")
        else:
            print(f"✗ Tabela {j}: Nenhum resultado para salvar")

    print(f"\n🎉 Processo finalizado! {len(todos_parametros_validos)} parâmetros processados em {NUM_TABELAS} tabelas")