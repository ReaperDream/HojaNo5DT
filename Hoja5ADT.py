# -*- coding: utf-8 -*-
from SimPy.Simulation import *
import random
from SimPy.Lib import Process, SimEvent, FIFO, PriorityQ, Resource, Level, Store
import simpy


RANDOM_SEED = 42 #Generación de numeros al azar
Mram = 100 #Cantidad de ram que va a ser utilizada
instTiempo = 3 #Numero de instrucciones que realizara el CPU
procesos = 50 #Procesos que van a ser realizados
tiempototal = 0.0 #Cantidad de tiempo total


class EV(Process):
	def __init__(self,env,numeroProceso):
		Process.__init__(self)
		self.env = env
		self.numeroProceso = numeroProceso
		self.New_pro = env.process(self.New(env,numeroProceso))

	def New(self,env,numeroProceso):
		#New

		self.inicio = env.now
		intervalo = 10
		creacion_pro  = random.expovariate(1.0 / intervalo)
		num_memoria = random.randint(1,10)#Se genera aleatoriamente la cantidad de memoria que uilizara un proceso
		yield env.timeout(creacion_pro)
		print("%s necesita %d mb de ram") % (numeroProceso,num_memoria)

		
		if(ram < num_memoria): 
			yield env.timeout(num_memoria)
			print("%s en espera, no hay suficiente memoria disponible para continuar")
		else:
			yield ram.get(num_memoria)
			print("%s ha obtenido la cantidad de %d mb de memoria RAM") % (numeroProceso,num_memoria)
			env.process(self.Ready(env,numeroProceso,num_memoria))

	def Ready(self,env,numeroProceso,num_memoria):
		#Ready
		inst_ter= 0 #Instrucciones terminadas
		num_inst = random.randint(1,10) #numero de instrucciones que va a tener cada proceso
		#mientras el numero de instrucciones sea menor a las instrucciones terminadas
		while num_inst > inst_ter:
			with CPU.request() as request:
				yield request
				#si la resta de el numero instrucciones generado con el numero de intrucciones terminadas, es mayor a al tiempo de proceso de instrucciones del cpu
				if (num_inst-inst_ter) >= instTiempo:
					#entonces se mantiene la velocidad
					vel = instTiempo
				else:
					vel=(num_inst-inst_ter)

			print("%s el cpu ejecutara  %d instrucciones" % (numeroProceso, vel))
			yield env.timeout(vel/instTiempo)   

			inst_ter += vel
			print("%s CPU trabajando, instrucciones realizadas %d de %d " % (numeroProceso, inst_ter, num_inst))
		env.process(self.Wait(env,numeroProceso,inst_ter,num_inst,num_memoria))
	#Wait
	def Wait(self,env,numeroProceso,inst_ter,num_inst,num_memoria):
		#Se genera al azar la desisción si el cpu va a seguir trabajando en ese proceso o va a seguir con el siguiente
		desicion = random.randint(1,2)
		if desicion == 1 and inst_ter<num_inst:
			with wait.request() as request:
				yield request
        		yield env.timeout(1) 
        		print("%s. Realizan operaciones de entrada/salida" % (numeroProceso))
        	env.process(self.Terminated(env,num_memoria,numeroProceso))
    #Terminated
	def Terminated(self,env,num_memoria,numeroProceso):
		#Finaliza el proceso, y se muestra en pantalla el numero de proceso y la cantidad de ram que utilizo
		yield ram.put(num_memoria)
		print("%s retorna %d mb de RAM, ha finalizado" % (numeroProceso, num_memoria))
		global tiempototal
		tiempototal += env.now - self.inicio	




#Se inicializa el ambiente de simulación
env = simpy.Environment()
CPU = simpy.Resource(env,capacity=1)#Resource utilizado para la cantidad de CPU que van a ser utilizados
ram = simpy.Container(env, init=Mram,capacity=Mram)#Tipo container utilizado para inizializar el total de ram y la capacidad
wait = simpy.Resource(env,capacity=1)# Cantidad de tiempo que se esperara para las opercaiones



#Random
random.seed(RANDOM_SEED)

#Se generan los procesos que se van a utilizar
for i in range(procesos):
	ev = EV(env,"Proceso numero:  %d" % i) 
	activate(ev,ev.New(env,"Proceso numero:  %d" % i)) #Se genera el proceso

#Se inicializa la simulación
env.run()

#tiempo promedio, en realizar todos los procesos
promedio=(tiempototal/procesos)
print("El tiempo promedio de los procesos es: %f s") % (promedio)
