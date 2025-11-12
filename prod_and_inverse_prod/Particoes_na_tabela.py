

class Particao:
    def __init__(self,coluna_inicio,linha_inicio,qtd_linhas,qtd_colunas,passo_coluna,passo_linha):
        self.COLUNA_INICIO  = coluna_inicio
        self.LINHA_INICIO   = linha_inicio
        self.QTD_COLUNAS    = qtd_colunas
        self.QTD_LINHAS     = qtd_linhas
        self.PASSO_COLUNA   = passo_coluna
        self.PASSO_LINHA    = passo_linha


FACTORS = Particao(coluna_inicio=26,linha_inicio=0,qtd_linhas=136,qtd_colunas=22,passo_linha=1,passo_coluna=)