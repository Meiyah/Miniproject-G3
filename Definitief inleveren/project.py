#afhandelen van alle imports die nodig zijn
from tkinter import *
from tkinter.messagebox import showinfo
from tkinter.messagebox import showwarning
from tkinter.messagebox import askyesno
import xmltodict
import random
import requests
import time
import datetime
import sqlite3
from qrcode import *
from PIL import Image, ImageTk

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
    """Opent de films.xml file"""
    bestand = open('films.xml', 'wb')
    bestand.write(bytes(response.text, 'UTF-8'))
    bestand.close()

schrijf_xml()
################################################

#xml omzetten zodat die kan worden uitgelezen
def verwerk_xml(file):
    """Zet de xml om zodat deze kan worden uitgelezen"""
    bestand = open(file, 'r')
    xml_string = bestand.read()
    return xmltodict.parse(xml_string)

films = verwerk_xml('films.xml')


###############SQL#####################################

#connectie leggen met de database
conn = sqlite3.connect('project_database.db')
c = conn.cursor()

#aanbieders ophalen
aanbieders = verwerk_xml('aanbiedersaccount.xml')

#alle huidige titels ophalen
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
except:
    print("titels bestaan al")

###################################################################


#\\\\\\\\\\\\\\\\\\\Kijker\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

#globale variabelen
definitieve_naam = ""
definitieve_email = ""
definitieve_code = ""

selectwaarde = ""

def selectie(evt):
    #waarde opslaan waar de cursor op het moment is in de listbox van scherm 2
    """Slaat de waarde op waar de cursor op het moment is in de listbox van scherm 2"""
    value=Filmlijst.get(Filmlijst.curselection())
    global selectwaarde
    selectwaarde = value[0]
    print(selectwaarde)


def close_frame1():
    #sluiten van eerste kijkerscherm
    """Sluit het eerste kijkerscherm af"""
    global definitieve_naam
    definitieve_naam = GETnaam.get()

    global definitieve_email
    definitieve_email = GETemail.get()

    global definitieve_code
    definitieve_code = codeGenerator(definitieve_naam)

    #naam en email vakken mogen niet leeg zijn en mailvak moet bepaalde waardes bevatten om door te kunnen
    if ((definitieve_naam != "") and (definitieve_email != "") and ("@" in definitieve_email) and ((".com" in definitieve_email) or (".nl" in definitieve_email))):
        frame1.destroy()
        frame2.pack()
    else:
        showinfo(title="popup", message="onjuiste invoer!")


def close_Frame2():
    #sluiten van tweede kijkerscherm
    """Sluit het tweede kijkerscherm af"""
    if selectwaarde != "":
        frame2.destroy()
        frame3.pack()

        Label(frame3, text=("naam:", definitieve_naam), width=50, bg='black', fg='White', font=15).pack(pady = 10)
        Label(frame3, text=("email:", definitieve_email), width=50, bg='black', fg='White', font=15).pack(pady = 10)
        Label(frame3, text=("code:", definitieve_code), width=50, bg='black', fg='White', font=15).pack(pady = 10)
        Label(frame3, text=("film:", selectwaarde), width=50, bg='black', fg='White', font=15).pack(pady = 10)
    else:
        showinfo(title="popup", message="Kies een film alstublieft")

def close_Frame3():
    #sluiten van laatste kijkerscherm en gegevens invoeren in database
    """Sluit het laatste kijkersscherm en voert de gegevens in in de sql database"""
    c.execute("INSERT INTO Bezoekers VALUES(?, ?, ?, ?, ?)", (selectwaarde, definitieve_naam, definitieve_email, definitieve_code, date))
    conn.commit()
    window.destroy()

def codeGenerator(naam):
    #aanmaken van een unieke code voor de kijker gebasseerd op zijn/haar naam
    """Maakt een unieke code aan voor de kijker gebasseerd op zijn/haar naam"""
    code = naam
    uniek = ""

    for i in code :
        r = ord(i) + random.randrange(1, 4)
        q = chr(r)
        uniek += q
    return uniek

def kijkerScherm():
    #wordt actief wanneer er sprake is van een kijker
    """Roept het kijkersscherm op als er voor kijker is gekozen"""
    beginscherm.destroy()
    frame1.pack()

