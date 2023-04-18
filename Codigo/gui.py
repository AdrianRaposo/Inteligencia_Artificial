from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import Image
from PIL import ImageTk
import csv
from Algoritmo import Alg
from datetime import datetime
from datetime import timedelta
import time as tm

def progresoBarra():
    global contaador, al,progress
    progress.set(round((contaador/(len(al.recorrido)-1))*100)) #Actualizamos progreso 

def comboChangedOrigen(event):
    seleccion.set(0)
    origenDestino(variable1.get()) #Actualizamos valor origen
    
def comboChangedDestino(event):
    seleccion.set(1)
    origenDestino(variable2.get()) #Actualizamos valor destino

def esTransbordo(estacion):
    for n in transbordos:
        if n == estacion:
            return True
    return False #Indicamos si la estacion es un transbordo en el recorrido obtenido

def getCoords(estacion):
    coordsestacion = [] #Coordenadas estacion respecto de la imagen
    for i in coords:
        if i[0] == estacion:
            coordsestacion.append((int)(i[1]))
            coordsestacion.append((int)(i[2])) #Busacamos y almacenamos las coordenadas
    return coordsestacion 

def origenDestino (estacion):
    global origenCambiado, destinoCambiado, coordOrigen, coordDestino,tren ,imgTren, bandera, imgBand
    
    if(seleccion.get() == 0) : #Se cambia el origen
        if(origenCambiado == True): #Se comprueba que se haya cambiado anteriormente
            for i in range(54):
                if btns[i][0] == origen.get():
                    btns[i][1].place(x=coordOrigen[0]-4,y=coordOrigen[1]-4) #Se vuelve a colocar el boton del antiguo origen
        origen.set(estacion) #Cambiamos el origen
        seleccion.set(1) #Indicamos que el proximo en cambiar será destino
        lista = getCoords(estacion) #Guardamos la coords del Origen
        coordOrigen=lista
        tren.config(image=imgTren, borderwidth=0,relief="flat")
        tren.image = imgTren
        tren.place(x=lista[0]-10, y=lista[1]-10) #Sustituimos el boton por un tren
        for i in range(54):
            if btns[i][0] == estacion:
                btns[i][1].place_forget() #olvidamos temporalmente el boton
                comboOrigen.current(i+1)
        origenCambiado=True  #Indicamos que el origen se ha cambiado
    else: #Se cambia el destino
        if(destinoCambiado == True): #Se comprueba que se haya cambiado anteriormente
            for i in range(54):
                if btns[i][0] == destino.get():
                    btns[i][1].place(x=coordDestino[0]-4,y=coordDestino[1]-4) #Se vuelve a colocar el boton del antiguo destino
        destino.set(estacion) #Cambiamos el destino
        seleccion.set(0) #Indicamos que el proximo en cambiar será origen
        lista = getCoords(estacion) #Guardamos la coords del Origen
        coordDestino= lista
        bandera.config(image=imgBand, borderwidth=0,relief="flat")
        bandera.image = imgBand
        bandera.place(x=lista[0]-10, y=lista[1]-10)#Sustituimos el boton por una bandera
        for i in range(54):
            if btns[i][0] == estacion:
                btns[i][1].place_forget()
                comboDestino.current(i+1) #Olvidamos temporalmente el boton
        destinoCambiado=True #Indicamos que el destino se ha cambiado

def getHorario(line, wind): #imprimir ventana de los horarios dependiendo de la linea
    
    if line == 1:
        window = Toplevel(wind, width=1362, height=521)
    elif line == 2:
        window = Toplevel(wind, width=1083, height=797)
    else:
        window = Toplevel(wind, width=1087, height=792)    
    frame = Frame(window, background='white')
    horarios = ImageTk.PhotoImage(Image.open('linea' + str(line) + '.png'))
    make_label(frame, horarios)
    frame.pack()
    
    window.mainloop()

