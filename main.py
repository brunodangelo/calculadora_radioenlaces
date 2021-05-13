# Copyright Google Inc. 2010 All Rights Reserved
#API de Google ---> https://developers.google.com/maps/gmp-get-started   ||| API utilizada: "Maps Elevation API"
import simplejson
import urllib
from urllib.parse import urlencode
from urllib.request import urlopen
from io import open
import ast
from math import acos, cos, sin, radians, sqrt, ceil, log
import webbrowser
from colorama import init, Fore, Back, Style

ELEVATION_BASE_URL = 'https://maps.google.com/maps/api/elevation/json'
CHART_BASE_URL = 'https://chart.googleapis.com/chart'

apikey='key=AIzaSyBYZMi1ShUMihw5DUztkFKP2dhUPp6brdA'

def getChart(chartData, chartDataScaling, chartType="lc",chartLabel="Elevación en Metros",chartSize="800x360", chartColor="orange", **chart_args):
    chart_args.update({
        'cht': chartType,
        'chs': chartSize,
        'chl': chartLabel,
        'chco': chartColor,
        'chds': chartDataScaling,
        'chxt': "x,y",
        'chxr': "1,{}".format(chartDataScaling),
    })

    dataString = 't:' + ','.join(str(x) for x in chartData) #formamos la url con el perfil de terreno en la API de Google
    chart_args['chd'] = dataString.strip(',')

    chartUrl = CHART_BASE_URL + '?' + urllib.parse.urlencode(chart_args)

    webbrowser.open(chartUrl, new=2, autoraise=True)
    init()
    print(Fore.WHITE+Back.BLUE+"Se muestra el perfil topografico en una ventana emergente"+Back.RESET)
    print("-------------------------------------------------------------------------")

def getElevation(path="-36.321978, -57.659936|-38.003508, -57.553065",samples="500",sensor="false", **elvtn_args):
    elvtn_args.update({
        'path': path,
        'samples': samples,
        'sensor': sensor
    })

    url = ELEVATION_BASE_URL + '?' + urllib.parse.urlencode(elvtn_args) + '&' + apikey #urlencode pasa los argumentos y los une para conformar una parte de la url, usando codigo URL
    response = simplejson.load(urllib.request.urlopen(url)) #urlopen abre la url | response contiene los valores de la elevacion del terreno

    #Guardamos en un archivo el Perfil del Terreno
    perfilDelTerreno = open("perfil.txt","w")
    perfilDelTerreno.write(str(response)) #Lo guardamos como en el archivo json de Google
    perfilDelTerreno.close()

def getInfo():
    #Leemos el archivo donde guardamos los datos del perfil del terreno
    perfilDelTerreno = open("perfil.txt","r")
    perfil=ast.literal_eval(perfilDelTerreno.read()) #Leemos y convertimos el string a dict para acceder a los valores
    perfilDelTerreno.close()

    elevationList = []
    latitudeList = []
    longitudeList = []

    for perfiles in perfil['results']:
        elevationList.append(perfiles['elevation'])
        latitudeList.append(perfiles['location']['lat'])
        longitudeList.append(perfiles['location']['lng'])

    return [elevationList, latitudeList, longitudeList]


def getDistance(puntoA, puntoB):
    puntoA=[radians(puntoA[0]), radians(puntoA[1])] #pasamos las coordenadas a radianes para
    puntoB=[radians(puntoB[0]), radians(puntoB[1])] #hacer los calculos
    a=6371.01 #radio de la tierra en km
    d=a*acos(sin(puntoA[0])*sin(puntoB[0]) + cos(puntoA[0])*cos(puntoB[0])*cos(puntoA[1] - puntoB[1]))
    return d

