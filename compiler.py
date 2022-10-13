import re

CMDS = {
"HLT" : 0x00,
"OUTR" : 0x01,
"ADD" : 0x02,
"ADDI" : 0x03,
"ADDR" : 0x04,
"ADDIR" : 0x05,
"SUBR" : 0x06,
"SUBIR" : 0x07,
"ANDR" : 0x08,
"ORR" : 0x09,
"LSR" : 0x0a,
"STA" : 0x0b,
"LDA" : 0x0c,
"LDAI" : 0x0d,
"STB" : 0x0e,
"LDB" : 0x0f,
"LDR" : 0x10,
"CPR" : 0x11,
"JMP" : 0x12,
"JC" : 0x13,
"JZ" : 0x14,
"DSPR" : 0x15,
"RESI" : 0x16,
"PUT" : 0x17,
"RES" : 0x18}

programFile  = "code.c"

vars = {}
program = []
operators = ["&&", "||", "==", "!=", "!", "&", "|", ">", ">=", "<", "<=", ">>", "<<", "+", "-"]
commutativeOperators = ["&&", "||", "|", "&", "==", "!=", "+"]
immediateOperators = ["-", "+", "==", "<=", ">=", ">", "<", "&&", "&", "||", "|", "!"]
assignOperators = ["=", "+=", "-=", ">>=", "<<=", "&=", "|="]
ramSize = 256
ramUsed = [False]*ramSize
protected = []
constant = False
constVal = 0
immediateMath = False
immediateConst = 0
ANYWHERE = -1

def is_digit(n):
    try:
        int(n)
        return True
    except ValueError:
        return  False

def getTokens(code):
    code = re.sub(r'[(){};\[\]]', r' \g<0> ', code)
    code = re.sub('>=|<=|\+=|-=|\|=|\!=|==|=|\+\+|\+|--|-|&=|>>=|>>=|>>|>>|\|\||\||&&|&|,', r' \g<0> ', code)
    code = re.sub(r'\s+', " ", code)
    code = re.sub(r'\s$', "", code)
    tokens = code.split(" ")

    for i in range(len(tokens)):
        if(tokens[i] == "true"):
            tokens[i] = "1"
        if(tokens[i] == "false"):
            tokens[i] = "0"
    return tokens

def ramUsage():
    used = 0
    for i in range(ramSize):
        if( ramUsed[i]):
            used += 1
    return used

def getFreeSpace():
    for i in range(ramSize):
        if not ramUsed[i]:
            ramUsed[i] = True
            return i
    error("out of memory")

def getArraySpace(length):
    index = 0
    freeSpaces = 0
    for i in range(ramSize):
        if not ramUsed[i]:
            freeSpaces += 1
            if(freeSpaces == length):
                for j in range(length):
                    ramUsed[index + j] = True
                    protected.append(index+j)
                return index
        else:
            freeSpaces = 0
            index = i + 1
    error("out of memory")

def freeupRam(addr):
    global ramUsed
    if not addr in protected:
        ramUsed[addr] = False

def getTokensFromFile(file):
    code = ""
    f = open(file, "r")
    for line in f:
        code += line
    return getTokens(code)

def error(err):
    print(err)
    exit()

def addToProgram(bytes):
    for byte in bytes:
        if byte in CMDS:
            print(str(len(program))+": ", byte, end = " ")
            byte = CMDS[byte]
        else:
            displayByte = byte
            if displayByte < -128:
                displayByte += 256
            print(displayByte, end = " ")
        while(byte < 0):
            byte += 256
        program.append(byte % 256)
    print("")

