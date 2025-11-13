from inverseProdOfTwoVariables import InverseProdOfTwoVariables
from prodOfTwoVariables import ProdOfNormalRVs
from Tabela import Tabela, Parametros
from Particoes_na_tabela import SUPLIERS_POSICOES, FACTORS_POSICOES, DISTRIBUTORS_POSICOES, RETAILERS_POSICOES
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
    NUM_TABELAS = 9  # número de matrizes (colunas de partição)
    ARQUIVO = "Stock_Data_in_days_cv_02_5V.xlsx"
    PAGINA = "Main_variables"

    # Inicialização
    tabela = Tabela()
    tabela.carregarArquivoParaRam(ARQUIVO)

    # lista de partições a carregar
    particoes = [
        ("SUPLIERS", SUPLIERS_POSICOES),
        ("FACTORS", FACTORS_POSICOES)
        #("DISTRIBUTORS", DISTRIBUTORS_POSICOES),
        #("RETAILERS", RETAILERS_POSICOES)
    ]

    todas_threads = []
    todos_parametros_validos = []

    # --- carregar todas as tabelas ---
    for nome_particao, particao in particoes:
        for j in range(NUM_TABELAS):
            print(f"=== CARREGANDO MATRIZ {nome_particao} #{j} ===")
            parametros = tabela.carregarMatriz(particao, PAGINA, tabela=j)
            if not parametros:
                print(f"⚠️  Nenhum parâmetro lido em {nome_particao} tabela {j}")
                continue

            def parametro_valido(p: Parametros):
                return (
                    p.mux2 is not None and p.muy is not None
                    and p.sigmax2 is not None and p.sigmay is not None
                    and p.sigmax2 > 0 and p.sigmay > 0
                    and p.mux2 > 0 and p.muy > 0
                )

            parametros_validos = [p for p in parametros if parametro_valido(p)]

            print(f"{nome_particao} tabela {j}: {len(parametros_validos)} parâmetros válidos")

            for i, param in enumerate(parametros_validos):
                todos_parametros_validos.append((nome_particao, j, i, param))

    print(f"\n=== TOTAL: {len(todos_parametros_validos)} parâmetros válidos em {len(particoes)*NUM_TABELAS} matrizes ===")

    # --- processamento (threads ou sequencial) ---
    if THREAD_MODE:
        print("Iniciando threads de cálculo (LB e DESV)...")

        for nome_particao, j, i, param in todos_parametros_validos:
            # Thread LB
            t1 = threading.Thread(
                target=calculaLB_thread,
                args=(param, j * 1000 + i),
                name=f"{nome_particao}_T{j}_P{i}_LB"
            )
            t1.start()
            todas_threads.append(t1)

            # Thread DESV
            t2 = threading.Thread(
                target=calculaDESV_thread,
                args=(param, j * 1000 + i),
                name=f"{nome_particao}_T{j}_P{i}_DESV"
            )
            t2.start()
            todas_threads.append(t2)

        for i, t in enumerate(todas_threads):
            t.join()
            if (i + 1) % 20 == 0:
                print(f"Concluídas {i + 1}/{len(todas_threads)} threads LB/DESV")

        todas_threads.clear()

        # print("Iniciando threads de probabilidade...")

        # for nome_particao, j, i, param in todos_parametros_validos:
        #     t3 = threading.Thread(
        #         target=calculaPROB_thread,
        #         args=(param, j * 1000 + i),
        #         name=f"{nome_particao}_T{j}_P{i}_PROB"
        #     )
        #     t3.start()
        #     todas_threads.append(t3)

        # for i, t in enumerate(todas_threads):
        #     t.join()
        #     if (i + 1) % 20 == 0:
        #         print(f"Concluídas {i + 1}/{len(todas_threads)} threads PROB")

    else:
        print("Executando cálculos sequencialmente...")
        for nome_particao, j, i, param in todos_parametros_validos:
            calculaLB_thread(param, j * 1000 + i)
            calculaDESV_thread(param, j * 1000 + i)
            calculaPROB_thread(param, j * 1000 + i)

    # --- salvar resultados ---
    print("\n=== SALVANDO RESULTADOS ===")

    # agrupar por partição
    resultados_por_particao = {
        "SUPLIERS": [],
        "FACTORS": [],
        "DISTRIBUTORS": [],
        "RETAILERS": []
    }
    for nome_particao, _, _, param in todos_parametros_validos:
        resultados_por_particao[nome_particao].append(param)

    for nome_particao, particao in particoes:
        parametros = resultados_por_particao[nome_particao]
        if parametros:
            tabela.salvarEmLote(parametros)
            print(f"✓ {nome_particao}: {len(parametros)} resultados salvos")
        else:
            print(f"✗ {nome_particao}: Nenhum resultado válido")

    tabela.removerArquivoDaRam()

    print(f"\n🎉 Processo finalizado! {len(todos_parametros_validos)} parâmetros processados.")
