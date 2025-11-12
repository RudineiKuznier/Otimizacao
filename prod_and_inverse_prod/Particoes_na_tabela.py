


class PosicoesParametros:
    def __init__(self,sigmaxart,sigmayart,constart,muxart,muy,mux1,sigmax1,sigmay,mux2,sigmax2,reoder_c,saidadesvpad,saidalbw,saidaprob,saidaprobart):
        self.SIGMAXART = sigmaxart
        self.SIGMAYART = sigmayart
        self.CONSTART = constart
        self.MUXART = muxart
        self.MUY = muy
        self.MUX1 = mux1
        self.SIGMAX1 = sigmax1
        self.SIGMAY = sigmay
        self.MUX2 = mux2
        self.SIGMAX2 = sigmax2
        self.REODER_C = reoder_c
        self.SAIDADESVPAD = saidadesvpad
        self.SAIDALBW = saidalbw
        self.SAIDAPROB = saidaprob
        self.SAIDAPROBART = saidaprobart
        

class Particao:
    def __init__(self,coluna_inicio,linha_inicio,qtd_linhas,qtd_colunas,passo_coluna,passo_linha,num_matrizes,posicoes_parametros : PosicoesParametros):
        self.COLUNA_INICIO          = coluna_inicio
        self.LINHA_INICIO           = linha_inicio
        # QTD define a quantidade de linhas e colunas que possue uma matriz 
        self.QTD_COLUNAS            = qtd_colunas
        self.QTD_LINHAS             = qtd_linhas
        self.PASSO_COLUNA           = passo_coluna
        self.PASSO_LINHA            = passo_linha
        self.NUM_MATRIZES           = num_matrizes
        self.POSICOES_PARAMETROS    = posicoes_parametros


SUPLIERS_VAR_POSICOES = PosicoesParametros( sigmaxart   = 138,  #   DesvPad(demand)
                                            sigmayart   = 143,  #   DesvPad(E(RLT))
                                            constart    = 158,  #   Reorder(Estado da arte)
                                            muxart      = 43,   #   demand
                                            muy         = 48,   #   Média(E(RLT))
                                            mux1        = 58,   #   Var(d-cap)
                                            sigmax1     = 63,   #   Desvpad(Var(S2nd))
                                            sigmay      = 68,   #   DesvPad(Var(E(RLT)))
                                            mux2        = 73,   #   Média(d-Cap)
                                            sigmax2     = 78,   #   DesvPad(Var(d-cap))
                                            reoder_c    = 13,   #   Reorder
                                            saidadesvpad= 88,   #   DesvPad(ND*ELT)
                                            saidalbw    = 83,   #   LB
                                            saidaprob   = 3,    #   P(Reorder)
                                            saidaprobart= 8  )  #   P(Estado da arte)
# utilize essa variável para carregar todas as factores
SUPLIERS_POSICOES = Particao(coluna_inicio      = 26,
                            linha_inicio        = 0,
                            qtd_linhas          = 3,
                            qtd_colunas         = 15,
                            passo_linha         = 0,
                            passo_coluna        = 7,
                            num_matrizes        = 9,
                            posicoes_parametros = SUPLIERS_VAR_POSICOES)


FACTORS_VAR_POSICOES = PosicoesParametros( sigmaxart   = 303,
                                            sigmayart   = 308,
                                            constart    = 323,
                                            muxart      = 208,
                                            muy         = 213,
                                            mux1        = 223,
                                            sigmax1     = 228,
                                            sigmay      = 233,
                                            mux2        = 238,
                                            sigmax2     = 243,
                                            reoder_c    = 323,
                                            saidadesvpad= 253,
                                            saidalbw    = 248,
                                            saidaprob   = 168,
                                            saidaprobart= 173  )
# utilize essa variável para carregar todas as factores
FACTORS_POSICOES = Particao(coluna_inicio      = 26,
                            linha_inicio        = 166,
                            qtd_linhas          = 3,
                            qtd_colunas         = 3,
                            passo_linha         = 0,
                            passo_coluna        = 19,
                            num_matrizes        = 9,
                            posicoes_parametros = FACTORS_VAR_POSICOES)


DISTRIBUTORS_VAR_POSICOES = PosicoesParametros( sigmaxart   = 138,
                                            sigmayart   = 143,
                                            constart    = 158,
                                            muxart      = 43,
                                            muy         = 48,
                                            mux1        = 58,
                                            sigmax1     = 63,
                                            sigmay      = 68,
                                            mux2        = 73,
                                            sigmax2     = 78,
                                            reoder_c    = 13,
                                            saidadesvpad= 88,
                                            saidalbw    = 83,
                                            saidaprob   = 3,
                                            saidaprobart= 8  )
# utilize essa variável para carregar todas as factores
DISTRIBUTORS_POSICOES = Particao(coluna_inicio      = 28,
                            linha_inicio        = 0,
                            qtd_linhas          = 3,
                            qtd_colunas         = 15,
                            passo_linha         = 0,
                            passo_coluna        = 7,
                            num_matrizes        = 9,
                            posicoes_parametros = DISTRIBUTORS_VAR_POSICOES)

                        
RETAILERS_VAR_POSICOES = PosicoesParametros( sigmaxart   = 138,
                                            sigmayart   = 143,
                                            constart    = 158,
                                            muxart      = 43,
                                            muy         = 48,
                                            mux1        = 58,
                                            sigmax1     = 63,
                                            sigmay      = 68,
                                            mux2        = 73,
                                            sigmax2     = 78,
                                            reoder_c    = 13,
                                            saidadesvpad= 88,
                                            saidalbw    = 83,
                                            saidaprob   = 3,
                                            saidaprobart= 8  )
# utilize essa variável para carregar todas as factores
RETAILERS_POSICOES = Particao(coluna_inicio      = 28,
                            linha_inicio        = 0,
                            qtd_linhas          = 3,
                            qtd_colunas         = 15,
                            passo_linha         = 0,
                            passo_coluna        = 7,
                            num_matrizes        = 9,
                            posicoes_parametros = RETAILERS_VAR_POSICOES)

