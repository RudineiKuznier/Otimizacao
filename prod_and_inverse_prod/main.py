from inverseProdOfTwoVariables import InverseProdOfTwoVariables
from prodOfTwoVariables import ProdOfNormalRVs
from Tabela import Tabela, Parametros
from Particoes_na_tabela import SUPLIERS_POSICOES, FACTORS_POSICOES, DISTRIBUTORS_POSICOES, RETAILERS_POSICOES
import threading
import os
mux_parametros = threading.Lock()
thread_semaphore = threading.Semaphore(800)
todas_threads = []

def calculaLB_thread(parametro: Parametros, index: int):
    try:
        solver = InverseProdOfTwoVariables(parametro.mux1, parametro.sigmax1, 
                                         parametro.muy, parametro.sigmay)
        c_solution = solver.solve_inverse_cdf()
        
        # Modifica diretamente o objeto Parametros
        with mux_parametros:
            parametro.lw = c_solution
            
    except Exception as e:
        print(f"✗ Erro thread LW {index}: {e} : muX={parametro.mux1}, sigX={parametro.sigmax1}, muY={parametro.muy}, sigY={parametro.sigmay}")
        with mux_parametros:
            parametro.lw = 0.0


def calculaDESV_thread(parametro: Parametros, index: int):
    try:
        analyzer = ProdOfNormalRVs(muX=parametro.mux2,
                                   sigmaX=parametro.sigmax2,
                                   muY=parametro.muy,
                                   sigmaY=parametro.sigmay)
        std_dev = analyzer.solve_cdf()
        # Modifica diretamente o objeto Parametros
        with mux_parametros:
            parametro.desv = std_dev
            
    except Exception as e:
        print(f"✗ Erro thread DESV {index}: {e} : muX={parametro.mux2}, sigX={parametro.sigmax2}, muY={parametro.muy}, sigY={parametro.sigmay}")
        with mux_parametros:
            parametro.lw = 0.0

def calculoDESVArt_thread(parametro: Parametros, index: int):
    try:
        analyzer_art = ProdOfNormalRVs(muX=parametro.muxart,
                                       sigmaX=parametro.sigxart,
                                       muY=parametro.muy,
                                       sigmaY=parametro.sigyart,
                                        c=(parametro.muxart * parametro.muy))
        std_dev_art = analyzer_art.solve_cdf()
        # Modifica diretamente o objeto Parametros
        with mux_parametros:
            parametro.desv_art = std_dev_art
            
    except Exception as e:
        print(f"✗ Erro thread DESVArt {index}: {e} : muX={parametro.muxart}, sigX={parametro.sigxart}, muY={parametro.muy}, sigY={parametro.sigyart}")
        with mux_parametros:
            parametro.lw = 0.0

def calculaPROB_thread(parametro: Parametros, index: int):
    try:
        analyzer = ProdOfNormalRVs(muX=parametro.mux2,
                                   sigmaX=parametro.sigmax2,
                                   muY=parametro.muy,
                                   sigmaY=parametro.sigmay,
                                   c=parametro.reorder)
        analyzer_art = ProdOfNormalRVs(muX=parametro.muxart,
                                      sigmaX=parametro.sigxart,
                                      muY=parametro.muy,
                                      sigmaY=parametro.sigyart)
        probart = analyzer_art.compute_product_cdf_1d(parametro.constart)
        std_dev = analyzer.solve_cdf()
        if parametro.reorder != 0:
            probability = analyzer.compute_product_cdf_1d(parametro.reorder)
            erro_percentual = analyzer.get_relative_error()
        else :
            probability = 0.0
            erro_percentual = 0.0
        

        with mux_parametros:
            parametro.prob = probability
            parametro.probart = probart
            parametro.error = erro_percentual
            parametro.desv = std_dev

    except Exception as e:
        print(f"✗ Erro thread linha({parametro.linha_salvar}) coluna({parametro.coluna_salvar}) {index}: {e} : muX={parametro.mux2}, sigX={parametro.sigmax2}, muY={parametro.muy}, sigY={parametro.sigmay}, c={parametro.reorder}\n"
              f" muX_art={parametro.muxart}, sigX_art={parametro.sigxart}, muY_art={parametro.muy}, sigY_art={parametro.sigyart}, c_art={parametro.constart}")

        with mux_parametros:
            parametro.lw = 0.0
    finally:
        thread_semaphore.release()

