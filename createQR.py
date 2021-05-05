import qrcode

code = qrcode.make("")

code.save("RIGHT_QR.png")

print("saved")
