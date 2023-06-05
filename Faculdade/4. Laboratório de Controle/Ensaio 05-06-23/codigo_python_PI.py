"""
Bancada Motor-Gerador
UFPA - Campus Tucuruí
Monitoria de Sistemas de Controle para Engenharia - PGRAD - MONITORIA 03/2020
Coodenador: Cleison Daniel Silva
Bolsista: Felipe Silveira Piano
Data: 27/09/2020
"""

# %% Bibliotecas utilizadas ---------------------------------------

import control as ct
import serial
import numpy as np
import matplotlib.pyplot as plt
import time as t
from scipy.signal import square, sawtooth

# %% -----------------------------------------------------------

#%% Sinal PRBS

def PRBS(size_min_seq, size):
    rand = np.random.randint(0, 10, size=size)
    prbs = []
    for i in range(size):
        if rand[i] > 5:
            prbs.append(np.ones(size_min_seq))
        else:
            prbs.append(np.zeros(size_min_seq))
    prbs = np.array(prbs).reshape(size*size_min_seq)[0:size]
    return prbs

prbs = PRBS(size_min_seq=2**3, size=1024)
numAmostras = len(prbs)
r = np.zeros(numAmostras)

tempo = np.linspace(0,4,1024)

for n in range(numAmostras):
    r[n] = prbs[n]

# %% Parâmetros do sistema e simulação

Ts = 0.02  # Tempo de amostragem
fre = 0.5  # Frequência
Amplitude = 0.1 # Amplitude
ponto_de_operacao = 7.5+0.5  # Ponto de Operação
nivel_dc_saida = 3.53+0.5  # Nível DC de Saída
amplitude_maxima = 15  # Tensão de alimentação da bancada
# numAmostras = 500  # Número de amostras
Kc = 0.86  # Ganho integral
a = 35  # Posição do zero

# %% -----------------------------------------------------------

# %% Criando arrays para armazenar valores

# tempo = np.zeros(numAmostras)  # Tempo
y = np.zeros(numAmostras)  # Saída
# r = np.zeros(numAmostras)  # Referência
u = np.zeros(numAmostras)  # Entrada
du = np.zeros(numAmostras)  # ---
e = np.zeros(numAmostras)  # Erro
toc = np.zeros(numAmostras)  # ---

# %% -----------------------------------------------------------

# %% Sinal de referência

for n in range(numAmostras):
    # + ponto_de_operacao # Onda Quadrada
    r[n] = Amplitude*square(2*np.pi*fre*n*Ts)
    # r[n] = Amplitude*sawtooth(2*np.pi*fre*n*Ts) + setpoint        # Dente de Serra
    # r[n] = Amplitude*np.sin(2*np.pi*fre*n*Ts) + setpoint          # Senoide
    #r[n] = u[n]

# %% -----------------------------------------------------------

# %% Conexão com o arduino

print('\nEstabelecendo conexão.')
conexao = serial.Serial(port='COM5', baudrate=9600, timeout=0.005)

t.sleep(1)
print('\nIniciando coleta.')

# %% -----------------------------------------------------------

# %% Loop principal de controle

Gc = ct.tf([Kc*1, Kc*a], [1, 0])
nivel_dc_entrada = ponto_de_operacao
Gz = ct.c2d(Gc, Ts, 'tustin')
b0 = Gz.num[0][0][0]
b1 = Gz.num[0][0][1]


for n in range(numAmostras):
    tic = t.time()

    if (conexao.inWaiting() > 0):
        y[n] = conexao.readline().decode()

    # remove o nivel_dc_saida
    sinal_medido = y[n] - nivel_dc_saida

    # calcula o erro
    e[n] = r[n] - sinal_medido
    # primeiras 50 amostras
    if (n < 50):
        u[n] = nivel_dc_entrada
        r[n] = 0.0
    else:
        du[n] = du[n-1]+b0*e[n]+b1*e[n-1]
        u[n] = nivel_dc_entrada + du[n]

    if (u[n] > amplitude_maxima):
        sinal_PWM = 255
    else:
        sinal_PWM = ((u[n])*255)/amplitude_maxima
        # sinal_PWM = sinal_PWM + (nivel_dc_entrada*255)/15

    # sinal_PWM deve ser um número inteiro entre 0 e 255
    conexao.write(str(round(sinal_PWM)).encode())

    t.sleep(Ts)

    if (n > 0):
        tempo[n] = tempo[n-1] + Ts
    toc[n] = t.time() - tic
t.sleep(1)
conexao.write('0'.encode())
print('\nFim da coleta.')
conexao.close()
print('media=', np.mean(r))

# %% -----------------------------------------------------------

# %% Plots

janela = (tempo >= 0) & (tempo <= 8)

# PLOT 1

plt.figure(figsize=(15, 7))
plt.plot(tempo[janela], r[janela]+nivel_dc_saida, '-b',
         label='Sinal de Entrada', linewidth=1.2)
plt.plot(tempo[janela], y[janela],
         '-r', label='Sinal de Saída', linewidth=1.2)
plt.xlabel('Tempo(s)')
plt.ylabel('Tensão (V)')
plt.grid()
plt.title('Aplicação de Onda Quadrada no Sistema em MF')
plt.legend(loc='lower right')
plt.show()

# PLOT 2

plt.figure(figsize=(15, 7))
plt.plot(tempo[janela], u[janela],
         '-r', label='Sinal de Controle', linewidth=1.2)
plt.xlabel('Tempo(s)')
plt.ylabel('Tensão (V)')
plt.grid()
plt.title('Sinal de Controle do Sistema em MF')
plt.legend(loc='lower right')
plt.show()


# %% Armazenando e salvando os dados

# dados = np.stack((tempo, r, y, u), axis=-1)
# # np.savetxt("Simulação PI em MF.csv", dados, delimiter=",")

dados = np.stack((tempo, r, y), axis=-1)

r_ofessert = r + nivel_dc_saida

dados = np.stack((tempo, r, y, u, r_ofessert), axis=-1)

np.savetxt("controle_P_dados_motorgerador.csv", dados, delimiter=";")

# %% -----------------------------------------------------------

# %% Obtendo a média do sinal de entrada e saída

b = np.mean(y)
print('Média do sinal de saída:')
print(b)
c = np.mean(r)
print('Média do sinal de entrada:')
print(c)

# %% -----------------------------------------------------------