if __name__ == "__main__":
    THREAD_MODE = True
    CALCULAR_DEV_LW = True
    global COLUNA_INICIO
    # mude aqui e em Particoes_na_tabela.py o inicio da coluna
    NUM_TABELAS = 1  # número de matrizes (colunas de partição)
    ARQUIVO = "Stock_Data_in_days_cv_02_3Var.xlsx"
    PAGINA = "Main_variables"
    print(f" ===== SISTEMA DE CALCULOS DE DESVIOS, LB E PROBABILIDADES =====\n"
          f"Digite '1' para calcular DESV e LB \n"
          f"Digite '0' para calcular PROBABILIDADES\n")
    user_input = input("Opção >> ")
    if user_input == '1':
        CALCULAR_DEV_LW = True
        COLUNA_INICIO = 4
        NUM_TABELAS = 1
    elif user_input == '0':
        CALCULAR_DEV_LW = False
        COLUNA_INICIO = 26
        NUM_TABELAS = 9
    ARQUIVO = input("Digite a planilha alvo >> ")
    print(f"Configuração de execução:\n"
          f"Arquivo: {ARQUIVO}\n"
          f"Página: {PAGINA}\n"
          f"Número de tabelas: {NUM_TABELAS}\n"
          f"Cálculo de DESV e LB: {CALCULAR_DEV_LW}\n"
          f"Coluna de início: {COLUNA_INICIO}\n")
    
    # Inicialização
    tabela = Tabela()
    tabela.carregarArquivoParaRam(ARQUIVO)

    # lista de partições a carregar
    particoes = [
        ("SUPLIERS", SUPLIERS_POSICOES),
        ("FACTORS", FACTORS_POSICOES),
        ("DISTRIBUTORS", DISTRIBUTORS_POSICOES),
        ("RETAILERS", RETAILERS_POSICOES)
    ]

    todas_threads = []
    todos_parametros_validos = []

    # --- carregar todas as tabelas ---
    for nome_particao, particao in particoes:
        for j in range(NUM_TABELAS):
            print(f"=== CARREGANDO MATRIZ {nome_particao} #{j} ===")
            parametros = tabela.carregarMatriz(particao, PAGINA, tabela=j,coluna_inicio=COLUNA_INICIO)
            if not parametros:
                print(f"⚠️  Nenhum parâmetro lido em {nome_particao} tabela {j}")
                continue

            def parametro_valido(p: Parametros):
                return (
                    True
                    # p.mux2 > 0
                    # is not None and p.muy is not None
                    # and p.sigmax2 is not None and p.sigmay is not None
                    # and p.sigmax2 > 0 and p.sigmay > 0
                    # and p.mux2 > 0 and p.muy > 0
                )

            parametros_validos = [p for p in parametros if parametro_valido(p)]

            print(f"{nome_particao} tabela {j}: {len(parametros_validos)} parâmetros válidos")

            for i, param in enumerate(parametros_validos):
                todos_parametros_validos.append((nome_particao, j, i, param))

    print(f"\n=== TOTAL: {len(todos_parametros_validos)} parâmetros válidos em {len(particoes)*NUM_TABELAS} matrizes ===")
    
    # --- processamento (threads ou sequencial) ---
    if THREAD_MODE:
        if CALCULAR_DEV_LW :
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
                    args=(param, j * 1000 + i + 1),
                    name=f"{nome_particao}_T{j}_P{i}_DESV"
                )
                t2.start()
                todas_threads.append(t2)

                t3 = threading.Thread(
                    target=calculoDESVArt_thread,
                    args=(param, j * 1000 + i + 2),
                    name=f"{nome_particao}_T{j}_P{i}_DESV_ART"
                )
                t3.start()
                todas_threads.append(t3)
                

            for i, t in enumerate(todas_threads):
                t.join()
                if (i + 1) % 20 == 0:
                    print(f"Concluídas {i + 1}/{len(todas_threads)} threads LB/DESV")

            todas_threads.clear()

        else:
            print("Iniciando threads de probabilidade...")
            total = 0
            for nome_particao, j, i, param in todos_parametros_validos:
                thread_semaphore.acquire()
                total +=1
                t3 = threading.Thread(
                    target=calculaPROB_thread,
                    args=(param, j * 1000 + i),
                    name=f"{nome_particao}_T{j}_P{i}_PROB"
                )
                t3.start()
                todas_threads.append(t3)

            for i, t in enumerate(todas_threads):
                t.join()
                if (i + 1) % 20 == 0:
                    print(f"Concluídas {i + 1}/{len(todas_threads)} threads PROB")

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
    os.system('afplay /System/Library/Sounds/Glass.aiff')
    print(f"\n🎉 Processo finalizado! {len(todos_parametros_validos)} parâmetros processados.")