def aanbiederScherm():
    #wordt actief wanneer er sprake is van een aanbieder
    """Roept het aanbiedersscherm op als er voor aanbieder is gekozen"""
    beginscherm.destroy()
    aanmeldFrame.pack()

#initialiseren van basis programma
window = Tk()
window.title("Welcome")

w, h = window.winfo_screenwidth(), window.winfo_screenheight()
window.overrideredirect(1)
window.geometry("%dx%d+0+0" % (w, h))

window.configure(background="black")

#eerste scherm van programma meteen activeren
beginscherm = Frame(window)
beginscherm.pack()

#GIF afbeelding
begin_logo = PhotoImage(file="cinema.gif")
w1 = Label(beginscherm,bg="black" , image=begin_logo).pack(side="top")

#afhandelen van de 2 beginscherm buttons
beginbutton = Button(beginscherm, text="Aanbieder",bg="red4",fg="white", width = 87,command=(lambda: aanbiederScherm())).pack()
beginbutton2 = Button(beginscherm, text="Kijker",bg="red4" ,fg="white",width = 87,command=(lambda: kijkerScherm())).pack()


def callback():
    #functie voor de quit button
    """Functie voor de quit button"""
    if askyesno('Verify', 'Do you Really want to quit?'):
        showwarning('Yes', 'Shutting down Filmtotaal')
        window.destroy()
    else:
        showinfo('No', 'Quit has been cancelled')

#initialiseren van de quit button
button1 = Button(text='EXIT',bg="red",fg="black" ,command=callback).pack()



#frame n1   ###########################
frame1 = Frame(window, padx=50, pady=30)
frame1.configure(background="red4")

GETnaam = StringVar()
GETemail = StringVar()

#GIF afbeelding
logo1 = PhotoImage(file="pop1.gif")
w1 = Label(frame1 , image=logo1).pack(side=TOP)

label = Label(frame1, text="voer gegevens in:", bg="lightblue1", font=25).pack(ipady=10, ipadx = 10 ,side=TOP)

Naam = Label(frame1, text='naam:', font=15,bg="red4",fg="white").pack(pady=0, padx=20, side=LEFT)
Naam_tekst = Entry(frame1, textvariable = GETnaam).pack(pady=50, side=LEFT)

Email = Label(frame1, text='email:', font=15,bg="red4",fg="white").pack(pady=0, padx=20, side=LEFT)
Email_tekst = Entry(frame1, textvariable = GETemail).pack(pady=100, side=LEFT)

buttonR = Button(frame1, text='continue',bg="seagreen1", command=(lambda: close_frame1()))
buttonR.pack(side=BOTTOM)
#EINDE FRAME n1#########################################







#frame n2   ######################################
frame2 = Frame(window, padx=50, pady=30)
frame2.configure(background="red4")

logo2 = PhotoImage(file="pop1.gif")
w1 = Label(frame2 , image=logo2).pack(side="top")

label2 = Label(frame2, text="films van vandaag:", bg="lightblue1", font=25).pack(ipadx=10, pady=10,side=TOP)
Filmlijst = Listbox(frame2, selectmode=SINGLE, width=50, height=15)
Filmlijst.bind('<<ListboxSelect>>',selectie)
for i in range(len(films['filmsoptv']['film'])):
    Filmlijst.insert(END, (Nieuwe_film_lijst[i], "om",  Nieuwe_film_lijst_tijden[i] ))

Filmlijst.pack()

choose = Button(frame2, text="choose",bg="seagreen1", command=(lambda: close_Frame2())).pack(pady=20, side=RIGHT)
#EINDE FRAME n2####################################################




#frame n3   #########################################
#frame initialiseren
frame3 = Frame(window, padx=300, pady=100)
frame3.configure(background="red4")

#GIF afbeelding
logo3 = PhotoImage(file="filmgegevens.gif")
w1 = Label(frame3 , image=logo3).pack(side="top")

gegevens = Label(frame3, text="uw gegevens:", bg="red4",fg="white", font=25).pack(ipadx=100, ipady=30)

accept = Button(frame3, text="accept",bg="seagreen1", command=(lambda: close_Frame3())).pack(side=BOTTOM, pady = 10)
#EINDE FRAME n3####################################################
#EINDE KIJKERSCHERMEN\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\










