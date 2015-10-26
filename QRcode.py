__author__ = 'Jens'
#Importeer de qrcode module en definier qr als qrcode.QRcode
import qrcode
qr = qrcode.QRCode()

#Hier wordt de data toegevoegd
qr.add_data('https://mijn.hu.nl')
qr.make(fit=True)

#img bevat een PIL.image.image object
img = qr.make_image()

#Save the Code
img.save('test2.png')
