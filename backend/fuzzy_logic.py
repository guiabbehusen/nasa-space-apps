import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

pm25_range = np.arange(0, 510, 0.1)
pm25 = ctrl.Antecedent(pm25_range, 'PM25')

# SO2 (1h média) em ppb
so2_range = np.arange(0, 1010, 1)
so2 = ctrl.Antecedent(so2_range, 'SO2')
co_range = np.arange(0, 51, 0.1)
co = ctrl.Antecedent(co_range, 'CO')


aqi_range = np.arange(0, 501, 1)
qualidade_ar = ctrl.Consequent(aqi_range, 'Qualidade_Ar', defuzzify_method='centroid')



pm25['Good'] = fuzz.trapmf(pm25_range, [0, 0, 12.0, 18.75]) # 18.75 é um ponto intermediário para sobreposição
pm25['Moderate'] = fuzz.trimf(pm25_range, [12.0, 23.75, 35.4]) # 23.75 = (12.1+35.4)/2
pm25['Unhealthy for Sensitive Groups'] = fuzz.trimf(pm25_range, [35.4, 45.45, 55.4]) # 45.45 = (35.5+55.4)/2
pm25['Unhealthy'] = fuzz.trimf(pm25_range, [55.4, 102.95, 150.4]) # 102.95 = (55.5+150.4)/2
pm25['Very_Unhealthy'] = fuzz.trimf(pm25_range, [150.4, 200.45, 250.4]) # 200.45 = (150.5+250.4)/2
pm25['Hazardous'] = fuzz.trapmf(pm25_range, [250.4, 375.45, 500.4, 500.4]) # Começa a 1 e permanece 1

## B. Funções de Pertinência para SO2 (ppb)

so2['Good'] = fuzz.trapmf(so2_range, [0, 0, 35, 55])
so2['Moderate'] = fuzz.trimf(so2_range, [35, 55, 75])
so2['Unhealthy_for_Sensitive_Groups'] = fuzz.trimf(so2_range, [75, 130, 185])
so2['Unhealthy'] = fuzz.trimf(so2_range, [185, 245, 304])
so2['Very_Unhealthy'] = fuzz.trimf(so2_range, [304, 454, 604])
so2['Hazardous'] = fuzz.trapmf(so2_range, [604, 804, 1004, 1004])

## C. Funções de Pertinência para CO (ppm)

co['Good'] = fuzz.trapmf(co_range, [0.0, 0.0, 4.4, 6.95])
co['Moderate'] = fuzz.trimf(co_range, [4.4, 6.95, 9.4])
co['Unhealthy_for_Sensitive_Groups'] = fuzz.trimf(co_range, [9.4, 10.95, 12.4])
co['Unhealthy'] = fuzz.trimf(co_range, [12.4, 13.95, 15.4])
co['Very_Unhealthy'] = fuzz.trimf(co_range, [15.4, 22.95, 30.4])
co['Hazardous'] = fuzz.trapmf(co_range, [30.4, 40.4, 50.4, 50.4])


qualidade_ar['Good'] = fuzz.trimf(aqi_range, [0, 25, 50])
qualidade_ar['Moderate'] = fuzz.trimf(aqi_range, [51, 75, 100])
qualidade_ar['Unhealthy_for_Sensitive_Groups'] = fuzz.trimf(aqi_range, [101, 125, 150])
qualidade_ar['Unhealthy'] = fuzz.trimf(aqi_range, [151, 175, 200])
qualidade_ar['Very_Unhealthy'] = fuzz.trimf(aqi_range, [201, 250, 300])
qualidade_ar['Hazardous'] = fuzz.trimf(aqi_range, [301, 400, 500])

regras = [
    # Categoria Good (Se TODOS forem 'Good')
    ctrl.Rule(pm25['Good'] & so2['Good'] & co['Good'], qualidade_ar['Good']),

    # Categoria Moderate
    ctrl.Rule(pm25['Moderate'] | so2['Moderate'] | co['Moderate'], qualidade_ar['Moderate']),

    # Categoria Unhealthy_for_Sensitive_Groups
    ctrl.Rule(pm25['Unhealthy_for_Sensitive_Groups'] | so2['Unhealthy_for_Sensitive_Groups'] | co['Unhealthy_for_Sensitive_Groups'], qualidade_ar['Unhealthy_for_Sensitive_Groups']),

    # Categoria Unhealthy
    ctrl.Rule(pm25['Unhealthy'] | so2['Unhealthy'] | co['Unhealthy'], qualidade_ar['Unhealthy']),

    # Categoria Very Unhealthy
    ctrl.Rule(pm25['Very_Unhealthy'] | so2['Very_Unhealthy'] | co['Very_Unhealthy'], qualidade_ar['Very_Unhealthy']),

    # Categoria Hazardous
    ctrl.Rule(pm25['Hazardous'] | so2['Hazardous'] | co['Hazardous'], qualidade_ar['Hazardous'])
]