def showPath(): #Función recursiva para dibujar el camino
    global contLineas, al, canvas, coordsExtra, frameInfo, listbox, contaador,progreso,transbordos,lineasUsadas,start
    if(start == True):
        return #Si se ha pulsado una vez el boton no hace nada más
    if al.recorrido[contLineas] == destino.get(): 
        contLineas = 0
        destino.set("---Seleccionar Destino---") 
        origen.set("---Seleccionar Origen---") #Reseteamos origen y destino
        fin = Label(frameInfo, text="¡Buen Viaje!", background="black", font=("Copperplate Gothic Bold", 20))
        fin.configure(fg="white")
        fin.place(x=55, y=670)
        listbox.insert(contaador, al.recorrido[contaador])# Añadimos la ultima estación del recorrido
        start=True #Indicamos que la funcion recursiva ha acabado
        return
    else:
        #Dibujamos tramo a tramo
        coordIn = getCoords(al.recorrido[contLineas]) # Coords nodo inicial del tramo
        coordFin = getCoords(al.recorrido[contLineas+1])# Coords nodo final del tramo
        listaAux = []
        listaAux.append(coordIn) 
        
        for i in coordsExtra:
            if(i[0] == al.recorrido[contLineas] and i[1] == al.recorrido[contLineas+1]):
                listaAux.append(i[2])    
        listaAux.append(coordFin)#Comprobamos si necesitamos coordenadas adicionales para dibujar el tramo
        
        for j in range(len(listaAux)-1):
            coord1 = listaAux[j]
            coord2 = listaAux[j+1]
            canvas.create_line(coord1[0], coord1[1], coord2[0], coord2[1], fill="black", width=12)
            canvas.create_line(coord1[0], coord1[1], coord2[0], coord2[1], fill="gray", width=7) #Dibujamos el tramo 
       
        canvas.create_oval(coordIn[0]-10, coordIn[1]-10, coordIn[0]+10, coordIn[1]+10, fill="black") #Contorno del punto
        
        if esTransbordo(al.recorrido[contLineas]) == True : #Si en la estacion se hace trasbordo pintamos el punto del color de la linea que se hace el trasbordo
            if lineasUsadas[contLineas+1]==1:
                canvas.create_oval(coordIn[0]-8, coordIn[1]-8, coordIn[0]+8, coordIn[1]+8, fill="green") #Linea 1
            elif lineasUsadas[contLineas+1]==2:
                canvas.create_oval(coordIn[0]-8, coordIn[1]-8, coordIn[0]+8, coordIn[1]+8, fill="red") #Linea32
            else:
                canvas.create_oval(coordIn[0]-8, coordIn[1]-8, coordIn[0]+8, coordIn[1]+8, fill="blue") #Linea 3
        else:
            if lineasUsadas[contLineas]==1:
                canvas.create_oval(coordIn[0]-8, coordIn[1]-8, coordIn[0]+8, coordIn[1]+8, fill="green") #Linea 1
            elif lineasUsadas[contLineas]==2:
                canvas.create_oval(coordIn[0]-8, coordIn[1]-8, coordIn[0]+8, coordIn[1]+8, fill="red") #Linea 2
            else:
                canvas.create_oval(coordIn[0]-8, coordIn[1]-8, coordIn[0]+8, coordIn[1]+8, fill="blue") #Linea 3
        
        listbox.insert(contaador, al.recorrido[contaador]) #añadimos estacion al recorrido
        contaador += 1
        contLineas += 1
        progreso.bind(progresoBarra()) #Avanzamos el progreso de la barra
        canvas.after(300, showPath)
        canvas.create_oval(coordFin[0]-10, coordFin[1]-10, coordFin[0]+10, coordFin[1]+10, fill="black")
        if lineasUsadas[contLineas]==1:
                canvas.create_oval(coordFin[0]-8, coordFin[1]-8, coordFin[0]+8, coordFin[1]+8, fill="green") #Linea 1
        elif lineasUsadas[contLineas]==2:
                canvas.create_oval(coordFin[0]-8, coordFin[1]-8, coordFin[0]+8, coordFin[1]+8, fill="red") #Linea2
        else:
                canvas.create_oval(coordFin[0]-8, coordFin[1]-8,coordFin[0]+8, coordFin[1]+8, fill="blue")#Linea3
    
