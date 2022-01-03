import re
import struct
import sys

reg_ip          = 0
reg_shift       = 1
reg_sp          = 2
reg_out_value   = 3
reg_out_int     = 4
reg_in_value    = 5
reg_in_int      = 6
reg_z           = 7
reg_zero_flag   = 8
reg_carry_flag  = 9

#special address for testing
test1           = 15
test2           = 16

class CLabel():
    def __init__(self, name, addr):
        self.name = name
        self.addr = addr

class CAssembler():
    def __init__(self):
        self.opcode = b""
        self.currentIP = 300
        self.labelList = []
        self.relocList = []
        return
    
    def CookOp(self, value, relocAddr):
        if type(value) == int:
            return value
        
        cookedValue = 0xDEAD
        if value.isnumeric():
            cookedValue = int(value)
        elif re.match("([a-zA-Z0-9_]+)", value):
            #We may got label. So add to reloc list
            cookedValue = 0xC0DE
            self.relocList.append(CLabel(value, relocAddr))
        else:
            print("Error unknown value: %s" % value)
        
        return cookedValue
    
    def GenNative(self, value):
        cookedValue = self.CookOp(value, self.currentIP)
        self.opcode += struct.pack("<H", cookedValue)
        self.currentIP += 1
        return self.currentIP
    
    def GenNor(self, a, b, r):
        cooked_a = self.CookOp(a, self.currentIP)
        cooked_b = self.CookOp(b, self.currentIP + 1)
        cooked_r = self.CookOp(r, self.currentIP + 2)
        
        self.opcode += struct.pack("<HHH", cooked_a, cooked_b, cooked_r)
        self.currentIP += 3
        return self.currentIP
    
    def GenNot(self, a, r):
        self.GenNor(a, a, r)
        return self.currentIP
        
    def GenOr(self, a, b, r):
        self.GenNor(a, b, reg_z)
        self.GenNot(reg_z, r)
        return self.currentIP
    
    def GenMov(self, a, r):
        self.GenOr(a, a, r)
        return self.currentIP
        
    def GenJmp(self, a):
        self.GenMov(a, reg_ip)
        return self.currentIP
    
    def GenJmpOverNative(self, listValue):
        #Calculate jmp destination
        jmpDst = self.currentIP + 7 + len(listValue)
        
        #Calculate address of jump. size of jmp instruction is 6 plus address to jmp is 7
        addrJmpDst = self.currentIP + 6
        self.GenJmp(addrJmpDst)
        
        #Generate jmpDst and store to address
        self.GenNative(jmpDst)
        for value in listValue:
            self.GenNative(value)
        
        return self.currentIP
    
    def GenExit(self):
        ip = self.GenJmpOverNative([0xFFFF])
        self.GenMov(ip - 1, reg_ip)
        return self.currentIP
    
    def GenAnd(self, a, b, r):
        ip = self.GenJmpOverNative([0x0, 0x0])
        t1 = ip - 2
        t2 = ip - 1
        self.GenNot(a, t1)
        self.GenNot(b, t2)
        self.GenOr(t1, t2, reg_z)
        self.GenNot(reg_z, r)
        return self.currentIP
    
    def GenXor(self, a, b, r):
        ip = self.GenJmpOverNative([0x0, 0x0])
        t1 = ip - 2
        t2 = ip - 1
        self.GenNot(a, t1)
        self.GenNot(b, t2)
        self.GenAnd(a, t2, t2)
        self.GenAnd(b, t1, t1)
        self.GenOr(t1, t2, r)
        return self.currentIP
        
    def GenRol(self, a, r):
        self.GenMov(a, a)
        self.GenMov(reg_shift, r)
        return self.currentIP
        
    def GenRor(self, a, r):
        self.GenMov(a, r)
        for i in range(0, 15):
            self.GenRol(r, r)
        return self.currentIP
    
    def GenShl(self, a, b):
        ip = self.GenJmpOverNative([0xFFFE])
        const_FFFE = ip - 1
        self.GenRol(a, b)
        self.GenAnd(b, const_FFFE, b)
        return self.currentIP
        
    def GenShr(self, a, b):
        ip = self.GenJmpOverNative([0x7FFF])
        const_7FFF = ip - 1
        self.GenRor(a, b)
        self.GenAnd(b, const_7FFF, b)
        return self.currentIP
    
    def GenZero(self, a):
        ip = self.GenJmpOverNative([0x0])
        self.GenMov(ip - 1, a)
        return self.currentIP
        
    def GenPrintC(self, a):
        self.GenMov(a, reg_out_value)
        ip = self.GenJmpOverNative([0x1])
        self.GenMov(ip - 1, reg_out_int)
        return self.currentIP
    
    def GenScanC(self, a):
        ip = self.GenJmpOverNative([0x1])
        self.GenMov(ip - 1, reg_in_int)
        self.GenMov(reg_in_value, a)
        return self.currentIP
        
    #Now the most complicated part: ADD and ADC function
    def GenFAdd(self, mask, carry, a, b, r):
        ip = self.GenJmpOverNative([0x0, 0x0, 0x0, 0x0, 0x0])
        tmp_a = ip - 5
        tmp_b = ip - 4
        bit_r = ip - 3
        t1 = ip - 2
        t2 = ip - 1
        self.GenAnd(a, mask, tmp_a)
        self.GenAnd(b, mask, tmp_b)
        self.GenAnd(carry, mask, carry)
        
        self.GenXor(a, b, t1)
        self.GenXor(t1, carry, bit_r)
        
        self.GenAnd(bit_r, mask, bit_r)
        
        self.GenOr(bit_r, r, r)
        
        self.GenAnd(a, b, t2)
        self.GenAnd(carry, t1, t1)
        
        self.GenOr(t2, t1, carry)
        
        self.GenMov(reg_shift, carry)
        
        self.GenMov(mask, mask)
        self.GenMov(reg_shift, mask)
        
        self.GenAnd(carry, mask, carry)
        
        return self.currentIP
        
    def GenAdc(self, a, b, r):
        ip = self.GenJmpOverNative([0x1, 0x0, 0x0])
        const_1 = ip - 3
        mask = ip - 2
        t = ip - 1
        self.GenZero(t)
        self.GenMov(const_1, mask)
        for i in range(0, 16):
            self.GenFAdd(mask, reg_carry_flag, a, b, t)
        
        self.GenMov(t, r)
        self.GenZero(t)
        
        for i in range(0, 16):
            self.GenOr(t, reg_carry_flag, t)
            self.GenMov(reg_carry_flag, reg_carry_flag)
            self.GenMov(reg_shift, reg_carry_flag)
        
        self.GenMov(t, reg_carry_flag)
        return self.currentIP
        
    # Jump 'a', if cond = FFFF, and 'b' if cond = 0000
    def GenBranch(self, a, b, cond):
        ip = self.GenJmpOverNative([0x0, 0x0])
        t1 = ip - 2
        t2 = ip - 1
        self.GenAnd(a, cond, t1)
        self.GenNot(cond, t2)
        self.GenAnd(b, t2, t2)
        self.GenOr(t1, t2, reg_ip)
        return self.currentIP
    
    def GenIsZero(self, a):
        #Old function is zero generate too long function. So implement new instead
        #if a is zero, z flag = 0 else z flag = 0xFFFF
        ip = self.GenJmpOverNative([0x0])
        self.GenMov(ip - 1, reg_zero_flag)
        for i in range(0, 15):
            self.GenOr(reg_zero_flag, a, reg_zero_flag)
            self.GenRol(reg_zero_flag, reg_zero_flag)
        self.GenOr(reg_zero_flag, a, reg_zero_flag)
        return self.currentIP
        
    def GenJZ(self, a):
        skipLabel = self.currentIP + 75 #size of jz instruction is 75
        ip = self.GenJmpOverNative([a, skipLabel])
        jmpAddr = ip - 2
        skipAddr = ip - 1
        self.GenBranch(skipAddr, jmpAddr, reg_zero_flag)
        return self.currentIP
        
    def GenJNZ(self, a):
        skipLabel = self.currentIP + 75 #size of jnz instruction is 75
        ip = self.GenJmpOverNative([a, skipLabel])
        jmpAddr = ip - 2
        skipAddr = ip - 1
        self.GenBranch(jmpAddr, skipAddr, reg_zero_flag)
        return self.currentIP
        
    def GenAdd(self, a, b, r):
        #https://stackoverflow.com/questions/4068033/add-two-integers-using-only-bitwise-operators
        jmpBack = self.currentIP + 103
        #print(hex(self.currentIP))
        ip = self.GenJmpOverNative([jmpBack, 0x0, 0x0])
        
        #Calculate some value
        jmpBackAddr = ip - 3
        carry = ip - 2
        shiftedcarry = ip - 1
        
        #Calculate and vs xor result
        self.GenAnd(a, b, carry)
        self.GenXor(a, b, r)
        ip = self.currentIP
        
        #We calculate label again
        labelJmpout = ip + 520 #distance
        
        #print(hex(self.currentIP))
        self.GenIsZero(carry)
        self.GenJZ(labelJmpout)

        self.GenShl(carry, shiftedcarry)
        self.GenAnd(r, shiftedcarry, carry)
        self.GenXor(r, shiftedcarry, r)
        self.GenJmp(jmpBackAddr)
        
        #print(hex(self.currentIP))

        
        
        return self.currentIP
    
    def IsLabel(self, ins):
        if ins[0:1].isnumeric() == True:
            return False
            
        if re.match("([a-zA-Z0-9_]+:)", ins):
            return True
        return False
    
    def IsLabelExist(self, labelName):
        for labelObj in self.labelList:
            if labelObj.name == labelName:
                return True
        
        return False
        
    def AddNewLabel(self, name, addr):
        self.labelList.append(CLabel(name, addr))
    
    def SyncOperationToReg(self, operation):
        if operation.upper() == "REG_IP":
            return str(reg_ip)
        elif operation.upper() == "REG_SHIFT":
            return str(reg_shift)
        elif operation.upper() == "REG_SP":
            return str(reg_sp)
        elif operation.upper() == "REG_OUT_VALUE":
            return str(reg_out_value)
        elif operation.upper() == "REG_Z":
            return str(reg_z)
        elif operation.upper() == "REG_ZERO_FLAG":
            return str(reg_zero_flag)
        else:
            return operation
    
    def GetLabelObj(self, labelName):
        for labelObj in self.labelList:
            if labelObj.name == labelName:
                return labelObj
        
        return None
    
    def FixValueInOpcode(self, addr, newValue):
        offset = (addr - 300) * 2
        tmp = self.opcode[:offset] + struct.pack("<H", newValue) + self.opcode[offset + 2:]
        self.opcode = tmp
        return True
    
    def FixReloc(self):
        #seriously need to be checked
        for relocObj in self.relocList:
            labelObj = self.GetLabelObj(relocObj.name)
            if labelObj == None:
                print("Could not resolve label %s" % relocObj.name)
                return False
                
            self.FixValueInOpcode(relocObj.addr, labelObj.addr)
        return True
    
    def AssemblerLine(self, line):
        if line == "":
            return True
            
        if self.IsLabel(line):
            labelName = line[:-1]
            if self.IsLabelExist(labelName):
                print("Label %s already exist" % labelName)
                return False
            self.AddNewLabel(labelName, self.currentIP)
        else:
            #We got ops code. Parse line to opcode and operations
            spaceIndex = line.find(" ")
            operationList = []
            if spaceIndex != -1:
                opcode = line[:spaceIndex].strip()
                operationList = line[spaceIndex:].split(",")
            else:
                opcode = line.strip()
            
            for i in range(0, len(operationList)):
                operation = operationList[i].strip()
                operation = self.SyncOperationToReg(operation)
                operationList[i] = operation
            
            if opcode.upper() == "DB": #inline native bytes
                for item in operationList:
                    self.GenNative(item)
            elif opcode.upper() == "EXIT": #Exit opcode
                self.GenExit()
            elif opcode.upper() == "NOR": #Nor opcode
                if len(operationList) != 3:
                    print("invalid number of params for NOR instruction")
                    return False
                self.GenNor(operationList[0], operationList[1], operationList[2])
            elif opcode.upper() == "OR": #Or opcode
                if len(operationList) != 3:
                    print("invalid number of params for OR instruction")
                    return False
                self.GenOr(operationList[0], operationList[1], operationList[2])
            elif opcode.upper() == "NOT": #Not opcode
                if len(operationList) != 2:
                    print("invalid number of params for NOT instruction")
                    return False
                self.GenNot(operationList[0], operationList[1])
            elif opcode.upper() == "MOV": #Mov opcode
                if len(operationList) != 2:
                    print("invalid number of params for MOV instruction")
                    return False
                self.GenMov(operationList[0], operationList[1])
            elif opcode.upper() == "JMP": #Jmp opcode
                if len(operationList) != 1:
                    print("invalid number of params for JMP instruction")
                    return False
                ip = self.GenJmpOverNative([operationList[0]])
                self.GenJmp(ip - 1)
            elif opcode.upper() == "AND": #And opcode
                if len(operationList) != 3:
                    print("invalid number of params for AND instruction")
                    return False
                self.GenAnd(operationList[0], operationList[1], operationList[2])
            elif opcode.upper() == "XOR": #Xor opcode
                if len(operationList) != 3:
                    print("invalid number of params for XOR instruction")
                    return False
                self.GenXor(operationList[0], operationList[1], operationList[2])
            elif opcode.upper() == "ROL":
                if len(operationList) != 2:
                    print("invalid number of params for ROL instruction")
                    return False
                self.GenRol(operationList[0], operationList[1])
            elif opcode.upper() == "ROR":
                if len(operationList) != 2:
                    print("invalid number of params for ROR instruction")
                    return False
                self.GenRor(operationList[0], operationList[1])
            elif opcode.upper() == "ZERO":
                if len(operationList) != 1:
                    print("invalid number of params for ZERO instruction")
                    return False
                self.GenZero(operationList[0])
            elif opcode.upper() == "PRINTC":
                if len(operationList) != 1:
                    print("invalid number of params for PRINTC instruction")
                    return False
                self.GenPrintC(operationList[0])
            elif opcode.upper() == "SCANC":
                if len(operationList) != 1:
                    print("invalid number of params for SCANC instruction")
                    return False
                self.GenScanC(operationList[0])
            elif opcode.upper() == "ADC":
                if len(operationList) != 3:
                    print("invalid number of params for ADC instruction")
                    return False
                self.GenAdc(operationList[0], operationList[1], operationList[2])
            elif opcode.upper() == "IS_0":
                if len(operationList) != 1:
                    print("invalid number of params for IS_0 instruction")
                    return False
                self.GenIsZero(operationList[0])
            elif opcode.upper() == "JZ":
                if len(operationList) != 1:
                    print("invalid number of params for JZ instruction")
                    return False
                self.GenJZ(operationList[0])
            elif opcode.upper() == "JNZ":
                if len(operationList) != 1:
                    print("invalid number of params for JNZ instruction")
                    return False
                self.GenJNZ(operationList[0])
            elif opcode.upper() == "SHL":
                if len(operationList) != 2:
                    print("invalid number of params for SHL instruction")
                    return False
                self.GenShl(operationList[0], operationList[1])
            elif opcode.upper() == "SHR":
                if len(operationList) != 2:
                    print("invalid number of params for SHR instruction")
                    return False
                self.GenShr(operationList[0], operationList[1])
            elif opcode.upper() == "ADD":
                if len(operationList) != 3:
                    print("invalid number of params for ADD instruction")
                    return False
                self.GenAdd(operationList[0], operationList[1], operationList[2])
            else:
                print("Unknown: %s" % line)
                return False
            
        return True
        
    def CompileFile(self, input, output):
        f = open(input, "r")
        lines = f.read().split("\n")
        f.close()
        
        for i in range(0, len(lines)):
            if self.AssemblerLine(lines[i]) == False:
                print("Error at line %d" % (i + 1))
                return False
        self.FixReloc()
        
        f = open(output, "wb")
        f.write(assemblerObj.opcode)
        f.close()
        return 0

def test():
    assemblerObj = CAssembler()
    
    assemblerObj.AssemblerLine("add 15, 16, 15")
    assemblerObj.AssemblerLine("exit")
    assemblerObj.FixReloc()
    
    f = open("test.bin", "wb")
    f.write(assemblerObj.opcode)
    f.close()

if __name__ == "__main__":
    #test()
    
    if len(sys.argv) != 3:
        print("usage: nor_compiler.py input output")
    else:
        input = sys.argv[1]
        output = sys.argv[2]
        assemblerObj = CAssembler()
        assemblerObj.CompileFile(input, output)
    