# Nota: O uso do operador OR ( | ) no skfuzzy, juntamente com a estrutura de regras
# sequencial de pior caso, simula bem a lógica do AQI. O sistema escolherá
# a saída de maior peso.

# --- 4. SISTEMA DE CONTROLE FUZZY (SIMULAÇÃO) ---

# Cria o sistema de controle
sistema_controle = ctrl.ControlSystem(regras)
# Cria a simulação do sistema
qualidade_ar_simulador = ctrl.ControlSystemSimulation(sistema_controle)

# --- FUNÇÃO DE TESTE E CLASSIFICAÇÃO ---

def classificar_qualidade_ar(pm25_conc, so2_conc, co_conc):
    """
    Classifica a Qualidade do Ar com base nas concentrações de poluentes.

    Parâmetros:
    - pm25_conc (float): Concentração de PM2.5 (μg/m³) - 24h média
    - so2_conc (float): Concentração de SO2 (ppb) - 1h média
    - co_conc (float): Concentração de CO (ppm) - 8h média

    Retorna:
    - O índice AQI defuzzificado (float) e a categoria linguística (string).
    """

    # Passa as entradas para a simulação
    qualidade_ar_simulador.input['PM25'] = pm25_conc
    qualidade_ar_simulador.input['SO2'] = so2_conc
    qualidade_ar_simulador.input['CO'] = co_conc

    # Calcula o resultado
    qualidade_ar_simulador.compute()

    # Pega o valor defuzzificado (índice AQI)
    aqi_resultante = qualidade_ar_simulador.output['Qualidade_Ar']

    # Mapeia o valor AQI para a categoria linguística (para o output final)
    categorias = {
        (0, 50): 'Good', (51, 100): 'Moderate', (101, 150): 'Unhealthy for Sensitive Groups',
        (151, 200): 'Unhealthy', (201, 300): 'Very Unhealthy', (301, 500): 'Hazardous'
    }
    categoria_final = 'Não Classificado'
    for (min_aqi, max_aqi), cat_name in categorias.items():
        if min_aqi <= aqi_resultante <= max_aqi:
            categoria_final = cat_name
            break

    return aqi_resultante, categoria_final

# --- EXECUTANDO EXEMPLOS ---

# Exemplo 1: Ar Bom (Valores baixos)
aqi_1, cat_1 = classificar_qualidade_ar(pm25_conc=10.0, so2_conc=20, co_conc=3.0)
print(f"Exemplo 1 (Bom): PM2.5={10.0} | SO2={20} | CO={3.0}")
print(f"-> AQI Resultante: {aqi_1:.2f} (Categoria: {cat_1})\n")
# Esperado: Perto de 'Good' (0-50)

# Exemplo 2: Ar Unhealthy_for_Sensitive_Groups devido ao PM2.5 (PM2.5 na faixa Unhealthy_for_Sensitive_Groups)
aqi_2, cat_2 = classificar_qualidade_ar(pm25_conc=40.0, so2_conc=20, co_conc=3.0)
print(f"Exemplo 2 (Unhealthy_for_Sensitive_Groups): PM2.5={40.0} | SO2={20} | CO={3.0}")
print(f"-> AQI Resultante: {aqi_2:.2f} (Categoria: {cat_2})\n")
# Esperado: Perto de 'Unhealthy_for_Sensitive_Groups' (101-150)

# Exemplo 3: Ar Perigoso devido ao SO2
aqi_3, cat_3 = classificar_qualidade_ar(pm25_conc=10.0, so2_conc=700, co_conc=3.0)
print(f"Exemplo 3 (Hazardous): PM2.5={10.0} | SO2={700} | CO={3.0}")
print(f"-> AQI Resultante: {aqi_3:.2f} (Categoria: {cat_3})\n")
# Esperado: Perto de 'Hazardous' (301-500)