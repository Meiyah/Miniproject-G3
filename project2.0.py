from tkinter import *
from tkinter.messagebox import showinfo
import csv
import xmltodict
import random
import requests
import time
import datetime
import sqlite3


#########API KEY VAN DE DAG OPVRAGEN##############
#tijd instellen
day = time.strftime('%d')
month = time.strftime('%m')
year = time.strftime('%Y')
date =  day + "-" + month + "-" + year

auth_details = ('<gebruikersnaam>', '<api key>')
response = requests.get('http://www.filmtotaal.nl/api/filmsoptv.xml?apikey=0246cgbbns3bmp7jvo7tbkri1p17um87&dag=' + date + '&sorteer=0',
auth=auth_details)

def schrijf_xml():
    bestand = open('films.xml', 'w')
    bestand.write(str(response.text))
    bestand.close()

schrijf_xml()
################################################


def verwerk_xml(file):
    bestand = open(file, 'r')
    xml_string = bestand.read()
    return xmltodict.parse(xml_string)

films = verwerk_xml('films.xml')


###############SQL#####################################
conn = sqlite3.connect('project_database.db')
c = conn.cursor()

aanbieders = verwerk_xml('aanbiedersaccount.xml')

#aanbieders = c.execute("SELECT ID FROM Aanbieders")

#aanbieders_lijst = []

#for row in aanbieders:
    #aanbieders_lijst.append(row)

#print(aanbieders_lijst)


filmsSQL = c.execute("SELECT Titel FROM Films")

film_lijst = []
Nieuwe_film_lijst = []
Nieuwe_film_lijst_tijden = []

#nieuwe films
for row in range(len(films['filmsoptv']['film'])):
    Nieuwe_film_lijst.append(films['filmsoptv']['film'][row]['titel'])
    Nieuwe_film_lijst_tijden.append(datetime.datetime.fromtimestamp(int(films['filmsoptv']['film'][row]['starttijd'])).strftime('%H:%M'))

#bestaande films
for row in filmsSQL:
    film_lijst.append(row)

print(film_lijst)
print(Nieuwe_film_lijst)

#zodra er nieuwe films zijn wordt de tabel met oude films geleegd
for i in film_lijst:
    if i not in Nieuwe_film_lijst:
        c.execute("DELETE FROM Films WHERE Titel IS ?", (i))
        c.execute("DELETE FROM FilmsMetAanbieders")

#als er een nieuwe film is wordt deze in de database gezet
try:
    for j in Nieuwe_film_lijst:
        if j not in film_lijst:
            for i in range(len(films['filmsoptv']['film'])):
                c.execute("INSERT INTO Films VALUES(?, ?, ?)", (films['filmsoptv']['film'][i]['titel'], films['filmsoptv']['film'][i]['jaar'], (datetime.datetime.fromtimestamp(int(films['filmsoptv']['film'][i]['starttijd'])).strftime('%H:%M'))))
                getal = random.randrange(0,5)
                c.execute("INSERT INTO FilmsMetAanbieders VALUES(?, ?)", (films['filmsoptv']['film'][i]['titel'], aanbieders['aanbieders']['aanbieder'][getal]['Naam']))
    film_lijst = Nieuwe_film_lijst
except:
    print("titels bestaan al")









###################################################################


#\\\\\\\\\\\\\\\\\\\Kijker\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

definitieve_naam = ""
definitieve_email = ""
definitieve_code = ""

selectwaarde = ""

def selectie(evt):
    value=Filmlijst.get(Filmlijst.curselection())
    global selectwaarde
    selectwaarde = value[0]
    print(selectwaarde)


def close_frame1():
    global definitieve_naam
    definitieve_naam = GETnaam.get()

    global definitieve_email
    definitieve_email = GETemail.get()

    global definitieve_code
    definitieve_code = codeGenerator(definitieve_naam)

    frame1.destroy()
    frame2.pack()


def close_Frame2():
    frame2.destroy()
    frame3.pack()

    Label(frame3, text=("naam:", definitieve_naam)).pack()
    Label(frame3, text=("email:", definitieve_email)).pack()
    Label(frame3, text=("code:", definitieve_code)).pack()
    Label(frame3, text=("film:", gekozenFilm())).pack()

def codeGenerator(naam):
    code = naam
    uniek = ""


    for i in code :
        r = ord(i) + random.randrange(1, 4)
        q = chr(r)
        uniek += q
    return uniek

def gekozenFilm():
    return selectwaarde

def close_Frame3():
    c.execute("INSERT INTO Bezoekers VALUES(?, ?, ?, ?)", (gekozenFilm(), definitieve_naam, definitieve_email, definitieve_code))
    conn.commit()
    window.destroy()
    bestand.close()

def kijkerScherm():
    beginscherm.destroy()
    frame1.pack()

