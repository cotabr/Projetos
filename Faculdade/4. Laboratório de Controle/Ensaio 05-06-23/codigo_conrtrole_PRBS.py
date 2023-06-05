"""
Bancada Motor-Gerador
UFPA - Campus Tucuruí
Monitoria de Sistemas de Controle para Engenharia - PGRAD - MONITORIA 03/2020
Coodenador: Cleison Daniel Silva
Bolsista: Felipe Silveira Piano
Data: 27/09/2020
"""

# gerenciador de dispositivo - encontrar porta COM

# from pyserial import Serial
import numpy as np
import matplotlib.pyplot as plt            # noqa: F401
import time as t
from scipy.signal import square, sawtooth  # noqa: F401
import serial


#%% Parâmetros do sistema
amplitude_maxima = 15
Ts = 0.02
fre = 0.5
Amplitude = 1
nivel_dc_saida = 3.53
ponto_de_operacao = 7.5

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
    r[n] = 3*prbs[n]+ponto_de_operacao

##########################################
# Tensão de alimentação da bancada

# numAmostras = 400
# tempo = np.zeros(numAmostras)
y = np.zeros(numAmostras)

# Kc = 0.86  # Ganho integral
# a = 35  # Posição do zero

# a = 2*np.ones(int(numAmostras/2))
# b = 4*np.ones(int(numAmostras/2))
# u = np.concatenate([a,b]) #degrau

# r = np.zeros(numAmostras)
u = np.zeros(numAmostras)

toc = np.zeros(numAmostras)
# #####################

# for n in range(numAmostras):
#    r[n] = Amplitude*square(2*np.pi*fre*n*Ts)
    # r[n] = Amplitude*sawtooth(2*np.pi*fre*n*Ts) + setpoint
    # r[n] = Amplitude*np.sin(2*np.pi*fre*n*Ts) + setpoint
    # r[n] = u[n]

# print('\nEstabelecendo conexão.')
# conexao = serial.Serial(port='COM5', baudrate=9600, timeout=0.005)

print('\nEstabelecendo conexão.')
# conexao = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=0.005)
conexao = serial.Serial(port='COM5', baudrate=9600, timeout=0.005)

t.sleep(1)
print('\nIniciando coleta.')

# #_____________ Loop principal de controle _____________##
nivel_dc_entrada = ponto_de_operacao

# Ganho do Controlador Proporcional
# Kp = 2.296  # Valor de projeto
Kp = 1.37

for n in range(numAmostras):
    tic = t.time()
    if (conexao.inWaiting() > 0):
        y[n] = conexao.readline().decode()

    # remove o nivel_dc_saida
    sinal_medido = y[n] - nivel_dc_saida
    # calcula o erro
    e = r[n] - sinal_medido

    # primeiras 50 amostras
    if (n < 50):
        u[n] = nivel_dc_entrada
        r[n] = 0.0
    else:
        u[n] = (Kp*e) + nivel_dc_entrada
        # print("Valor de (Kp*e)", (Kp*e))

    if (u[n] > amplitude_maxima):
        # print("Valor de u[n]", u[n])
        sinal_PWM = 255
    else:
        sinal_PWM = ((u[n])*255)/amplitude_maxima
    # sinal_PWM deve ser um número inteiro entre 0 e 255
    conexao.write(str(round(sinal_PWM)).encode())
    # print("Sinal Controle PWM: ", sinal_PWM)
    t.sleep(Ts)

    if (n > 0):
        tempo[n] = tempo[n-1] + Ts
    toc[n] = t.time() - tic

conexao.write('0'.encode())
print('\nFim da coleta.')
conexao.close()

print('media=', np.mean(r))

print('\nPeríodo real:', np.mean(toc))
print('Nivel_DC:', np.mean(y[tempo > 2]))

plt.figure(figsize=(10, 10))
plt.subplot(211)
plt.plot(tempo, u, '-b', linewidth=1.2)
plt.xlabel('Tempo(s)')
plt.ylabel('Tensão (V)')
plt.grid()
plt.title('Onda Quadrada - Malha Aberta')
plt.legend(loc='lower right', labels=('Sinal de Entrada', 'Sinal de Saída'))

plt.subplot(212)
plt.plot(tempo, r + nivel_dc_saida,'-b', tempo, y, '-r', linewidth=1.2)
# plt.plot(tempo, y, '-ro', linewidth=1.2)
plt.xlabel('Tempo(s)')
plt.ylabel('Tensão (V)')
plt.grid()
# plt.title('Tensão de Saída - Malha Aberta')
plt.show()

# dados = np.stack((tempo, r, y), axis=-1)

# r_ofessert = r + nivel_dc_saida

# dados = np.stack((tempo, r, y, u, r_ofessert), axis=-1)

# np.savetxt("controle_P_dados_motorgerador.csv", dados, delimiter=";")


# np.savetxt("6_5_dados_motorgerador.csv", dados, delimiter=";")