def getLink(puntoA,puntoB,f,k):
    elevationList = getInfo()[0]
    latitudeList = getInfo()[1]
    longitudeList = getInfo()[2]

    perfilDelTerreno = open("perfil.txt","r")
    perfil=ast.literal_eval(perfilDelTerreno.read()) #Leemos y convertimos el string a dict para acceder a los valores
    perfilDelTerreno.close()

    hObs = max(elevationList)

    for perfiles in perfil['results']:
        if perfiles['elevation']==max(elevationList):
            puntoObs=[perfiles['location']['lat'],perfiles['location']['lng']] #Es el punto donde se encuentra el Obstaculo
    d1 = getDistance(puntoA, puntoObs) #km
    d = getDistance(puntoA, puntoB) #km
    d2 = (d - d1) #km
    c = ((d1*d2*0.078)/k) #en metros
    z4_5 = 0.66*c #en metros
    cL = 3*(10**5) #velocidad de la luz km/seg
    r1 = 548*sqrt((d1*d2)/(d*f)) #metros
    D = 0.6*r1 + z4_5 #OBSTACULO FICTICIO en metros

    Ha = hObs + c + D

    print("Distancia 1: {} km".format(round(d1,2)))
    print("Distancia 2: {} km".format(round(d2,2)))
    print("Distancia Total: {} km".format(round(d,2)))
    print("CURVATURA: {} metros".format(round(c,2)))
    print("Primer radio de Fresnel: {} metros".format(round(r1,2)))
    print("Altura del obstáculo: {} m.s.n.m".format(round(hObs,2)))
    print("Despejamiento: {} metros".format(round(D,2)))
    print("Altura de la antena: {} m.s.n.m".format(round(Ha,2)))
    print("Cantidad de tramos de 6 metros: {}".format(ceil(Ha/6)))
    print("-------------------------------------------------------------------------")

def getPtx(PIRE, Gtx, Grx, f, d):
    Ptel = -147 + 20*log(f*(10**6),10) + 20*log(d*1000,10)
    Prx = -125 #dBW
    Ptx = Prx - Gtx - Grx + Ptel #dBW

    print("Potencia de transmisión: {} dBW ({} dBm)".format(round(Ptx,2),round((Ptx+30),2)))
    print("-------------------------------------------------------------------------")

def fadingMargin(puntoA,puntoB,f):
    #Factor de Rigurosidad
    while True:
        try:
            print("Factor de rugosidad (A): ")
            print("1- A=4 (Agua o terreno liso)")
            print("2- A=1 (Terreno promedio)")
            print("3- A=0.25 (Terreno aspero o montañoso)")
            opcion1 = int(input("Opción: "))
            print("-------------------------------------------------------------------------")
            if opcion1 == 1:
                A = 4
                break
            elif opcion1 == 2:
                A = 1
                break
            elif opcion1 == 3:
                A = 0.25
                break
            else:
                print("-------------------------------------------------------------------------")
                print("Debe introducir una opción entre 1 y 3")
                print("-------------------------------------------------------------------------")
        except ValueError:
            print("-------------------------------------------------------------------------")
            print("Opción no válida")
            print("-------------------------------------------------------------------------")

    #Factor del clima
    while True:
        try:
            print("Factor de Factor de análisis del clima (B):")
            print("1- B=1")
            print("2- B=0.5 (Áreas calientes y húmedas)")
            print("3- B=0.25 (Áreas continentales promedio)")
            print("4- B=0.125 (Áreas sécas o montañosas)")
            opcion2 = int(input("Opción: "))
            print("-------------------------------------------------------------------------")
            if opcion2 == 1:
                B = 1
                break
            elif opcion2 == 2:
                B = 0.5
                break
            elif opcion2 == 3:
                B = 0.25
                break
            elif opcion2 == 4:
                B = 0.125
                break
            else:
                print("-------------------------------------------------------------------------")
                print("Debe introducir una opción entre 1 y 4")
                print("-------------------------------------------------------------------------")
        except ValueError:
            print("-------------------------------------------------------------------------")
            print("Opción no válida")
            print("-------------------------------------------------------------------------")

    #Confiabilidad
    while True:
        try:
            print("Factor de Confiabilidad (R) (Ej: 0.999999):")
            R = float(input("R: "))
            print("-------------------------------------------------------------------------")
            if 0<R<1: #comprobamos que el usuario introduce datos correctos
                break
            else:
                print("Ingrese un numero flotante entre 0 y 1")
                print("-------------------------------------------------------------------------")
        except ValueError:
            print("-------------------------------------------------------------------------")
            print("Debe ingresar un numero flotante")
            print("-------------------------------------------------------------------------")

    #Calculo
    d = getDistance(puntoA, puntoB)
    Fm = 30*log(d,10) + 10*log(6*A*B*(f/1000),10) - 10*log(1-R,10) - 70
    print("El margen de Fading es {} dB".format(round(Fm,2)))
    print("-------------------------------------------------------------------------")


