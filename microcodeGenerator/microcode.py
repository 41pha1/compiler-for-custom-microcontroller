BI =    0x1
RI =    0x2
AI =    0x4
AO =    0x8
CE =    0x10
CO =    0x20
CS =    0x40
PI =    0x80
RO =    0x100
ALS =   0x200
ALO =   0x400
OI =    0x800
MI =    0x1000
STO =   0x2000
HLT =   0x4000
CS2 =   0x8000
BO =    0x10000
DI =    0x20000
DAI =   0x40000
ANO =   0x80000
ORO =   0x100000
LSO =   0x200000
SO =    0x400000
SI =    0x800000

length = 4096
program = []

CF = 1024
NZF = 2048

instructions = [
    [HLT],                                                                                    #0x00 HLT
    [CO | MI, STO | MI | CE, RO | OI],                                                        #0x01 OUTR
    [CO | MI, CE | STO | MI, RO | BI, ALO | AI],                                              #0x02 ADD
    [CO | MI, CE | STO | BI, ALO | AI],                                                       #0x03 ADDI
    [CO | MI, CE | STO | MI, RO | BI, CO | MI, CE | STO | MI, RO | AI, ALO | RI],             #0x04 ADDR
    [CO | MI, CE | STO | BI, CO | MI, CE | STO | MI, RO | AI, ALO | RI],                      #0x05 ADDIR
    [CO | MI, CE | STO | MI, RO | BI, CO | MI, CE | STO | MI, RO | AI, ALS | ALO | RI],       #0x06 SUBR
    [CO | MI, CE | STO | BI, CO | MI, CE | STO | MI, RO | AI, ALS | ALO | RI],                #0x07 SUBIR
    [CO | MI, CE | STO | MI, RO | BI, CO | MI, CE | STO | MI, RO | AI, ANO | RI],             #0x08 ANDR
    [CO | MI, CE | STO | MI, RO | BI, CO | MI, CE | STO | MI, RO | AI, ORO | RI],             #0x09 ORR
    [CO | MI, CE | STO | MI, RO | AI, LSO | RI],                                              #0x0a LSR
    [CO | MI, CE | STO | MI, RI | AO],                                                        #0x0b STA
    [CO | MI, CE | STO | MI, RO | AI],                                                        #0x0c LDA
    [CO | MI, CE | STO | AI],                                                                 #0x0d LDAI
    [CO | MI, CE | STO | MI, RI | BO],                                                        #0x0e STB
    [CO | MI, CE | STO | MI, RO | BI],                                                        #0x0f LDB
    [CO | MI, CE | STO | SI, CO | MI, CE | STO | MI, RI | SO] ,                               #0x10 LDR
    [CO | MI, CE | STO | MI, RO | SI, CO | MI, CE | STO | MI, RI | SO],                       #0x11 CPR
    [CO | MI, STO | SI | CE, CO | MI, STO | CS2, SO | CS],                                    #0x12 JMP
    [CO | MI, STO | SI | CE, CO | MI, STO | CS2, SO | CS],                                    #0x13 JC
    [CO | MI, STO | SI | CE, CO | MI, STO | CS2, SO | CS],                                    #0x14 JZ
    [CO | MI, CE | STO | MI, RO | DAI, CO | MI, CE | STO | MI, RO | DI],                      #0x15 DSPR
    [CO | MI, STO | MI, RO | MI, RO | SI, CO | MI, STO | MI | CE, SO | RI],                   #0x16 RESI    addr1 addr2     write contents at the address at addr1 to addr2          
    [CO | MI, CE | STO | MI, RO | SI, CO | MI, STO | MI | CE, RO | MI, RI | SO],              #0x17 PUT     addr1 addr2     write contents at addr1 to the address at addr2
    [CO | MI, STO | MI | CE, RO | MI, RO | SI, CO | MI, STO | MI | CE, SO | RI],              #0x18 RES     addr1 addr2     write contents at the address at addr1 to the address at addr2
    []
]

onlyIfCarryFlagSet = [0x13]
onlyIfZeroFlagSet = [0x14]

for i in range(length):
    program.append(0)

for flag in range(4):

    carry = flag % 2 == 1
    zero = flag < 2

    for cmd in range(64):
        for step in range(16):
            index = flag*1024+cmd*16+step

            if step == 0:
                program[index] = CO | MI
            if step == 1:
                program[index] = PI | CE | STO
            if step > 1:
                if (not carry and cmd in onlyIfCarryFlagSet) or (not zero and cmd in onlyIfZeroFlagSet):
                    if step == 2:
                        program[index] = CE
                    if step == 3:
                        program[index] = CE
                    continue
                if cmd < len(instructions):
                    if (step-2) < len(instructions[cmd]):
                        program[index] = instructions[cmd][step-2]
                #    else:
                #        program[index] = SKP

f = open("microcode.txt", "w")
f.write("v2.0 raw\n")

for i in range(int(length)):
    f.write(hex(program[i])[2:]+"\n")
f.close()
