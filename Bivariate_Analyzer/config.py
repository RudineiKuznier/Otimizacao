MU_VECTOR = [15, 13.856] #Demanda e tempo - Variancia
SIGMA_MATRIX = [[494.624, 0], [0, 0.591]] #Matriz de correlação - análise
#Variancia da demanda
# 0 - correlação da demanda e do tempo: 0 é sem correlação 
# Tempo e demanda são curvas normais
# 0 - coeficiente de correlação
# Variancia do tempo

#Limite inferior -> probabilidade da demanda ser menor que 27 & menor que 14 é 50%  
#  e superior -> chance de ser maior que 97.288 e 16.7013 é praticamente 0 -> 3,7 desvios e é uma curva normal

X1_LIMITS = (27.1208, 97.288) # Número de desvios padrão
X2_LIMITS = (14.2751, 16.7013) #
NUM_GRID_POINTS = 25

EXCEL_FILE_NAME = 'Probability_distributions_OO.xlsx'
EXCEL_SHEET_NAME = 'CDF_Data'

INPUT_VALUE_TO_FIND = 956.2
NUM_RESULTS_DESIRED = 5 

#Multiplicação - & lógico
#X1 - 
#X2 - 