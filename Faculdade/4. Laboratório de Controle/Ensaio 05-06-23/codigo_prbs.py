#%% Bibliotecas

import numpy as np
import matplotlib.pyplot as plt            # noqa: F401
import time as t
from scipy.signal import square, sawtooth  # noqa: F401
import serial

#%% Parâmetros do Sistema

amplitude_maxima = 15
Ts = 0.02
fre = 0.5
Amplitude = 1
# nivel_dc_saida = 3.53
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

toc = np.zeros(numAmostras)
y = np.zeros(numAmostras)

#%% Conexão com Arduino

print('\nEstabelecendo conexão.')
conexao = serial.Serial(port='COM5', baudrate=9600, timeout=0.005)

t.sleep(1)
print('\nIniciando coleta.')

#%% Loop de Controle

for n in range(numAmostras):
    tic = t.time()

    if (conexao.inWaiting() > 0):

        y[n] = conexao.readline().decode()
           
    u = (r[n]*255)/15
    conexao.write(str(round(u)).encode())
    
    t.sleep(Ts)
    
    if (n > 0):
        tempo[n] = tempo[n-1] + Ts
    toc[n] = t.time() - tic
conexao.write('0'.encode())
print('\nFim da coleta.')
conexao.close()
print('media=',np.mean(r))

#%% Outros

print('media=',np.mean(r))

print('\nPeríodo real:', np.mean(toc))
print('Nivel_DC:', np.mean(y[tempo>2]))

plt.figure(figsize=(10, 15))

plt.subplot(311)
plt.plot(tempo, r, '-b', linewidth=1.2)
plt.xlabel('Tempo(s)')
plt.ylabel('Tensão (V)')
plt.grid()
plt.title('Onda Quadrada - Malha Aberta')
plt.legend(loc='lower right', labels=('Sinal de Entrada', 'Sinal de Saída'))

plt.subplot(312)
plt.plot(tempo, y, '-r', linewidth=1.2)
plt.xlabel('Tempo(s)')
plt.ylabel('Tensão (V)')
plt.grid()
plt.title('Tensão de Saída - Malha Aberta')

plt.subplot(313)
plt.plot(tempo, r - np.mean(r), '-b', linewidth=1.2, label='Sinal de Entrada')
plt.plot(tempo, y - np.mean(y), '-r', linewidth=1.2, label='Sinal de Saída')
plt.xlabel('Tempo(s)')
plt.ylabel('Tensão (V)')
plt.grid()
plt.title('Sinais Centrados em 0')
plt.legend(loc='lower right')

plt.tight_layout()
plt.show()

#%% Salva os dados

dados=np.stack((tempo,r,y),axis=-1)

b = np.mean(y)
print('Média do sinal de saída:')
print(b)
c = np.mean(r)
print('Média do sinal de entrada:')
print(c)

# np.savetxt("DADOS_PRBS.csv", dados, delimiter=" ")