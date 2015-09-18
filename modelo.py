#!/usr/bin/python

import sys
import random
import math
from graph_tool.all import *

ADICIONA_VERTICE = 0
ADICIONA_ARESTAS = 1
ESTRATEGIA_PROATIVA = 2
ATUALIZA_LISTA = 3

if len(sys.argv) < 6:
 sys.exit(1)

# Estrategia utilizada para a gerencia de vizinhanca
# 0: inativa
# 1: preemptiva
# 2: proativa
estrategia = int(sys.argv[1])

# Tamanho da rede considerada
tamanho_rede = int(sys.argv[2])

# Funcao que define a entrada de pares no sistem
# 0: constante
# 1: flash crowd
# 2: popularizacao
entrada_pares = int(sys.argv[3])

# Periodo de tempo no qual os pares entraram no sistema
#tempo_maximo_entrada = int(sys.argv[4])

# Numero maximo de vizinhos (ou conexoes) que qualquer pode ter
#max_vizinhanca = int(sys.argv[4])
max_vizinhanca = 80 

# Porcentagem de pares que aceitam conexoes
pares_alcancaveis = float(sys.argv[4])

# Semente utilizada para gerar os numeros randomicos
semente = int(sys.argv[5])

# Numero de conexoes do conjunto de possiveis arestas adicionadas ao grafo a cada instante de tempo
conexoes_adicionadas = 10

# Periodo no qual o par obtem uma nova lista de pares (visao do sistema) e atualiza o conjunto de possiveis conexoes
intervalo_atualizacao_lista = 150

# Fila de eventos para ser processado
fila_eventos = {}

# Conjunto de vertices (pares) da rede
pares = []
# Conjunto de arestas (conexores) da rede
conexoes = []

# Conexoes estabelecidas no instante de tempo atual
conexoes_novas = []

# Tamanho atual da rede
tamanho_atual_rede = 0

# Conjunto de possiveis conexoes a serem adicionadas ao grafo
possiveis_conexoes = []

alcancabilidade = []

# Tamanho da vizinhanca de cada um dos pares
vizinhanca = {}

vizinhos = {}

# Instante t da simulacao
timestep = 0

# Tempo maximo da simulacao
max_timestep = 200

intervalo_proativo = 50

remover_proativa = 1

entrada = {}

def configura_experimento():
 # Inicia o gerador randomico
 random.seed(semente)
 
 # Gera a alcancabilidade dos pares
 global alcancabilidade
 alcancabilidade += ((int) (pares_alcancaveis*tamanho_rede)) * [1]
 alcancabilidade += ((int) ((1-pares_alcancaveis)*tamanho_rede)) * [0]
 random.shuffle(alcancabilidade)
 alcancabilidade.insert(0, 1)
 
 # Gera a taxa de entrada dos pares
 tempo = 0
 for vertice in range(tamanho_rede):
  if entrada_pares == 0:
#   tempo += (max(1, tempo_maximo_entrada/tamanho_rede))
    tempo += 5
  elif entrada_pares == 1:
   tempo += (int) (max(1, math.exp(vertice/(tamanho_rede/3.0))))
  elif entrada_pares == 2:
   tempo += (int) (max(1, (tamanho_rede/4)*math.exp(-vertice/(tamanho_rede/8))))
  entrada[vertice] = tempo
  adiciona_evento(tempo, (ADICIONA_VERTICE, vertice))
  if estrategia == 2:
   adiciona_evento(tempo+intervalo_proativo, (ESTRATEGIA_PROATIVA, vertice))
 
 # Gera evento de adicao de arestas
 adiciona_evento(entrada[min(entrada)], (ADICIONA_ARESTAS, conexoes_adicionadas))
# print entrada[max(entrada)]

# Adiciona um evento de um determinado tipo com o timestamp tempo
def adiciona_evento(tempo, tipo):
 if tempo not in fila_eventos:
  fila_eventos[tempo] = []
 fila_eventos[tempo].append(tipo)

# Configura a entrada de um par na rede, realizando o setup de configuracoes 
def entrada_par(nodo):
 global tamanho_atual_rede
 pares.append(nodo)
 vizinhanca[nodo] = 0
 vizinhos[nodo] = []
 tamanho_atual_rede += 1
 if estrategia == 1:
  gera_possiveis_conexoes_preemptiva(nodo)
 else:
  gera_possiveis_conexoes(nodo)

# Atualiza o conjunto de possiveis conexoes com as informacoes do nodo
def gera_possiveis_conexoes(nodo):
 if vizinhanca[nodo] < max_vizinhanca:
  for vertice in pares:
   if vizinhanca[vertice] < max_vizinhanca and vertice != nodo and alcancabilidade[vertice] == 1 and (nodo, vertice) not in conexoes and (vertice, nodo) not in conexoes:
    possiveis_conexoes.append((nodo, vertice))
 tempo = timestep + intervalo_atualizacao_lista
 adiciona_evento(tempo, (ATUALIZA_LISTA, nodo))

# Adiciona um determinado numero de conexoes ao grafo
def adiciona_conexoes(conexoes_adicionadas):
 if len(possiveis_conexoes) > 0:
  conexoes_novas = []
  for conexao in range(min(len(possiveis_conexoes), conexoes_adicionadas)):
   try:
    origem, destino = random.choice(possiveis_conexoes)
    conexoes.append((origem, destino))
    vizinhos[origem].append(destino)
    vizinhos[destino].append(origem)
    conexoes_novas.append((origem, destino))
    possiveis_conexoes.remove((origem, destino))
    if (destino, origem) in possiveis_conexoes:
     possiveis_conexoes.remove((destino, origem))
    vizinhanca[origem] += 1
    vizinhanca[destino] += 1
    if estrategia == 1:
     verifica_possiveis_conexoes_preemptiva(origem)
     verifica_possiveis_conexoes_preemptiva(destino)
    else:
     verifica_possiveis_conexoes(origem)
     verifica_possiveis_conexoes(destino)
   except:
    continue
 tempo = timestep + 1
 adiciona_evento(tempo, (ADICIONA_ARESTAS, conexoes_adicionadas))

