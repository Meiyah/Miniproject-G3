#Importeer de qrcode module en definier qr als qrcode.QRcode
import qrcode
qr = qrcode.QRCode()

#Hier wordt de data toegevoegd
qr.add_data('Kaartnummer= 100 ,E-mail= abc@abc.com, code=8465bxfgeu')
qr.make(fit=True)

#img bevat een PIL.image.image object
img = qr.make_image()

#Save the Code
img.save('test2.png')