def newWindow():
    global al, canvas, matriz, coordsExtra, criterio, frameInfo, listbox, contaador,progreso,progress,transbordos,lineasUsadas,start
    start = False
    
    if(origen.get() == "---Seleccionar Origen---" or destino.get()== "---Seleccionar Destino---"): #Se comprueba que se hayan seleccionado origen y destino
        messagebox.showerror(title="Error", message="No se puede calcular la ruta si alguno de los campos origen o destino esta vacío.") #Mensaje de error
        return
    else:
        lineasAux = [] #array con las lineas del metro
        with open('lineas.csv', newline='') as File:  
            reader = csv.reader(File,delimiter=';') # Abrimos y leemos el fichero que contiene las coordenadas
            for row in reader :
                lineasAux.append(row)
                
        dia = datetime.now().strftime('%A') #dia de la semana para calcular los horarios de los trenes
        hora = tm.strftime('%H:%M') #hora actual para calcular los horarios de los trenes
        horaDate = datetime.strptime(hora, '%H:%M')
        if dia == "Monday" or dia == "Tuesday" or dia == "Wednesday" or dia == "Thursday": #transformamos el valor de dia a nuestro formato
            dia = 1
        elif dia == "Friday":
            dia = 2
        elif dia == "Saturday":
            dia = 3
        elif dia == "Sunday":
            dia = 4
        else:
            print("Error al obtener el dia")
        
        al = Alg(origen.get(), destino.get(), varOpcion.get(), dia, horaDate) # Llamamos al algoritmo A*
        al.main() #Inicializamos el algoritmo
        camino = al.getRecorrido() #Recorrido  
        if al.criterio == "DISTANCIA":
            al.getLineas() 
            transbordos = al.getTransbordos() #Transbordos
        else:
            transbordos = al.transbordos
        lineasUsadas = al.line #lineas usadas repetidas
        lineasUnicas = set(lineasUsadas) #set de lineas usadas unicas
        lines = [] #lista de lineas usadas unicas
        for numero in lineasUnicas:
            lines.append(numero)
        contaador = 0
        #Creamos nueva ventana y  la configuramos
        newWindow = Toplevel(root, width=1000, height=778)
        newWindow.title("Ruta " + origen.get() + "-" + destino.get())
        newWindow.resizable(FALSE, FALSE)
        #Creamos frame donde aparecerá la ruta
        frameRuta = Frame(newWindow, width=710, height=778, background='white')
        frameRuta.pack_propagate(0)
        frameRuta.pack(side="left")
        #Creamos frame donde aparecerá la información
        frameInfo = Frame(newWindow, width=290, height=778, background='black')
        frameInfo.pack_propagate(0)
        frameInfo.pack(side="right")
        #Widegets frameInfo

        #Barra de progreso de la creación de la ruta
        progreso= ttk.Progressbar(frameInfo,orient='horizontal',length=224,variable=progress)
        progreso.place(x=40,y=255)
        progress.set(0)
        #Label texto
        estaciones = Label(frameInfo, text="Estaciones: ", background="black", font=("Copperplate Gothic Bold", 15))
        estaciones.configure(fg="white")
        estaciones.place(x=80, y=30)
        #Listbox que muestra las estaciones del recorrido
        listbox = Listbox(frameInfo, font=("Copperplate Gothic Bold", 11), background="black")  
        listbox.configure(fg="white")
        listbox.place(x=40, y=80)
        #Boton Start
        boton = Button(frameInfo, height="2", width="12", text="START", font=("Copperplate Gothic Bold", 11), cursor="hand2")
        boton.config(command=lambda:showPath())
        boton.configure(fg="black")
        boton.place(x=80, y=590)
        #Label de texto "criterio" 
        criterioMetro = Label(frameInfo, text="Criterio: " + varOpcion.get(), background="black", font=("Copperplate Gothic Bold", 11))
        criterioMetro.configure(fg="white")
        criterioMetro.place(x=60, y=320)

        #Label de texto "Distacia y tiempo"
        if(varOpcion.get() == "DISTANCIA"):
            valor = Label(frameInfo, text="Distancia(km): " + str(al.principal), background="black", font=("Copperplate Gothic Bold", 11))
        else:
            valor = Label(frameInfo, text="Tiempo(min): " + str(al.principal), background="black", font=("Copperplate Gothic Bold", 11))
            valor2 = Label(frameInfo, text="Distancia(km): " + str(al.secundario), background="black", font=("Copperplate Gothic Bold", 11))
            valor2.place(x=60, y=380)
            valor2.configure(fg="white")
        valor.place(x=60, y=360)
        valor.configure(fg="white")
        
        #Label texto 
        lineas = Label(frameInfo, text="Lineas utilizadas: " + str(lines), background="black", font=("Copperplate Gothic Bold", 11))
        lineas.configure(fg="white")
        lineas.place(x=60, y=340)
        if al.criterio == "TIEMPO":
            esperaTitle = Label(frameInfo, text="Tiempos espera", background="black", font=("Copperplate Gothic Bold", 13))
            esperaTitle.configure(fg="white")
            esperaTitle.place(x=70, y=430)
            espera = Label(frameInfo, text= origen.get() + ": " + str(al.tiemposEspera[0]) + "(min)", background="black", font=("Copperplate Gothic Bold", 11))
            espera.configure(fg="white")
            espera.place(x=40, y=470)
            suma = 20
            for x in range (len(transbordos)):
                esperaAux = Label(frameInfo, text= transbordos[x] + "(min): " + str(al.tiemposEspera[x+1]) + "(min)", background="black", font=("Copperplate Gothic Bold", 11))
                esperaAux.config(fg="white")
                esperaAux.place(x=40, y=470 + suma)
                suma += 20
            horaSalida =Label(frameInfo, text= "Hora salida: " + str(hora) , background="black", font=("Copperplate Gothic Bold", 11))
            horaSalida.configure(fg="white")
            horaSalida.place(x=40, y=530)
            horaLlegada =Label(frameInfo, text= "Hora llegada: " + (horaDate +  timedelta(0,al.principal*60)).strftime("%H:%M"), background="black", font=("Copperplate Gothic Bold", 11))
            horaLlegada.configure(fg="white")
            horaLlegada.place(x=40, y=550)
        #Widgets frameRuta
        #Creamos el lienzo donde se dibujara la ruta
        canvas = Canvas(frameRuta, width=710, height=778, bg='white')
        canvas.pack(anchor='nw', fill='both', expand=1) #Lienzo
        metro = Image.open('metroAtenas.png')
        metro = ImageTk.PhotoImage(metro)
        canvas.create_image(0,0,image=metro,anchor="nw")#Imagen de fondo

        coordsExtra = [] #coordenadas extras par dibujar el recorrido 
        for estacion in range (len(camino)-1):
            for row in matriz:
                if row[0] == camino[estacion] and row[1] == camino[estacion+1]:
                    coordsExtra.append(row) #Alamcenamos las coordenadas necesarias
                             
    coords1 = getCoords(origen.get()) #Cordenadas donde poner el antiguo boton origen
    coords2 = getCoords(destino.get()) #Cordenadas donde poner el antiguo boton destino
    tren.place_forget() #Retiramos el tren de la ventana principal
    bandera.place_forget() #Retiramos la bandera de la ventana principal
    
    for i in range (54):
        
        if btns[i][0] == origen.get():
            btns[i][1].place(x=coords1[0]-5, y=coords1[1]-5)
        if btns[i][0] == destino.get():
            btns[i][1].place(x=coords2[0]-5, y=coords2[1]-5) #Buscamos el origen y el destino y colocamos los botones

    seleccion.set(0) #Restablecemos la seleccion
    comboOrigen.current(0) #Restablecemos el origen
    comboDestino.current(0) #Restabelecemos el destino
    newWindow.mainloop()
    