def aanbiederScherm():
    beginscherm.destroy()
    aanmeldFrame.pack()


window = Tk()
window.title("project")

beginscherm = Frame(window)
beginscherm.pack()
beginbutton = Button(beginscherm, text="aanbieder", command=(lambda: aanbiederScherm())).pack()
beginbutton2 = Button(beginscherm, text="kijker", command=(lambda: kijkerScherm())).pack()


aanmeldFrame = Frame(window)




#frame n1   ###########################3
frame1 = Frame(window, padx=50, pady=30)


GETnaam = StringVar()
GETemail = StringVar()

label = Label(frame1, text="voer gegevens in:", bg="green", font=25).pack(ipady=50, ipadx = 50 ,side=TOP)

Naam = Label(frame1, text='naam:', font=15).pack(pady=0, padx=20, side=LEFT)
Naam_tekst = Entry(frame1, textvariable = GETnaam).pack(pady=50, side=LEFT)

Email = Label(frame1, text='email:', font=15).pack(pady=0, padx=20, side=LEFT)
Email_tekst = Entry(frame1, textvariable = GETemail).pack(pady=100, side=LEFT)

buttonR = Button(frame1, text='continue', command=(lambda: close_frame1()))
buttonR.pack(side=BOTTOM)
##########################################












#frame n2   ######################################
frame2 = Frame(window, padx=100, pady=80)


label2 = Label(frame2, text="films van vandaag:", bg="blue", font=25).pack(ipadx=60, pady=50)
Filmlijst = Listbox(frame2, selectmode=SINGLE, width=50, height=15)
Filmlijst.bind('<<ListboxSelect>>',selectie)
for i in range(len(films['filmsoptv']['film'])):
    Filmlijst.insert(END, (Nieuwe_film_lijst[i], "om",  Nieuwe_film_lijst_tijden[i] ))



Filmlijst.pack()

choose = Button(frame2, text="choose", command=(lambda: close_Frame2())).pack(pady=20, side=RIGHT)
#####################################################







#frame n3   #########################################

frame3 = Frame(window, padx=300, pady=100)

bestand = open("bezoekers.csv", 'a')
reader = csv.writer(bestand, delimiter=';')

gegevens = Label(frame3, text="uw gegevens:", bg="red", font=25).pack(ipadx=100, ipady=30)

accept = Button(frame3, text="accept", command=(lambda: close_Frame3())).pack(side=BOTTOM)
#####################################################
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\











############AANBIEDERS##############################

lijst = []


aanbieders = verwerk_xml('aanbiedersaccount.xml')

def sort(lst):
    for i in range(len(lijst)):
        for j in range(i+1, len(lijst)):
            if lst[j] < lst[i]:
                lst[j], lst[i] = lst[i], lst[j]
    return lst

def meldAan():
    def_ID = GETID.get()
    def_Ww = GETWw.get()

    ingelogd = False
    for row in range(len(aanbieders['aanbieders']['aanbieder'])):
        if(def_ID in aanbieders['aanbieders']['aanbieder'][row]['Naam']) and (def_Ww in aanbieders['aanbieders']['aanbieder'][row]['Wachtwoord']) and (def_ID != "") and (def_Ww != ""):
            ingelogd = True
            print("ingelogd!")
            aanmeldFrame.destroy()
            lijstframe.pack(ipadx=200)
            bezoekers.pack(pady=20)
            T.pack()
    if not ingelogd:
        showinfo(title="popup", message="verkeerde invoer! probeer het later nog eens")
        window.destroy()



welkom = Label(aanmeldFrame, text="Welkom!").pack()

GETID = StringVar()
GETWw = StringVar()

ID = Label(aanmeldFrame, text='ID:', font=15).pack(pady=0, padx=20, side=LEFT)
ID_tekst = Entry(aanmeldFrame, textvariable = GETID).pack(pady=50, side=LEFT)

Ww = Label(aanmeldFrame, text='Password:', font=15).pack(pady=0, padx=20, side=LEFT)
Ww_tekst = Entry(aanmeldFrame, textvariable = GETWw).pack(pady=100, side=LEFT)


Aanmelden = Button(aanmeldFrame, text="aanmelden", command=(lambda: meldAan())).pack()

lijstframe = Frame(window)

bezoekers = Label(lijstframe, text="bezoekers:", bg="red", font=25)

bestand_bezoekers = open("bezoekers.csv", 'r')
reader_bezoekers = csv.DictReader(bestand_bezoekers, delimiter=';')

for row in reader_bezoekers:
    lijst.append((row['naam'] + ", " + row['film']))

sort(lijst)

T = Text(lijstframe, width=40, height=20)
for item in range(len(lijst)):
    T.insert(END, ((lijst[item]) + '\n'))

bestand_bezoekers.close()


conn.commit()
window.mainloop()