def getPostifixNotation(tokens):
    stack = []
    postfix = []
    index = 0
    while(index < len(tokens)):
        if(is_digit(tokens[index])):
            postfix.append(tokens[index])
        elif tokens[index].split("[")[0] in vars:
            postfix.append(tokens[index])
        elif(tokens[index] == "("):
            stack.append("(")
        elif(tokens[index] == ")"):
            while(stack[-1] != "("):
                postfix.append(stack.pop())
            stack.pop()
        elif tokens[index] in operators:
            while len(stack)>0 and stack[-1] in operators:
                if operators.index(tokens[index]) <= operators.index(stack[-1]):
                    postfix.append(stack.pop())
                else:
                    break
            stack.append(tokens[index])
        else:
            error(tokens[index] + " is not a valid arithmetic token")
        index += 1
    while(len(stack) != 0):
        postfix.append(stack.pop())
    return postfix

def getPrefixNotation(tokens, index):
    infix = []
    openBrackets = 1
    while(openBrackets != 0 and tokens[index] != ";" and tokens[index] !="]" and tokens[index] !=","):
        if(tokens[index] == "-" and not (is_digit(tokens[index - 1]) or tokens[index - 1] in vars)):
            infix.append("0")
        infix.append(tokens[index])
        if(tokens[index] == "("):
            openBrackets +=1
        elif(tokens[index] == ")"):
            openBrackets -= 1
            if(openBrackets == 0):
                infix.pop()
        if tokens[index] in vars:
            if tokens[index + 1] == "[":
                innerOpenBrackets = 1
                infix[-1]+=(tokens[index+1])
                index += 2
                while(innerOpenBrackets != 0):
                    if(tokens[index] == "["):
                        innerOpenBrackets+=1
                    elif tokens[index] == "]":
                        innerOpenBrackets-=1
                    infix[-1]+=(tokens[index])
                    index += 1
                index -= 1
        index+=1
    infix.reverse()
    for i in range(len(infix)):
        if(infix[i] == "("):
            infix[i] = ")"
        elif(infix[i] == ")"):
            infix[i] = "("
    postfix = getPostifixNotation(infix)
    postfix.reverse()
    prefix = postfix
    return prefix, index

def isBiggerEquals(par1, par2):
    if(immediateMath):
        addToProgram(["SUBIR", immediateConst, par2])
    else:
        addToProgram(["SUBR", par1, par2])
    addToProgram(["JC", (len(program)+9) % 256, (len(program)+9) >> 8])
    addToProgram(["LDR", 0, par2])
    addToProgram(["JMP", (len(program)+6) % 256, (len(program)+6) >> 8])
    addToProgram(["LDR", 1, par2])

def isBigger(par1, par2):
    if(immediateMath):
        addToProgram(["SUBIR", immediateConst + 1, par2])
    else:
        addr = getFreeSpace()
        addToProgram(["CPR", par1, addr])
        addToProgram(["ADDIR", 1, addr])
        addToProgram(["SUBR", addr, par2])
        freeupRam(addr)
    addToProgram(["JC",  (len(program)+9) % 256, (len(program)+9) >> 8])
    addToProgram(["LDR", 0, par2])
    addToProgram(["JMP", (len(program)+6) % 256, (len(program)+6) >> 8])
    addToProgram(["LDR", 1, par2])

def isSmallerEquals(par1, par2):
    if(immediateMath):
        addToProgram(["SUBIR", immediateConst + 1, par2])
    else:
        addr = getFreeSpace()
        addToProgram(["CPR", par1, addr])
        addToProgram(["ADDIR", 1, addr])
        addToProgram(["SUBR", addr, par2])
        freeupRam(addr)
    addToProgram(["JC",  (len(program)+9) % 256, (len(program)+9) >> 8])
    addToProgram(["LDR", 1, par2])
    addToProgram(["JMP", (len(program)+6) % 256, (len(program)+6) >> 8])
    addToProgram(["LDR", 0, par2])

def isSmaller(par1, par2):
    if(immediateMath):
        addToProgram(["SUBIR", immediateConst, par2])
    else:
        addToProgram(["SUBR", par1, par2])
    addToProgram(["JC",  (len(program)+9) % 256, (len(program)+9) >> 8])
    addToProgram(["LDR", 1, par2])
    addToProgram(["JMP", (len(program)+6) % 256, (len(program)+6) >> 8])
    addToProgram(["LDR", 0, par2])

