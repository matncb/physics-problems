#solver.py

from config import * #carrega configurações
import numpy as np

class Solver:
    def __init__(self):
        #Renomeando para nomes mais simples
        
        self.m, self.ap, self.yd, self.yr, self.ym = (
            MASSA, 
            APOGEU, 
            ALTURA_ABERTURA_DROGUE,
            ALTURA_ABERTURA_REEFING,  
            ALTURA_ABERTURA_MAIN
        ) 

        self.AD, self.cdD, self.AR, self.cdR, self.AM, self.cdM = (
            AREA_DROGUE, 
            CD_DROGUE,
            AREA_REEFING,
            CD_REEFING,
            AREA_MAIN,
            CD_MAIN
        )
                                    
        self.g, self.vx, self.vy = (
            ACELERACAO_GRAVITACIONAL,
            VELOCIDADE_VENTO_HORIZONTAL,
            VELOCIDADE_VENTO_VERTICAL
        )

    def rho(self, y):
        """
        Calcula a densidade do ar em função da altitude (acima do nível do mar).
        
        Parâmetros:
            y (float): Altitude em metros (0 a 25000)
        
        Retorna:
            float: Densidade do ar em kg/m³
        """
        # Constantes
        R_star = 8.3144598    # Constante universal dos gases [J/(mol·K)]
        M = 0.0289644         # Massa molar do ar [kg/mol]
        g0 = 9.80665          # Gravidade padrão [m/s²]
        L = -0.0065           # Gradiente térmico troposférico [K/m]
        
        # Ajuste para São Carlos (altitude média = 856 m)
        T0_sl = 288.15        # Temperatura padrão ao nível do mar [K]
        P0_sl = 101325.0      # Pressão padrão ao nível do mar [Pa]
        h_sc = 856            # Altitude de São Carlos [m]
        
        # Temperatura e pressão ao nível de São Carlos
        T0_sc = T0_sl + L * h_sc
        P0_sc = P0_sl * (T0_sc / T0_sl)**(-g0 * M / (R_star * L))
        
        # Altitude absoluta acima do nível do mar
        h = y
        
        # Camada 1: Troposfera (0-11 km)
        if h <= 11000:
            T = T0_sc + L * (h - h_sc)
            P = P0_sc * (T / T0_sc)**(-g0 * M / (R_star * L))
        
        # Camada 2: Baixa Estratosfera (11-20 km)
        elif h <= 20000:
            T_trop = T0_sc + L * (11000 - h_sc)  # Temperatura no topo da troposfera
            P_trop = P0_sc * (T_trop / T0_sc)**(-g0 * M / (R_star * L))
            T = T_trop  # Temperatura constante
            P = P_trop * np.exp(-g0 * M * (h - 11000) / (R_star * T))
        
        # Camada 3: Estratosfera (20-25 km)
        else:
            T_trop = T0_sc + L * (11000 - h_sc)
            P_trop = P0_sc * (T_trop / T0_sc)**(-g0 * M / (R_star * L))
            P_20k = P_trop * np.exp(-g0 * M * (20000 - 11000) / (R_star * T_trop))
            T_20k = T_trop + 0.001 * (h - 20000)  # Gradiente positivo
            P = P_20k * (T_20k / T_trop)**(-g0 * M / (R_star * 0.001))
            T = T_20k
        
        # Cálculo da densidade
        return (P * M) / (R_star * T)
    
    def F_drag(self, cd, A, S):
        #Modelo para a força de arrasto

        y, y_dot, x, x_dot = S
        rho_value = self.rho(y)

        Fx = (1/2)* rho_value* cd * A * (y_dot**2 + x_dot**2)**(1/2) * x_dot
        Fy = (1/2)* rho_value* cd * A * (y_dot**2 + x_dot**2)**(1/2) * y_dot

        return (Fx, Fy)

    def dSdt(self, S):
        #Modelo matemático em formato matricial
        #S = [y, y_dot, x, x_dot] --> matriz
        # dSdt = [y_dot, y_ddot, x_dot, x_ddot]
        # Precisamos escrever y_ddot e x_ddot em termos de um modelo físico
        
        y, y_dot, x, x_dot = S

        y_ddot = 0
        x_ddot = 0

        return [y_dot, y_ddot, x_dot, x_ddot]


        
    