def make_label(parent, img):
    label = Label(parent, image=img)
    label.pack()
    return label #Creamos label de la imagen sobre el frame parent

def confButt():
    for i in range(len(btns)):
        btns[i][1].config(command= lambda i=i: origenDestino(btns[i][0])) #Configuramos el comando de cada botón

def newHorarios(): #ventana para seleccionar la linea
    window2 = Toplevel(root, width=200, height=200, bg="black")
    window2.title("Horarios")
    window2.resizable(FALSE, FALSE)
    aux = 40
    for num in range (3):
        if num == 0:
            color = "green"
        elif num == 1:
            color = "red"
        else:
            color = "blue"
            
        hor = Button(window2, height="1", width="6", text="Linea " + str(num+1), font=("Copperplate Gothic Bold", 11), cursor="hand2", bg="white", fg = color)
        hor.config(command=lambda num=num:getHorario(num+1, window2))
        hor.place(x=60, y=10 + aux)
        aux += 40
    window2.mainloop()
def on_closing():
    if messagebox.showinfo("","Hasta pronto :)"):
        root.destroy()
#Ventana Principal   
#Generamos y configuramos la ventana
root= Tk()
root.config(bg='white')
root.geometry("1000x778")
root.title("Metro Atenas")
root.resizable(False,False)
root.iconbitmap("icono.ico")
#Generamos y configuramos el frame contrario al del mapa del metro
framePr = Frame (root,width=290, height=778, background='white')
framePr.pack(side = 'left')
imgg = ImageTk.PhotoImage(Image.open('metroAtenass.png'))
make_label(framePr, imgg)
#Generamos y configuramos el frame que tiene la imagen del metro
frameIm = Frame(root, width=710, height=778, background='white') 
frameIm.pack_propagate(0)    
frameIm.pack(side = 'right')

#Generamos los widgets del frameIm
img = ImageTk.PhotoImage(Image.open('metroAtenas.png')) #Imagen del mapa del metro
btns = [] # Lista que guarda los botones de cada estacion
coords = [] #Lista que guarda las coordenadas de cada estación respecto de la imagen
imagen= Image.open('buttonIm.png')
bgrIm = ImageTk.PhotoImage(imagen) #Imagen que usaran los botones
make_label(frameIm, img) # Añadimos la imagen al frame
with open('coordImg.csv', newline='') as File:  
    reader = csv.reader(File,delimiter=';') # Abrimos y leemos el fichero que contiene las coordenadas
    for row in reader :
        btns.append([row[0],Button(frameIm,width =4, height = 4,border=0,image=bgrIm,cursor="hand2")]) #Creamos los botones de cada estación
        btns[len(btns)-1][1].place(x=((int)(row[1])-5),y=((int)(row[2])-5)) #Colocamos los botones en el frame
        coords.append([row[0], row[1], row[2]]) # Guardamos las coordendas en una lista
    confButt() #Configuramos los botones

