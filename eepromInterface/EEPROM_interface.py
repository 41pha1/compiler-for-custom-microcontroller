import RPi.GPIO as GPIO
import time

# 13, 16, 18, 37
WE = 38
OE = 35

A = [22, 3, 5, 7, 29, 31, 26, 24, 21, 19, 40, 15]
D = [23, 32, 33, 8, 10, 36, 11, 12]

chip = 0
writeZeros = False
doFullClear = False
verifyOnly = False
changeMode = True
dataFile = "out.txt"

def setAddress(addr):
    for i in range(len(A)):
        bit = addr & 1
        if(bit):
            GPIO.output(A[i], GPIO.HIGH)
        else:
            GPIO.output(A[i], GPIO.LOW)

        addr = addr >> 1

def readByte(addr):
    setAddress(addr)
    byte = 0
    for i in range(len(D)):
        byte += GPIO.input(D[i]) << len(D)
        byte = byte >> 1
    return byte

def writeByte(addr, byte):
    setAddress(addr)

    for i in range(len(D)):
        bit = byte & 1
        if(bit):
            GPIO.output(D[i], GPIO.HIGH)
        else:
            GPIO.output(D[i], GPIO.LOW)

        byte = byte >> 1
    time.sleep(0.001)
    GPIO.output(WE, GPIO.LOW)
    time.sleep(0.01)
    GPIO.output(WE, GPIO.HIGH)
    time.sleep(0.005)

def setupRead():
    for i in range(len(D)):
        GPIO.setup(D[i], GPIO.IN)
    GPIO.output(OE, GPIO.LOW)
    time.sleep(0.0005)

def setupWrite():
    for i in range(len(D)):
        GPIO.setup(D[i], GPIO.OUT)
    GPIO.output(OE, GPIO.HIGH)
    time.sleep(0.0005)

def clear():
    print("Clearing entire chip...")
    for i in range(4096):
        writeByte(i, 0)

displayCount = 0

def display(byte):
    global displayCount
    displayCount += 1

    if displayCount % 16 == 1:
        print(hex(displayCount-1)+": "),

    hexstring = hex(byte)[2:]
    if byte < 16:
        hexstring = "0" + hexstring
    print(hexstring),

    if displayCount % 4 == 0:
        print(" "),
    if displayCount % 16 == 0:
        print("")

GPIO.setmode(GPIO.BOARD)
GPIO.setup(WE, GPIO.OUT)
GPIO.setup(OE, GPIO.OUT)

for i in range(len(A)):
    GPIO.setup(A[i], GPIO.OUT)

GPIO.output(WE, GPIO.HIGH)
GPIO.output(OE, GPIO.HIGH)

f = open(dataFile, "r")
f.readline()

setupWrite()
if doFullClear:
    clear()

line = f.readline()[:-1]
bytes = []
addr = 0
if changeMode:
    setupRead()

while line:
    byte = (int(line, 16)>>8*chip) % 256
    display(byte)
    bytes.append(byte)
    if(byte != 0 or writeZeros or changeMode):
        if not verifyOnly:
            if changeMode:
                if(not readByte(addr) == byte):
                    setupWrite()
                    writeByte(addr, byte)
                    setupRead()
            else:
                writeByte(addr, byte)
    addr += 1
    line = f.readline()[:-1]

print("")
print("Verifying...")

setupRead()
foundError = False
for i in range(addr):
    if(readByte(i) != bytes[i]):
        print("I/O error: Byte "+str(i)+" invalid! expceted " + hex(bytes[i]) + ", read "+hex(readByte(i)))
        foundError = True

if not foundError:
    print("Success!")

GPIO.cleanup()