if __name__ == '__main__': #Permite o previene que partes del codigo se ejecuten cuando se estan importando modulos

    print("-------------------------------------------------------------------------")
    print("TP2 DSSC - Cálculo de RadioEnlaces - Eiras, Orazi, Selaro, D'Angelo")
    print("El software permite calcular el diseño de un Radio Enlace entre 2 puntos")
    print("teniendo en cuenta la elevacion del terreno.")
    print("-------------------------------------------------------------------------")

    webbrowser.open("https://www.gps-coordinates.net/", new=2, autoraise=True)
    init()
    print(Fore.WHITE+Back.BLUE+"BUSQUE LAS COORDENADAS EN LA PAGINA WEB ABIERTA \nIntroduzcalas con el siguiente formato ejemplo:-36.321978, -57.659936\n"+Back.RESET)

    try:
        print("Ingrese las coordenadas en formato decimal:")

        print("PUNTO A")
        latA = float(input('Latitud --> '))
        lngA = float(input('Longitud --> '))
        puntoA = [latA, lngA]

        print("PUNTO B")
        latB = float(input('Latitud --> '))
        lngB = float(input('Longitud --> '))
        puntoB = [latB, lngB]

        caminoStr = "{}, {}".format(latA, lngA) + "|" + "{}, {}".format(latB, lngB) #la funcion getElevation requiere strings

        f = int(input("Frecuencia en MHz:"))
        k = float(input('Factor k (valores normales entre  -1 y 3): '))
        print("-------------------------------------------------------------------------")

        getElevation(caminoStr) #Guardamos el perfil en un .txt

    except urllib.error.HTTPError:
        print("ERROR! Introduzca coordenadas válidas")
    except ValueError:
        print("Tipo de dato incorrecto. Para las coordenadas, frecuencia y factor k debe introducir números")

    #Menu
    while True:
        try:
            print("MENU")
            print("1- Calcular Potencia de Tx")
            print("2- Calcular Margen de Fading")
            print("3- Calcular altura minima de las Antenas y Datos del enlace")
            print("4- Obtener grafico del Perfil del Terreno (Pop up)")
            print("5- Salir")
            opcion = int(input("Opción: "))
            print("-------------------------------------------------------------------------")
            if opcion == 1:
                #Valores de la consigna
                PIRE = 11 #dBW
                Gtx = 18 #dBi
                Grx = 18 #dBi
                getPtx(PIRE, Gtx, Grx, f, d=getDistance(puntoA, puntoB))
            elif opcion == 2:
                fadingMargin(puntoA, puntoB, f)
            elif opcion == 3:
                getLink(puntoA,puntoB,f,k)
            elif opcion == 4:
                #autoescala para el grafico
                elevacionMax=max(getInfo()[0])
                elevacionMin=min(getInfo()[0])
                if elevacionMin>0:
                    elevacionMin=0
                autoEscala = "{},{}".format(elevacionMin*1.1,elevacionMax*1.1)
                #grafico
                getChart(chartData=getInfo()[0],chartDataScaling=autoEscala)
            elif opcion == 5:
                break
        except ValueError:
            print("Introduzca una opción válida")
        except:
            print("Error!")