# Verifica se algum par nao pode mais receber conexoes
def verifica_possiveis_conexoes(nodo):
 if vizinhanca[nodo] >= max_vizinhanca:
  for origem, destino in possiveis_conexoes:
   if origem == nodo or destino == nodo:
    possiveis_conexoes.remove((origem, destino))

# Remove um determinado numero de vizinhos do nodo
def remove_vizinhos(nodo, numero_removidas):
 for indice in range(numero_removidas):
  destino = random.choice(vizinhos[nodo])
  #print nodo, destino, conexoes
  if (nodo, destino) in conexoes:
   conexoes.remove((nodo, destino))
  else:
   conexoes.remove((destino, nodo))
  vizinhos[nodo].remove(destino)
  vizinhos[destino].remove(nodo)
  vizinhanca[nodo] -= 1
  vizinhanca[destino] -= 1

# ESTRATEGIA PREEMPTIVA
def gera_possiveis_conexoes_preemptiva(nodo):
 if vizinhanca[nodo] < max_vizinhanca:
  for vertice in pares:
   if vertice != nodo and alcancabilidade[vertice] == 1 and (nodo, vertice) not in conexoes and (vertice, nodo) not in conexoes:
    possiveis_conexoes.append((nodo, vertice))
 tempo = timestep + intervalo_atualizacao_lista
 adiciona_evento(tempo, (ATUALIZA_LISTA, nodo))
 
# Verifica se algum par nao pode mais receber conexoes
def verifica_possiveis_conexoes_preemptiva(nodo):
 if vizinhanca[nodo] >= max_vizinhanca:
  for origem, destino in possiveis_conexoes:
   if origem == nodo:
    possiveis_conexoes.remove((origem, destino))

# Estrategia preemptiva de gerenciar conexoes. Faz a verificacao e poda do excesso de vizinhos
def verifica_consistencia():
 for vertice in pares:
  if vizinhanca[vertice] > max_vizinhanca:
   remove_vizinhos(vertice, vizinhanca[vertice] - max_vizinhanca) 

# ESTRATEGIA PROATIVA
def estrategia_proativa(nodo):
 if vizinhanca[nodo] == max_vizinhanca:
  remove_vizinhos(nodo, remover_proativa)
   #gera_possiveis_conexoes(vertice, False)
 tempo = timestep+intervalo_proativo
 adiciona_evento(tempo, (ESTRATEGIA_PROATIVA, nodo))
   
# Main loop
configura_experimento()
while True:
 # Procura o proximo evento
 timestep = min(fila_eventos)
 if timestep > entrada[max(entrada)] + max_timestep:
  break
 eventos = fila_eventos[timestep]
# print timestep, entrada[max(entrada)] + max_timestep
 
 # Trata ele
 for evento, parametro in eventos:
  if evento == ADICIONA_VERTICE:
   entrada_par(parametro)
  elif evento == ADICIONA_ARESTAS:
   adiciona_conexoes(parametro)
   verifica_consistencia()
  elif evento == ESTRATEGIA_PROATIVA:
   estrategia_proativa(parametro)
  elif evento == ATUALIZA_LISTA:
   gera_possiveis_conexoes(parametro)   
 
 # Apaga o evento
 del fila_eventos[timestep]
 
descritor = "CORRIGIDO_Modelo-Estrategia=" + str(estrategia) + "-N=" + str(tamanho_rede) + "-Entrada=" + str(entrada_pares) + "-Viz=" + str(max_vizinhanca) + "-R=" + str(pares_alcancaveis) + "-S=" + str(semente)

arq = open(descritor + ".dat", "w")
for origem, destino in conexoes:
 arq.write(str(origem) + "\t" + str(destino) + "\n")
 arq.write(str(destino) + "\t" + str(origem) + "\n")
arq.close()

arq = open(descritor + ".plt", "w")
arq.write('''set encoding iso_8859_1
set terminal postscript eps enhanced color butt "Helvetica" 20
set grid layerdefault
set grid xtics
set grid ytics
set xrange [0:*]
set yrange [0:*]
set ylabel "Par #"
set xlabel "Par #"
set output "%s.eps"
set style data l

plot "%s.dat" notitle with p''' %(descritor, descritor))
arq.close()

#arq = open(descritor + "_entrada.dat", "w")
#for tempo_entrada_par in entrada:
# arq.write(str(tempo_entrada_par) + "\t" + str(entrada[tempo_entrada_par]) + "\n")
#arq.close()

#arq = open(descritor + "_entrada.plt", "w")
#arq.write('''set encoding iso_8859_1
#set terminal postscript eps enhanced color butt "Helvetica" 20
#set grid layerdefault
#set grid xtics
#set grid ytics
#set xrange [0:*]
#set yrange [0:*]
#set ylabel "Tempo (minutos)"
#set xlabel "Par #"
#set output "%s_entrada.eps"
#set style data l

#plot "%s_entrada.dat" notitle with p''' %(descritor, descritor))
#arq.close()

def build_graph():
 g = Graph(directed=False)
 vert = {}
 for origem, destino in conexoes:
  if origem not in vert:
   vert[origem] = g.add_vertex()
  if destino not in vert:
   vert[destino] = g.add_vertex()
  g.add_edge(vert[origem], vert[destino])
 g.save(descritor + ".xml.gz")

build_graph()

print "Finished"
