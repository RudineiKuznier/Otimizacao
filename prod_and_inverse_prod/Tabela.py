
from enum import Enum
import xlwings as xw
import threading
import openpyxl

# Cria o mutex
mutex = threading.Lock()

# inicio da primeira linha e coluna
LINHA_INICIO                    = 0
COLUNA_INICIO                   = 28
NUM_LINHAS_INICIO_AO_FIM        = 136
NUM_COLUNAS_INICIO_AO_FIM       = 22
# diz a quantidade de colunas que separa uma tabela de outra
NUM_COLUNAS_ENTRE_MATRIZES      = 0
# DEFINE DE QUANTIDADES DE LINHAS E COLUNAS NUMA TABELA
NUMLINHAS                       = 3
NUMCOLUNAS                      = 15
# DEFINE DO NÚMERO DE TABELAS EM UMA PÁGINA
NUM_MATRIZES_NA_PAGINA          = 9
# DEFINE DAS LOCALIZAÇÕES DOS ARQUIVOS
LOCAL_NOME_TABELA               = "Stock_Data_in_days_cv_0,2_5V.xlsx"
PAGINA_NO_DOCUMENTO             = "Main_variables"
# DEFINE DAS POSIÇÕES DOS VALORES DENTRO DA MATRIZ
MUY_LINHA                       = 48
MUX1_LINHA                      = 58
SIGMAX1_LINHA                   = 63
SIGMAY_LINHA                    = 68
MUX2_LINHA                      = 73
SIGMAX2_LINHA                   = 78
SAIDADESVPAD_LINHA              = 88
SAIDALBW_LINHA                  = 83
SAIDAPROB_LINHA                 = 3

class Parametros:
    def __init__ (self,muy : float,mux1 : float,sigmax1 : float,sigmay : float, mux2 : float, sigmax2 : float, linha_salvar : int, coluna_salvar : int,nome_tabela : str ,pagina_tabela : str):
        self.muy = muy
        self.mux1 = mux1
        self.sigmax1 = sigmax1
        self.sigmay = sigmay
        self.mux2 = mux2
        self.sigmax2 = sigmax2
        self.linha_salvar = linha_salvar
        self.coluna_salvar = coluna_salvar
        self.nome_tabela = nome_tabela
        self.pagina_tabela = pagina_tabela

    def __repr__(self):
        return (f"Parâmetros da tabela : \n muy = {self.muy} \n mux1 = {self.mux1} \n sigmax1 = {self.sigmax1} \n sigmay = {self.sigmay} \n mux2 = {self.mux2} \n sigmax2 = {self.sigmax2} \n linha = {self.linha_salvar} \n coluna = {self.coluna_salvar} \n ")


class Posicoes(Enum) :

    MUY             = (LINHA_INICIO + MUY_LINHA,COLUNA_INICIO) # iguais
    MUX1            = (LINHA_INICIO + MUX1_LINHA,COLUNA_INICIO) # diferentes
    SIGMAX1         = (LINHA_INICIO + SIGMAX1_LINHA,COLUNA_INICIO) # diferentes
    SIGMAY          = (LINHA_INICIO + SIGMAY_LINHA,COLUNA_INICIO) # iguais
    MUX2            = (LINHA_INICIO + MUX2_LINHA,COLUNA_INICIO) 
    SIGMAX2         = (LINHA_INICIO + SIGMAX2_LINHA,COLUNA_INICIO)
    SAIDADESVPAD    = (LINHA_INICIO + SAIDADESVPAD_LINHA,COLUNA_INICIO)
    SAIDALBW        = (LINHA_INICIO + SAIDALBW_LINHA,COLUNA_INICIO)
    SAIDAPROB       = (LINHA_INICIO + SAIDAPROB_LINHA,COLUNA_INICIO)

    @property
    def linha(self):
        return self.value[0]
    
    @property
    def coluna(self):
        return self.value[1]

    