def QRcode(lijst_bezoekers):
    #Gegevens van de aanbieder opslaan in een QR code
    """Slaat de gegevens van de aanbieder op in een QR code"""
    qr = QRCode()
    l = lijst_bezoekers

    #Hier wordt de data toegevoegd
    for rij in range(len(l)):
        qr.add_data(l[rij])
        qr.make(fit=True)

    #img bevat een PIL.image.image object
    img = qr.make_image()

    #Save the Code
    img.save('qrcode_project.png')




############AANBIEDERS##############################

#initialiseren van inlogscherm
aanmeldFrame = Frame(window)
aanmeldFrame.configure(background="red4")

#lijst met bezoekers van aanbieder
lijst = []

#globale variabelen voor inloggegevens
GETID = StringVar()
GETWw = StringVar()

#initialiseren van frame voor de lijst
Kijkerslist = Frame(window)
Kijkerslist.configure(background="red4")

def meldAan():
    global aanmeldFrame
"""Checkt of de inloggevens kloppen wie er op dat moment inlogt"""
    #invoer opslaan in variabelen
    def_ID = GETID.get()
    def_Ww = GETWw.get()

    #gebasseerd op wie er inlogt, worden zijn bezoekers voor die dag opgevraagd
    k = (def_ID,)
    Checklist = c.execute("SELECT f.Titel, b.Naam, f.Starttijd, fa.Aanbieder FROM Films f LEFT JOIN Bezoekers b on f.Titel = b.Film LEFT JOIN FilmsMetAanbieders fa on fa.Film = f.Titel WHERE Naam NOT NULL AND Aanbieder IS ? ORDER BY Starttijd, Naam", (k))

    ingelogd = False

    #kijkt of de meegegeven ID en Wachtwoord voorkomen in de database met accounts
    for row in range(len(aanbieders['aanbieders']['aanbieder'])):
        if(def_ID in aanbieders['aanbieders']['aanbieder'][row]['Naam']) and (def_Ww in aanbieders['aanbieders']['aanbieder'][row]['Wachtwoord']) and (def_ID != "") and (def_Ww != ""):
            ingelogd = True
            aanmeldFrame.destroy()

            for row in Checklist:
                lijst.append(row)
                print(row)

            QRcode(lijst)
            load = Image.open("qrcode_project.png")
            render = ImageTk.PhotoImage(load)

            img = Label(Kijkerslist,image =render)
            img.image = render
            img.place(x = 250, y = 125)

            Kijkerslist.pack(ipadx=500, ipady=400)
            print("done")

    if not ingelogd:
        #wanneer er een foute invoer wordt gegeven komt er een melding binnen en vervolgens wordt het frame opnieuw gebouwd
        showinfo(title="popup", message="Het ID en/of Wachtwoord is onjuist")
        aanmeldFrame.destroy()
        aanmeldFrame = Frame(window)
        aanmeldFrame.configure(background="red4")
        Loginscreen()
        aanmeldFrame.pack()


def Loginscreen():
    #aanmaak van attributen voor het inlogscherm
    """maakt de attributen voor het inlogscherm aan"""
    welkom = Label(aanmeldFrame, text="Voer uw gegevens in A.u.b.",bg="red4",fg="white",font=("Helvetica", 16)).pack()

    global GETID
    global GETWw

    ID = Label(aanmeldFrame, text='ID:', bg="red4",fg="white").pack(pady=0, padx=20, side=LEFT)
    ID_tekst = Entry(aanmeldFrame, textvariable = GETID).pack(pady=50, side=LEFT)

    Ww = Label(aanmeldFrame, text='Password:', font=15,bg="red4",fg="white").pack(pady=0, padx=20, side=LEFT)
    Ww_tekst = Entry(aanmeldFrame, textvariable = GETWw).pack(pady=100, side=LEFT)

    Aanmelden = Button(aanmeldFrame, text="aanmelden",bg="green" ,fg="white", command=(lambda: meldAan())).pack(side=BOTTOM)


Loginscreen()


#kop voor in frame met lijst van bezoekers
bezoekers = Label(Kijkerslist, text="bezoekers:", bg="red4",fg="white", font=25).pack()

#connectie laten comitten
conn.commit()
#programma draaiende houden
window.mainloop()