#Generamos los widgets del framePr

#Variables que usan los widgets
coordsExtra = []
matriz = []
valuesOrigen = []
valuesDestino = []
contLineas = 0
contMatriz = 0
destino = StringVar()
origen = StringVar()
seleccion = IntVar()
progress = IntVar()
varOpcion = StringVar()
variable1 = StringVar()
variable2 = StringVar()
coordOrigen = []
coordDestino = []
origenCambiado=False
destinoCambiado=False

#Botones que se usan para decidir el criterio
varOpcion.set("DISTANCIA") #Se inicializa a uno de ellos
crit = Label(framePr, text="Criterio: ", background="black", font=("Copperplate Gothic Bold", 15), fg="white")
crit.place(x=100, y=270)
Radiobutton(framePr, text="Distancia", font=("Copperplate Gothic Bold", 11), width=8,variable=varOpcion, value="DISTANCIA", bg="white").place(x=95, y=320)#Criterio: Distancia
Radiobutton(framePr, text="Tiempo", font=("Copperplate Gothic Bold", 11), width=8,variable=varOpcion, value="TIEMPO", bg="white").place(x=95, y=370)#Criterio: Tiempo

# Botones que abrirán nuevas ventanas
Button(framePr ,text = "Calcular Ruta",width=20, height=2,relief="solid",borderwidth = 1,font=("Copperplate Gothic Bold", 11), bg="black", fg="white", cursor="hand2",command= lambda: newWindow() ).place(x=30, y=570)
Button(framePr ,text = "Consultar Horarios",width=20, height=1,relief="solid",borderwidth = 1,font=("Copperplate Gothic Bold", 11), bg="green", cursor="hand2",command= lambda: newHorarios(), fg="white").place(x=30, y=480)
#ComboBox que indicarán la selección del origen y del destino
valuesOrigen.append("---Seleccionar Origen---")
valuesDestino.append("---Seleccionar Destino---")
for i in range (54):
    valuesOrigen.append(btns[i][0])
    valuesDestino.append(btns[i][0]) #Añadimos los valores que tendrán las comboBox 
comboOrigen= ttk.Combobox(framePr, textvariable = variable1, font=("Copperplate Gothic Bold", 11)) #Creamos el comboBox Origen
comboDestino= ttk.Combobox(framePr, textvariable = variable2, font=("Copperplate Gothic Bold", 11)) #Creamos el comboBox Destino
comboOrigen['values'] = valuesOrigen
comboOrigen['state'] = 'readonly'
comboOrigen.current(0)#Establecemos valor inicial
comboDestino['values'] = valuesDestino
comboDestino['state'] = 'readonly'
comboDestino.current(0)#Establecemos valor inicial
ruta = Label(framePr, text="Ruta: ", font=("Copperplate Gothic Bold", 15), fg="white", bg="black")
ruta.place(x=130, y=100)
comboOrigen.place(x=40, y=150)
comboDestino.place(x=40, y=180) #Añadimos los comboBox al framePr
comboOrigen.bind('<<ComboboxSelected>>', comboChangedOrigen)
comboDestino.bind('<<ComboboxSelected>>', comboChangedDestino) #Configuramos lo comandos de los comboBox
origen.set("---Seleccionar Origen---")
destino.set("---Seleccionar Destino---") #Establecemos los valores originales de origen y destino

#Frames auxiliares para el FrameIm
tren = Label(frameIm)
bandera = Label(frameIm)
imgTren = ImageTk.PhotoImage(Image.open('tren.jpg'))
imgBand = ImageTk.PhotoImage(Image.open('bandera.png'))

#Coordenadas auxiliares de puntos que se usaran para dibujar las curvas del plano del metro
with open('coordsAux.csv', newline='') as File:  
    reader = csv.reader(File,delimiter=';')
    for row in reader :
        matriz.append([])
        coordsAux = []
        coordsAux.append((int)(row[2]))
        coordsAux.append((int)(row[3]))
        matriz[contMatriz].append(row[0])
        matriz[contMatriz].append(row[1])
        matriz[contMatriz].append(coordsAux)
        contMatriz += 1

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()