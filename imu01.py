import serial

#Indentify serial communication
ser = serial.Serial('/dev/ttyUSB0', 9600)

count = 0

while True:
    if (ser.in_waiting > 0):
        count += 1
        
        #Read serial stream
        line = ser.readline()
        #print(line)
        
        #Avoid first n-lines of serial information
        if count>1:
            
            #Strip serial stream of extra characters
            
            line = line.rstrip().lstrip()
            #print(line)
            
            line = str(line)
            line = line.strip("'")
            line = line.strip("b'")
            #print(line)
            
            #Return float
            line = float(line)
            
            print(line, "\n")
            
