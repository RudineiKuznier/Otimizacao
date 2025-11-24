import pandas as pd

arquivo_entrada = 'teste_planilha.xlsx'
df = pd.read_excel(arquivo_entrada, header=None)

# O atributo .T é um atalho para .transpose()
df_invertido = df.T

arquivo_saida = 'teste_planilha_saida.xlsx'

# index=False e header=False garantem que o Pandas não adicione 
# números de índice extras nas bordas da planilha.
df_invertido.to_excel(arquivo_saida, index=False, header=False)

print(f"Sucesso! O arquivo foi salvo como '{arquivo_saida}'")