def isEqual(par1, par2):
    if(immediateMath):
        addToProgram(["SUBIR", immediateConst, par2])
    else:
        addToProgram(["SUBR", par1, par2])
    addToProgram(["JZ", (len(program)+9) % 256, (len(program)+9) >> 8])
    addToProgram(["LDR", 0, par2])
    addToProgram(["JMP", (len(program)+6) % 256, (len(program)+6) >> 8])
    addToProgram(["LDR", 1, par2])

def isNotEqual(par1, par2):
    if(immediateMath):
        addToProgram(["SUBIR", immediateConst, par2])
    else:
        addToProgram(["SUBR", par1, par2])
    addToProgram(["JZ", (len(program)+9) % 256, (len(program)+9) >> 8])
    addToProgram(["LDR", 1, par2])
    addToProgram(["JMP", (len(program)+6) % 256, (len(program)+6) >> 8])
    addToProgram(["LDR", 0, par2])

def iterateExpression(tokens, index, addr, depth):
    global constant, constVal, immediateMath, immediateConst
    if(tokens[index] in operators):
        const1 = 0
        const2 = 0
        is1const = False
        is2const = False
        constantMath = False

        par1, offset1 = iterateExpression(tokens, index+1, addr, depth + 1)
        if(constant):
            is1const = True
            const1 = constVal

        par2, offset2 = iterateExpression(tokens, index+1+offset1, -1, depth + 1)
        if(constant):
            is2const = True
            const2 = constVal

        offset = offset1+offset2+1

        immediateMath = False
        immediateConst = 0

        constant = False
        if(is1const and is2const):
            constantMath = True
            constant = True
        elif(is1const):
            if(addr == ANYWHERE):
                addr = getFreeSpace()
            addToProgram(["LDR", const1, addr])
            par1 = addr
        elif(is2const):
            if(addr == ANYWHERE):
                addr = getFreeSpace()
            if(tokens[index] in immediateOperators):
                immediateMath = True
                immediateConst = const2
                if(par1 != addr):
                    addToProgram(["CPR", par1, addr])
                    par1 = addr
            elif(tokens[index] in commutativeOperators):
                addToProgram(["LDR", const2, addr])
                par2 = par1
                par1 = addr
            else:
                par2 = getFreeSpace()
                addToProgram(["LDR", const2, par2])

        if(par1 in vars.values() and par1 != addr):
            if(addr == ANYWHERE):
                addr = getFreeSpace()
            newPar1 = addr
            addToProgram(["CPR", par1, newPar1])
            par1 = newPar1

        if(tokens[index] == "+"):
            if(constantMath):
                constVal = const1 + const2
                par1 = ANYWHERE
            elif(immediateMath):
                addToProgram(["ADDIR", immediateConst, par1])
            else:
                addToProgram(["ADDR", par2, par1])
        elif(tokens[index] == "-"):
            if(constantMath):
                constVal = const1 - const2
                par1 = ANYWHERE
            elif(immediateMath):
                addToProgram(["SUBIR", immediateConst, par1])
            else:
                addToProgram(["SUBR", par2, par1])
        elif(tokens[index] == "&" or tokens[index] == "&&"):
            if(constantMath):
                constVal = const1 & const2
                par1 = ANYWHERE
            elif(immediateMath):
                addr = getFreeSpace()
                addToProgram(["LDR", immediateConst, addr])
                addToProgram(["ANDR", addr, par1])
                freeupRam(addr)
            else:
                addToProgram(["ANDR", par2, par1])
        elif(tokens[index] == "|" or tokens[index] == "||"):
            if(constantMath):
                constVal = const1 & const2
                par1 = ANYWHERE
            elif(immediateMath):
                addr = getFreeSpace()
                addToProgram(["LDR", immediateConst, addr])
                addToProgram(["ORR", addr, par1])
                freeupRam(addr)
            else:
                addToProgram(["ORR", par2, par1])
        elif(tokens[index] == "=="):
            if(constantMath):
                constVal = int(const2 == const1)
                par1 = ANYWHERE
            else:
                isEqual(par2, par1)
        elif(tokens[index] == "!="):
            if(constantMath):
                constVal = int(const2 != const1)
                par1 = ANYWHERE
            else:
                isNotEqual(par2, par1)
        elif(tokens[index] == ">"):
            if(constantMath):
                constVal = int(const1 > const2)
                par1 = ANYWHERE
            else:
                isBigger(par2, par1)
        elif(tokens[index] == "<"):
            if(constantMath):
                constVal = int(const1 < const2)
                par1 = ANYWHERE
            else:
                isSmaller(par2, par1)
        elif(tokens[index] == ">="):
            if(constantMath):
                constVal = int(const1 >= const2)
                par1 = ANYWHERE
            else:
                isBiggerEquals(par2, par1)
        elif(tokens[index] == "<="):
            if(constantMath):
                constVal = int(const1 <= const2)
                par1 = ANYWHERE
            else:
                isSmallerEquals(par2, par1)
        else:
            error(tokens[index]+" is an unsupported operator")
        freeupRam(par2)
        return par1, offset
    else:
        result = 0
        if tokens[index].split("[")[0] in vars:
            constant = False
            if len(tokens[index].split("[")) > 1:
                indexTokens = getTokens(tokens[index])[2:]
                indexRes = getFreeSpace()
                off = evaluateExpression(indexTokens, 0, indexRes)
                addToProgram(["ADDIR", vars[tokens[index].split("[")[0]], indexRes, "RESI", indexRes])
                result = indexRes
            else:
                result = vars[tokens[index]]
        elif is_digit(tokens[index]):
            constant = True
            constVal = int(tokens[index])
            result = ANYWHERE
        else:
            error(tokens[index] +" is an unexpected expression token")
        return result, 1

