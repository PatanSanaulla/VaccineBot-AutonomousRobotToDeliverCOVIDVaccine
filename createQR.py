import qrcode

code = qrcode.make("RIGHT")

code.save("RIGHT_QR.png")

print("saved")
