import sqlite3

conn = sqlite3.connect('bezoekers_data.db')
c = conn.cursor()

#c.execute("CREATE TABLE Aanbieders('ID' TEXT, 'Password' TEXT)")


aanbieders = ['Youri', 'Jens', 'Kelvin', 'Ryan', 'Pjotr']
wachtwoorden = ['w1','w2','w3','w4','w5',]

for i in range(5):
    c.execute("INSERT INTO Aanbieders VALUES(?, ?)", (aanbieders[i], wachtwoorden[i]))

conn.commit()