def evaluateExpression(tokens, index, addr):
    prefix, index = getPrefixNotation(tokens, index)
    print(prefix)
    result, off = iterateExpression(prefix, 0, addr, 0)

    if(constant):
        addToProgram(["LDR", constVal, addr])

    elif(result != addr):
        addToProgram(["CPR", result, addr])
        result = addr
        #if not result in vars.values():
        #    freeupRam(result)
    return index

def evaluateExpressionAnywhere(tokens, index):
    prefix, index = getPrefixNotation(tokens, index)
    print(prefix)
    result, off = iterateExpression(prefix, 0, -1, 0)

    if(constant):
        result = getFreeSpace()
        addToProgram(["LDR", constVal, result])

    return index, result

def evaluateExpressionFlags(tokens, index):
    prefix, index = getPrefixNotation(tokens, index)
    print(prefix)
    result, off = iterateExpression(prefix, 0, -1, 0)

    if(constant):
        result = getFreeSpace()
        addToProgram(["LDR", constVal, result])

    addToProgram(["ADDIR", 0, result])
    freeupRam(result)
    return index

def setVariable(tokens, index):
    var = vars[tokens[index]]
    if(tokens[index+1] == "["):
        indexRes = getFreeSpace()
        index = evaluateExpression(tokens, index+2, indexRes)
        if(var != 0):
            addToProgram(["ADDIR", var, indexRes])
        if(tokens[index+1] == "="):
            res = getFreeSpace()
            index =  evaluateExpression(tokens, index+2, res) +1
            addToProgram(["PUT", res, indexRes])
            freeupRam(res)
            return index

        error(tokens[index + 1]+ " is an invalid array set operator")
    else:
        if(tokens[index+1] == "="):
            return evaluateExpression(tokens, index+2, var) +1
        error(tokens[index]+ " is an invalid var set operator")

def addVar(tokens, index):
    index += 1

    if(tokens[index+1] == "["):
        if(is_digit(tokens[index+2]) and tokens[index+3] == "]"):
            vars[tokens[index]] = getArraySpace(int(tokens[index+2]))
            index += 3
        else:
            error("array size must be constant")
    else:
        vars[tokens[index]] = getFreeSpace()
        protected.append(vars[tokens[index]])

    if(tokens[index+1] == "="):
        index = setVariable(tokens, index)
        if(tokens[index-1] == ";"):
            return index
        if(tokens[index-1] == ","):
            return addVar(tokens, index-1)
        error("Expected ; or ,")
    if(tokens[index+1 == ";"]):
        return index + 2
    error("Expected = or ;")

