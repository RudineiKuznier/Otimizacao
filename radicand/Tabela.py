
from enum import Enum
import threading
import openpyxl


# Guia de uso para o rudinei :

# Como carregar os dados da tabela ?
# declare a tabela
# tab = Tabela(localENome=TABELA_MATLAB,qtd_linhas=0,qtd_colunas=NUMCOLUNAS)
# parametros = pegarParametros(localENome=TABELA_MATLAB,coluna=0,valor=-1000)
# Parametros é um objeto que facilita o acesso aos parametros

# Para salvar um valor é :
# salvarColunaSaida(localENome=TABELA_MATLAB, coluna=coluna, valor=valor)
# coluna basta passar o index da coluna mesmo, algo como o iterador de parametros.

# Cria o mutex
mutex = threading.Lock()

# Defines de tabelas
NUMLINHAS       = 3
NUMCOLUNAS      = 15
TABELA_MATLAB = "Stock_Data_in_days_cv_0,2_2.xlsx"

LINHA_SALVAMENTO = 45

class Parametros:
    def __init__ (self,muy : float,mux : float,sigmax1 : float,sigmay : float, mux2 : float, sigmax2 : float):
        self.muy = muy
        self.mux = mux
        self.sigmax1 = sigmax1
        self.sigmay = sigmay
        self.mux2 = mux2
        self.sigmax2 = sigmax2

    def __repr__(self):
        return (f"Parâmetros da tabela : \n muy = {self.muy} \n mux = {self.mux} \n sigmax1 = {self.sigmax1} \n sigmay = {self.sigmay} \n mux2 = {self.mux2} \n sigmax2 = {self.sigmax2}")


class Posicoes(Enum) :

    MUY             = (8,4) # iguais
    MUX1             = (18,4) # diferentes
    SIGMAX1          = (23,4) # diferentes
    SIGMAY          = (28,4) # iguais

    MUX2             = (33,4) 
    SIGMAX2          = (38,4)

    SAIDAMEDIA      = (33,4)
    SAIDADESVPAD    = (38,4)
    SAIDALBW        = (45,4)
    SAIDADESCPAD    = (50,4)

    @property
    def linha(self):
        return self.value[0]
    
    @property
    def coluna(self):
        return self.value[1]
    
    @property
    def par(self):
        return {self.value[0],self.value[1]}
    

class Tabela :
    '" TABELA É NÃO SINCRONIZADA (NÃO MANTÉM O ARQUIVO XLSX ABERTO), SE PRECISAR, CHAMA ATUALIZAR "'
    def __init__(self, localENome: str,qtd_linhas : int, qtd_colunas : int):
        mutex.acquire()
        # Carregar o arquivo
        try:
            workbook = openpyxl.load_workbook(localENome,data_only=True)
            # Selecionar a planilha (sheet) ativa
            sheet = workbook.active
            
            # Inicializar lista de tabelas
            self.tabelas = []
            for coluna in range(qtd_colunas):
                muy = sheet.cell(row=Posicoes.MUY.linha, column=Posicoes.MUY.coluna + coluna).value or 0.0
                mux = sheet.cell(row=Posicoes.MUX1.linha, column=Posicoes.MUX1.coluna + coluna).value or 0.0
                sigmax1 = sheet.cell(row=Posicoes.SIGMAX1.linha, column=Posicoes.SIGMAX1.coluna + coluna).value or 0.0
                sigmay = sheet.cell(row=Posicoes.SIGMAY.linha, column=Posicoes.SIGMAY.coluna + coluna).value or 0.0
                mux2 = sheet.cell(row=Posicoes.MUX2.linha, column=Posicoes.MUX2.coluna + coluna).value or 0.0
                sigmax2 = sheet.cell(row=Posicoes.SIGMAX2.linha, column=Posicoes.SIGMAX2.coluna + coluna).value or 0.0
                parametro = Parametros(muy=muy,mux=mux,sigmax1=sigmax1,sigmay=sigmay, mux2=mux2, sigmax2=sigmax2)
                print(parametro)
                self.tabelas.append(parametro)
            workbook.close()
        finally:
            # Devolve o mutex
            mutex.release()

        return
    def pegarParametros(self) -> list[Parametros] :
        return self.tabelas
    
    def salvarColunaSaida(self, localENome: str, coluna: int, valor: float):
        # Pede permissão
        mutex.acquire()
        try:
            try:
                # Carregar o arquivo
                workbook = openpyxl.load_workbook(localENome)
                sheet = workbook.active
                
                # Substituir o valor na posição (LINHA_SALVAMENTO, coluna)
                sheet.cell(row=LINHA_SALVAMENTO, column=coluna + 4).value = valor
                
                # Salvar o arquivo
                workbook.save(localENome)
                workbook.close()
                
                print(f"Valor {valor} salvo em ({LINHA_SALVAMENTO}, {coluna + 4})")
                
            except FileNotFoundError:
                print(f"Erro: Arquivo '{localENome}' não encontrado")
            except PermissionError:
                print(f"Erro: Sem permissão para escrever no arquivo '{localENome}'")
            except Exception as e:
                print(f"Erro ao salvar arquivo: {e}")

        finally:
            # Devolve o mutex
            mutex.release()
        
        
        return
        


