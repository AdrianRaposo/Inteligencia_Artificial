import networkx as nx
import pandas as pd
import numpy as np
import math
import json
import os
import csv
from datetime import datetime
from datetime import timedelta

class Alg():
    
    
    def __init__(self, origen, destino, criterio,dia,hora):
        self.criterio= criterio
        self.origen = origen
        self.destino = destino
        self.estacionActual = origen
        self.principal = 0
        self.secundario = 0
        self.dia = dia
        self.hora = hora
        self.frecuencia = 0
        self.horarios = []
        self.initGraph()
        self.lineasMetro=[]
        self.initLineas()
        self.initHorarios()
        self.listaAbierta = []
        self.listaCerrada = []
        self.recorrido = []
        self.lineas = []
        self.line = []
        self.tiemposEspera = []
        self.transbordos = []
    
    def initLineas(self):
        with open('lineas.csv', newline='') as File:
            reader = csv.reader(File,delimiter=';') # Abrimos y leemos el fichero que contiene las coordenadas
            for row in reader :
                self.lineasMetro.append(row)

    def time_in_range(self,start, end, x):
        if start <= end:
            return start <= x <= end
        else:
            return start <= x or x <= end
    def initFrecuencia(self,estacion,horaES):
        #linea = self.G.nodes[estacion]['Linea']
        linea = self.line[self.recorrido.index(estacion)+1]
        for x in self.horarios[linea-1][self.dia-1]:
            if self.time_in_range(datetime.strptime(x[0],"%H:%M"),datetime.strptime(x[1],"%H:%M"),horaES):
                contSuma=0
                for y in range(len(self.lineasMetro[linea-1])):
                    if(self.lineasMetro[linea-1][y]==estacion):
                        break
                    else:
                        contSuma+= self.G.edges[self.lineasMetro[linea-1][y],self.lineasMetro[linea-1][y+1]]['TIEMPO']
                self.horainicio = datetime.strptime(x[0],"%H:%M") + timedelta(0,contSuma*60)
                #ESTO FALTA  
                self.frecuencia = round(x[2])
                break
    
    def tiempoEspera(self,hora1, hora2):
        h1 = hora1
        h2 = hora2
        fr = timedelta(0,self.frecuencia*60)
        if(h1<=h2):
            resta = h2-h1
            return (resta.seconds)/60
        else:
            resta = h1-h2
        while(resta>=fr):
            h2 = h2 + timedelta(0,self.frecuencia*60)
            resta = h1-h2
        self.horaSalida = h1 +  timedelta(0,(self.frecuencia-((resta.seconds)/60)))
        return self.frecuencia-((resta.seconds)/60)

        
    def initHorarios(self):
        for i in range(3) :
            self.horarios.append([])
            for j in range(4):
                self.horarios[i].append([])
        timetable =self.leer(os.path.abspath("Horarios.json"))
        for x in timetable:
            self.horarios[x['Line']-1][x['Dia']-1].append([x['HorarioInicio'],x['HorarioFinal'],x['Frecuencia']])

    def getRecorrido(self):
        return self.recorrido
    
    def getLineas(self):
        for x in self.recorrido:
            self.lineas.append(self.G.nodes[x]['Linea'])
        return self.lineas
    
    def transbordosAux(self):
        transbordosAux = []
        with open('transbordos.csv', newline='') as File:  
            reader = csv.reader(File,delimiter=';')
            for row in reader :
                transbordosAux.append(row)
        return transbordosAux
    
    def getTransbordos(self):
        transbordos = []
        transbordosAux = self.transbordosAux()
        for x in range (len(self.lineas)):
            if self.lineas[x] == 0:
                if x > 0 and self.lineas[x-1] == 0:
                    for y in transbordosAux:
                        if self.recorrido[x-1] == y[0] and self.recorrido[x] == y[1]:
                            self.line.append((int)(y[2]))
                elif x > 0 and self.lineas[x-1] != 0:
                    self.line.append(self.lineas[x-1])          
                else:
                    if self.lineas[x+1] == 0:
                        for y in transbordosAux:
                            if self.recorrido[x+1] == y[0] and self.recorrido[x] == y[1]:
                                self.line.append((int)(y[2]))
                    else:
                        self.line.append(self.lineas[x+1])
            else:
                self.line.append(self.lineas[x])
        for x in range(len(self.line)-1):
                if(self.line[x]!=self.line[x+1]):
                    transbordos.append(self.recorrido[x])         
        return transbordos

    def algoritmo(self):
        sucesores = []
        solucionEncontrada = False
        self.listaAbierta.append(self.estacionActual)
        self.G.nodes[self.estacionActual]['F']=self.fheuristica(self.estacionActual)
        self.G.nodes[self.estacionActual]['G']=0
        self.G.nodes[self.estacionActual]['Padre']=None
        self.lineaAct= []
        while(solucionEncontrada == False):
            if(len(self.listaAbierta)<0):
                print("Error.")
                return
            self.estacionActual= self.valFMin()

            if self.G.nodes[self.estacionActual]['Linea'] != 0 or self.G.nodes[self.estacionActual]['Padre'] == None:
                self.lineaAct.append(self.G.nodes[self.estacionActual]['Linea'])
            elif self.G.nodes[self.estacionActual]['Linea'] == 0 and self.G.nodes[self.G.nodes[self.estacionActual]['Padre']]['Linea'] == 0:
                transbordosAux = self.transbordosAux()
                for y in transbordosAux:
                        if self.G.nodes[self.estacionActual]['Padre'] == y[0] and self.estacionActual == y[1]:
                            self.lineaAct.append(y[2]) 
            else:
                self.lineaAct.append(self.G.nodes[self.G.nodes[self.estacionActual]['Padre']]['Linea'])
            self.listaCerrada.append(self.estacionActual)

            self.listaAbierta.remove(self.estacionActual)
            if(self.estacionActual == self.destino ):
                solucionEncontrada =  True
            else:
                sucesores = self.hijos(self.estacionActual)
                for n in sucesores:
                    self.tratarHijo(n,self.estacionActual)
                         
    def penalizacion(self, hijo, padre): 
        if self.criterio== "DISTANCIA" or self.lineaAct[self.listaCerrada.index(padre)-1] == 0:
            return 0
        else:
            linea = 0
            if(self.G.nodes[hijo]['Linea']==0 and self.G.nodes[padre]['Linea']==0):
                transbordosAux = self.transbordosAux()
                for y in transbordosAux:
                        if padre == y[0] and hijo == y[1]:
                            linea= y[2]
            else:
                if(self.G.nodes[hijo]['Linea']==0 and self.G.nodes[padre]['Linea']!=0):
                    linea = self.G.nodes[padre]['Linea']
                else:
                    linea = self.G.nodes[hijo]['Linea']
            if (int)(linea) != (int)(self.lineaAct[self.listaCerrada.index(padre)]):
                return 5
            else :
                return 0

                

    def tratarHijo(self, hijo, padre):
        penalizacion = self.penalizacion(hijo, padre)
        if((hijo in self.listaCerrada)== False):
            if((hijo in self.listaAbierta)== True):
                if(self.G.nodes[hijo]['G'] > (self.G.nodes[padre]['G'] + self.G.edges[hijo,padre][self.criterio]) + penalizacion):
                   self.G.nodes[hijo]['G'] = self.G.nodes[padre]['G'] + self.G.edges[hijo,padre][self.criterio] + penalizacion
                   self.calF(hijo)
                   self.G.nodes[hijo]['Padre']= padre
            else:
                self.listaAbierta.append(hijo)
                self.G.nodes[hijo]['G'] = self.G.nodes[padre]['G'] + self.G.edges[hijo,padre][self.criterio] + penalizacion
                self.calF(hijo)
                self.G.nodes[hijo]['Padre']= padre

    def initGraph(self):
        data = pd.read_csv(os.path.abspath("metro.csv"), sep=';', index_col=False, encoding='cp1252')

        self.G = nx.from_pandas_edgelist(data, source='ORIGEN', target='DESTINO', edge_attr=['DISTANCIA', 'TIEMPO'])

        coords = self.leer(os.path.abspath("Coordenadas.json"))
        for x in coords:
            self.G.nodes[x['Station']]['Coordenadas'] = [x['Latitude'], x['Longitude']]
            self.G.nodes[x['Station']]['Linea'] = x['Line']

    def fheuristica(self, estacion) -> int:
        
        lon1 = np.radians(self.G.nodes[estacion]['Coordenadas'][0])
        lat1 = np.radians(self.G.nodes[estacion]['Coordenadas'][1])
        lon2 = np.radians(self.G.nodes[self.destino]['Coordenadas'][0])
        lat2 = np.radians(self.G.nodes[self.destino]['Coordenadas'][1])
        #radio de la tierra
        r = 6371
        difLat = lat2 - lat1
        difLong = lon2 - lon1
        a = np.sin(difLat/2) ** 2 + np.cos(lat2) * np.cos(lat1) * np.sin(difLong/2) ** 2
        c = 2 * np.arctan2(math.sqrt(a), math.sqrt(1-a))
        if(self.criterio == 'DISTANCIA'):
            return c*r
        elif (self.criterio == 'TIEMPO'):
            return (c*r)/1.3 #Velocidad media metro de atenas
    
    def calF(self, estacion):
        self.G.nodes[estacion]['F'] = self.G.nodes[estacion]['G'] + self.fheuristica(estacion)


    def valFMin(self):
        minValor=float("inf")
        estacion=None
        for n in self.listaAbierta:
            if(self.G.nodes[n]['F']<minValor):
                minValor=self.G.nodes[n]['F']
                estacion=n; 
        return estacion


    def hijos(self, padre):
        sucesores=[]
        for n in nx.neighbors(self.G,padre):
            sucesores.append(n)
        return sucesores

    def camino(self):
        aux=self.listaCerrada.index(self.estacionActual)
        estacion = self.listaCerrada[aux]
        self.recorrido.insert(0,estacion)
        self.principal = round(self.G.nodes[estacion]['G'],4)
        while(self.G.nodes[estacion]['Padre'] != None):
            self.recorrido.insert(0,self.G.nodes[estacion]['Padre'])
            estacion = self.G.nodes[estacion]['Padre']
       
    def otrosCriterios(self):
        x=1
        if(self.criterio == 'TIEMPO'):
            while(x <len(self.recorrido)):
                self.secundario += self.G.edges[self.recorrido[x-1],self.recorrido[x]]['DISTANCIA']
                self.secundario = round(self.secundario,4) 
                x += 1
        else:
             while(x <len(self.recorrido)):
                self.secundario += self.G.edges[self.recorrido[x-1],self.recorrido[x]]['TIEMPO'] 
                x += 1
            
    def leer(self, data):
                with open (data, 'r') as f:
                    estructura = json.load(f)
                    f.close()
                return estructura
    
    def calcularTiempo(self):
        self.getLineas()
        self.transbordos = self.getTransbordos()
        self.initFrecuencia(self.origen,self.hora)
        self.principal = self.principal + self.tiempoEspera(self.hora,self.horainicio)
        self.tiemposEspera.append(self.tiempoEspera(self.hora,self.horainicio))
        for x in self.transbordos:
            self.initFrecuencia(x,self.horaSalida +timedelta(0,self.G.nodes[x]['G']*60))
            suma= round(self.tiempoEspera(self.horaSalida +timedelta(0,self.G.nodes[x]['G']*60),self.horainicio))
            self.principal = self.principal + suma
            self.tiemposEspera.append(suma)
              
        self.principal -= len(self.transbordos)*5
    
        
    def main(self):

        self.algoritmo()
        self.camino()   
        self.otrosCriterios()
        if(self.criterio=='TIEMPO'):
            self.calcularTiempo()