def combine(tokens, index):
    return index

def evaluateParantheses(tokens, index):
    return index

def ifStatement(tokens, index):
    if(tokens[index+1] != "("):
        error("invalid if statement")
    index = evaluateExpressionFlags(tokens, index+2)
    addToProgram(["JZ", 0, 0])
    ENDpointer = len(program)-2
    index = evaluateStatement(tokens, index)
    program[ENDpointer] = len(program) % 256
    program[ENDpointer+1] = len(program) >> 8
    return index

def printFunction(tokens, index):
    index, result = evaluateExpressionAnywhere(tokens, index+2)
    addToProgram(["OUTR", result])
    freeupRam(result)
    return index

def displayFunction(tokens, index):
    index, addr = evaluateExpressionAnywhere(tokens, index+2)
    index, res = evaluateExpressionAnywhere(tokens, index+1)
    addToProgram(["DSPR", addr, res])
    freeupRam(addr)
    freeupRam(res)
    return index

def forLoop(tokens, index):
    index += 2
    if(tokens[index] == "int"):
        index = addVar(tokens, index)
    elif(tokens[index] in vars):
        index = setVariable(tokens, index)
    else:
        error("Invalid For Loop")

    startIndex = len(program)
    index = evaluateExpressionFlags(tokens,  index)
    increaseIndex = index + 1

    addToProgram(["JZ", 0, 0])
    ENDpointer = len(program)-2

    openBrackets = 1
    while(openBrackets != 0):
        index += 1
        if(tokens[index] == "("):
            openBrackets +=1
        if(tokens[index] == ")"):
            openBrackets -=1

    index = evaluateStatement(tokens, index+1)
    setVariable(tokens, increaseIndex)
    addToProgram(["JMP", startIndex % 256, startIndex >> 8])
    program[ENDpointer] = len(program) % 256
    program[ENDpointer+1] = len(program) >> 8
    return index

def whileLoop(tokens, index):
    index += 2
    startIndex = len(program)
    index = evaluateExpressionFlags(tokens,  index)
    addToProgram(["JZ", 0, 0])
    ENDpointer = len(program)-2

    index = evaluateStatement(tokens, index)
    addToProgram(["JMP", startIndex % 256, startIndex >> 8])
    program[ENDpointer] = len(program) % 256
    program[ENDpointer+1] = len(program) >> 8
    return index

def evaluateStatement(tokens, index):
    if(tokens[index] == "{"):
        index += 1
        while tokens[index] != "}":
            index = evaluateStatement(tokens, index)
        return index + 1

    if(tokens[index] == "int"):
        return addVar(tokens, index)

    if(tokens[index] in vars):
        return setVariable(tokens, index)

    if(tokens[index] == "for"):
        return forLoop(tokens, index)

    if(tokens[index] == "while"):
        return whileLoop(tokens, index)

    if(tokens[index] == "print"):
        return printFunction(tokens, index)

    if(tokens[index] == "display"):
        return displayFunction(tokens, index)

    if(tokens[index] == "if"):
        return ifStatement(tokens, index)

    if(tokens[index] == ";"):
        return index +1

    error(tokens[index] + " is not a valid identifier")

def translate(tokens, index):
    while(index < len(tokens)):
        index = evaluateStatement(tokens, index)


tokens = getTokensFromFile(programFile)
print(tokens)
translate(tokens, 0)
addToProgram(["HLT"])

print("Ram Usage: "+str(ramUsage()) + " bytes")

o = open("out.txt", "w")
o.write("v2.0 raw\n")

for i in range(len(program)):
    o.write(hex(program[i])[2:]+"\n")
    #print(str(i)+": "+str(program[i]))