class Tabela :
    def __init__(self,pagina : str, localENome: str,matriz_linha : int, matriz_coluna : int):
        self.tabelas = []
        mutex.acquire()
        try:
            workbook = openpyxl.load_workbook(localENome, data_only=True)
            print (f" --------- LENDO DE ---------\n Tabela. : {localENome} \n Página : {pagina} \n")
            # Verifica se a página existe
            if pagina in workbook.sheetnames:
                sheet = workbook[pagina]
            else:
                # Lista as páginas disponíveis se a desejada não existir
                print(f"Página {pagina} não encontrada.")
                workbook.close()
                exit(1)
            shift_coluna = matriz_coluna * NUM_COLUNAS_INICIO_AO_FIM
            shift_linha  = matriz_linha * NUM_LINHAS_INICIO_AO_FIM
            for linha in range(NUMLINHAS):
                for coluna in range(NUMCOLUNAS):
                    muy     = sheet.cell(row=Posicoes.MUY.linha + linha  + shift_linha, column=Posicoes.MUY.coluna + coluna + shift_coluna).value or 0.0
                    mux1    = sheet.cell(row=Posicoes.MUX1.linha + linha  + shift_linha, column=Posicoes.MUX1.coluna + coluna + shift_coluna).value or 0.0
                    sigmax1 = sheet.cell(row=Posicoes.SIGMAX1.linha + linha  + shift_linha, column=Posicoes.SIGMAX1.coluna + coluna + shift_coluna).value or 0.0
                    sigmay  = sheet.cell(row=Posicoes.SIGMAY.linha + linha  + shift_linha, column=Posicoes.SIGMAY.coluna + coluna + shift_coluna).value or 0.0
                    mux2    = sheet.cell(row=Posicoes.MUX2.linha + linha  + shift_linha, column=Posicoes.MUX2.coluna + coluna + shift_coluna).value or 0.0
                    sigmax2 = sheet.cell(row=Posicoes.SIGMAX2.linha + linha  + shift_linha, column=Posicoes.SIGMAX2.coluna + coluna + shift_coluna).value or 0.0
                    coluna_salvar = coluna + shift_coluna + COLUNA_INICIO
                    parametro = Parametros(muy=muy, mux1=mux1, sigmax1=sigmax1, sigmay=sigmay, mux2=mux2, sigmax2=sigmax2, linha_salvar=linha + shift_linha,coluna_salvar= coluna_salvar,nome_tabela=localENome,pagina_tabela=pagina)

                    # print(parametro)

                    self.tabelas.append(parametro)
            
            workbook.close()
        except Exception as e:
            print(f"Erro ao carregar arquivo: {e}")
        finally:
            mutex.release()
        return
    
    def pegarParametros(self) -> list[Parametros] :
        return self.tabelas
    
    def salvarEmLote(self,valores : list[float], parametro : list[Parametros],lwb: bool = False, desvpad: bool = False,probabilidade : bool = False) :
        return

    def salvarColunaSaida(self, valor: float, parametro : Parametros, lwb: bool = False, desvpad: bool = False,probabilidade : bool = False):
        # Pede permissão
        mutex.acquire()
        try:
            try:
                # Carregar o arquivo
                workbook = openpyxl.load_workbook(parametro.nome_tabela)
                
                # Selecionar a página específica
                sheet = workbook[parametro.pagina_tabela]
                
                if (desvpad):
                    linha = Posicoes.SAIDADESVPAD.linha
                elif (lwb):
                    linha = Posicoes.SAIDALBW.linha
                elif (probabilidade):
                    linha = Posicoes.SAIDAPROB.linha
                else:
                    print("ERRO AO TENTAR SALVAR NA TABELA, NÃO FOI PASSADO O PARÂMETRO DA LINHA DE SALVAMENTO.")
                    exit(1) 
                coluna = parametro.coluna_salvar
                # Substituir o valor na posição (linha, coluna + 4)
                print(f"Salvando ({valor}) na coluna ({coluna}) e linha ({linha + parametro.linha_salvar}) \n")
                sheet.cell(row=parametro.linha_salvar + linha, column=coluna).value = valor
                
                # Salvar o arquivo
                workbook.save(parametro.nome_tabela)
                workbook.close()
                
                # print(f"Valor {valor} salvo em {parametro.pagina_tabela}({ parametro.linha_salvar + linha}, {parametro.coluna_salvar + 4})")
                
            except FileNotFoundError:
                print(f"Erro: Arquivo '{parametro.nome_tabela}' não encontrado")
            except KeyError:
                print(f"Erro: Página '{parametro.pagina_tabela}' não encontrada. Páginas disponíveis: {workbook.sheetnames}")
            except PermissionError:
                print(f"Erro: Sem permissão para escrever no arquivo '{parametro.nome_tabela}'")
            except Exception as e:
                print(f"Erro ao salvar arquivo: {e}")

        finally:
            # Devolve o mutex
            mutex.release()
        
        return
        


# tab = Tabela(pagina= PAGINA_NO_DOCUMENTO,localENome= LOCAL_NOME_TABELA,matriz_linha=0,matriz_coluna=1)
# parametros = tab.pegarParametros()
# index = 0
# for i in parametros :
#     tab.salvarColunaSaida(valor=index,parametro=i,lwb=True)
#     index += 1