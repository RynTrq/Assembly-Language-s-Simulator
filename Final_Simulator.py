wInstructions=list()
MM=list()
Mem=list()
Errors=list()
labels=list()
variables=list()
Registers=list()
var_values=[]
program_counter=0
'''print("Give the assembly code as input(to end giving input type'hogya'):")
i=1
while True:
    print("Line",i,":",end=" ")
    a=input()
    a.strip()
    if a=='hogya':
        break
    else:
        Instructions.append(a)
        i+=1
for i in range(len(Instructions)):
    a=Instructions[i].split()
    Instructions[i]=[i+1]
    for j in range(len(a)):
        Instructions[i].append(a[j])'''




#Making all the Instructions locations get to a value zero.
for i in range(0,128):
        Mem.append(0)
for i in range(0,128):
        MM.append(0)
for i in range(0,8):
    Registers.append('0000000000000000')
for i in range(0,128):
        var_values.append(0)




#Functions definition
def todecimal(n,bit):
    va=0
    for i in range(0,bit):
        a=int(n[bit-1-i])
        va=va+a*(2**i)
    return va
def todecimalf(n,bit):
    va=0
    dp=bit
    for i in range(len(n)):
        if n[i]=='.':
            dp=i
            break
    for i in range(dp):
        va=va+int(n[dp-i-1])*(2**i)
    for i in range(dp+1,len(n)):
        va=va+int(n[i])*(2**(-1*(i-dp)))
    return va
def tobinary(n,bit):
    if n==0:
        return '0'*bit
    temp_lst=[]
    while n>0:
        q=n//2
        r=n%2
        temp_lst.append(r)
        n=q
    va=0
    for tt in range(0,len(temp_lst)):
        va=va+temp_lst[tt]*(10**(tt))
    x=bit-len(temp_lst)
    va=str(va)
    va='0'*x+va
    return va
def tobinaryf_(n):
    n0=int(n)
    n1=n-int(n)
    temp_lst=[]
    if n0==0:
        va='0'
    else:
        while n0>0:
            q=n0//2
            r=n0%2
            temp_lst.append(r)
            n0=q
        c=len(temp_lst)
        va=str(temp_lst[-1])
        for tt in range(1,c):
            va=va+str(temp_lst[c-tt-1])
    temp_lst=[]
    if n1==0:
        vb='0'
    else:
        while n1!=0:
            m=n1*2
            m0=int(m)
            m1=m-int(m)
            temp_lst.append(m0)
            n1=m1
        c=len(temp_lst)
        vb=str(temp_lst[0])
        for tt in range(1,c):
            vb=vb+str(temp_lst[tt])
    v=va+'.'+vb
    return v
def tobinary_f(n,bit):
    n0=int(n)
    n1=n-int(n)
    temp_lst=[]
    if n0==0:
        va='0'
    else:
        while n0>0:
            q=n0//2
            r=n0%2
            temp_lst.append(r)
            n0=q
        c=len(temp_lst)
        va=str(temp_lst[-1])
        for tt in range(1,c):
            va=va+str(temp_lst[c-tt-1])
    temp_lst=[]
    if n1==0:
        vb='0'
    else:
        while n1!=0:
            m=n1*2
            m0=int(m)
            m1=m-int(m)
            temp_lst.append(m0)
            n1=m1
        c=len(temp_lst)
        vb=str(temp_lst[0])
        for tt in range(1,c):
            vb=vb+str(temp_lst[tt])
    v=va+'.'+vb
    return '0'*(bit-len(v))+v
def reg_add(inpp):
    if inpp=='R0':
        return '000'
    elif inpp=='R1':
        return '001'
    elif inpp=='R2':
        return '010'
    elif inpp=='R3':
        return '011'
    elif inpp=='R4':
        return '100'
    elif inpp=='R5':
        return '101'
    elif inpp=='R6':
        return '110'
    elif inpp=='FLAGS':
        return '111'
def checkins(ins):
    lst=['add','sub','mov','ld','st','mul','div','rs','ls','xor','or','and','not','cmp','jmp','jlt','jgt','je','hlt','addf','subf','movf']
    if ins[1] in lst:
        return True
    else:
        return False
def checkregister(a):
    lst=['R0','R1','R2','R3','R4','R5','R6','FLAGS']
    if a in lst:
        return True
    else:
        return False
def checktype(ins):
    if len(ins)<2:
        return None
    lst=['add','sub','mul','xor','or','and','addf','subf']
    if ins[1] in lst:
        return 'A'
    lst=['ld','st']
    if ins[1] in lst:
        return 'D'
    lst=['jmp','jlt','jgt','je']
    if ins[1] in lst:
        return 'E'
    lst=['hlt']
    if ins[1] in lst:
        return 'F'
    lst=['rs','ls',]
    if ins[1] in lst:
        return 'B'
    lst=['movf']
    if ins[1] in lst:
        return 'B0'
    lst=['div','not','cmp']
    if ins[1] in lst:
        return 'C'
    if ins[1]=='mov':
        if checkregister(ins[3])==True:
            return 'C'
    if ins[1]=='mov':
        if checkregister(ins[3])==False:
            return 'B'
    return None
def islabel(a):
    if a[-1]==':' and a[-2]!=' ':
        return True
    else:
        return False


'''for i in range(len(Instructions)):
    if checktype(Instructions[i])=='B' or checktype(Instructions[i])=='B0':
        if Instructions[i][3][0]=='&':
            if len(Instructions[i][3])==2:
                    Instructions[i][3]=Instructions[i][3][1]
            elif len(Instructions[i][3])>2:
                bb=Instructions[i][3][1]
                for j in range(2,len(Instructions[i][3])):
                    bb=bb+Instructions[i][3][j]
                Instructions[i][3]=bb
print("Instructions",Instructions)'''


'''#Error Handling
for i in range(len(Instructions)):
    if len(Instructions[i])>1:
        if islabel(Instructions[i][1])==True and len(Instructions[i])>2:
            aa='Line no:'+str(Instructions[i][0])+" - Invalid indentation after label."
            Errors.append(aa)
        if checkins(Instructions[i])==True or Instructions[i][1]=='var' or islabel(Instructions[i][1])==True:
            if checktype(Instructions[i])=='A':
                if len(Instructions[i])!=5:
                    aa="Line no:"+str(Instructions[i][0])+' - Invalid instruction format.'
                    Errors.append(aa)
                    print(aa)
                    quit()
                if checkregister(Instructions[i][2])==False:
                    aa="Line no:"+str(Instructions[i][0])+" - Invalid register name-"+Instructions[i][2]
                    Errors.append(aa)
                if checkregister(Instructions[i][3])==False:
                    aa="Line no:"+str(Instructions[i][0])+" - Invalid register name-"+Instructions[i][3]
                    Errors.append(aa)
                if checkregister(Instructions[i][4])==False:
                    aa="Line no:"+str(Instructions[i][0])+" - Invalid register name-"+Instructions[i][4]
                    Errors.append(aa)
            if checktype(Instructions[i])=='B' or checktype(Instructions[i])=='B0':
                if len(Instructions[i])!=4:
                    aa="Line no:"+str(Instructions[i][0])+' - Invalid instruction format.'
                    Errors.append(aa)
                    print(aa)
                    quit()
                if checkregister(Instructions[i][2])==False:
                    aa="Line no:"+str(Instructions[i][0])+" - Invalid register name-",Instructions[i][2]
                    Errors.append(aa)
                try:
                    if float(Instructions[i][3])-int(float(Instructions[i][3]))==0:
                        if float(Instructions[i][3])>=0 and float(Instructions[i][3])<128:
                            continue
                        else:
                            aa="Line no:"+str(Instructions[i][0])+" - Immediate value out of range-",Instructions[i][3]
                            Errors.append(aa)
                    elif checktype(Instructions[i])=='B0':
                        if len(tobinaryf_(float(Instructions[i][3])))>8:
                            aa="Line no:"+str(Instructions[i][0])+" - Immediate value cannot be contained within 8 bits-",Instructions[i][3]
                            Errors.append(aa)
                    else:
                        aa="Line no:"+str(Instructions[i][0])+" - Immediate value not a whole number-",Instructions[i][3]
                        Errors.append(aa)
                except:
                    aa="Line no:"+str(Instructions[i][0])+" - Invalid immediate value-",Instructions[i][3]
                    Errors.append(aa)
            if checktype(Instructions[i])=='C':
                if len(Instructions[i])!=4:
                    aa="Line no:"+str(Instructions[i][0])+' - Invalid instruction format.'
                    Errors.append(aa)
                    print(aa)
                    quit()
                if checkregister(Instructions[i][2])==False:
                    aa="Line no:"+str(Instructions[i][0])+" - Invalid register name-",Instructions[i][2]
                    Errors.append(aa)
                if checkregister(Instructions[i][3])==False and Instructions[i][3]!='FLAGS':
                    aa="Line no:"+str(Instructions[i][0])+" - Invalid register name-",Instructions[i][3]
                    Errors.append(aa)
            if checktype(Instructions[i])=='D':
                if len(Instructions[i])!=4:
                    aa="Line no:"+str(Instructions[i][0])+' - Invalid instruction format.'
                    Errors.append(aa)
                    print(aa)
                    quit()
                if checkregister(Instructions[i][2])==False:
                    aa="Line no:"+str(Instructions[i][0])+" - Invalid register name-",Instructions[i][2]
                    Errors.append(aa)
            if checktype(Instructions[i])=='E':
                if len(Instructions[i])!=3:
                    aa="Line no:"+str(Instructions[i][0])+' - Invalid instruction format.'
                    Errors.append(aa)
                    print(aa)
                    quit()
            if checktype(Instructions[i])=='F':
                if len(Instructions[i])!=2:
                    aa="Line no:"+str(Instructions[i][0])+' - Invalid instruction format.'
                    Errors.append(aa)
                    print(aa)
                    quit()
            if Instructions[i][1]=='var':
                if len(Instructions[i])!=3:
                    aa="Line no:"+str(Instructions[i][0])+' - Invalid instruction format.'
                    Errors.append(aa)
                    print(aa)
                    quit()
        else:
            aa="Line no:"+str(Instructions[i][0])+" - Invalid insruction-"+Instructions[i][1]
            Errors.append(aa)
hlt_c=0
hlt_i=0
for i in range(len(Instructions)):
    if len(Instructions[i])>1:
        if Instructions[i][1]=='hlt':
            hlt_c=hlt_c+1
        elif hlt_c>0:
            hlt_i=hlt_i+1
    if hlt_c>1:
        aa="There are multiple 'hlt' instructions in the program."
        Errors.append(aa)
    if hlt_i>0:
        aa="There are instructions even after the 'hlt' instruction."
        Errors.append(aa)
if hlt_c==0:
    aa="There's no 'hlt' instruction in the program."
    Errors.append(aa)



#Saving intruction coded in binary to Memory.
ins_count=0
for i in range(len(Instructions)):
    if len(Instructions[i])>1:
        if islabel(Instructions[i][1])==True:
            if Instructions[i][1] in labels:
                aa="Line no:"+str(Instructions[i][0])+" - Label being defined for the second time!"
                Errors.append(aa)
            else:
                labels.append(Instructions[i][1])
                Mem[ins_count]=Instructions[i][1]
                ins_count=ins_count+1
        elif Instructions[i][1]=='var':
            if Instructions[i][2] in variables:
                continue
            else:
                variables.append(Instructions[i][2])
                Mem[127-(variables.index(Instructions[i][2]))]=Instructions[i][2]
        elif checktype(Instructions[i])=='A':
            if Instructions[i][1]=='add':
                Mem[ins_count]=['00000']
            elif Instructions[i][1]=='addf':
                Mem[ins_count]=['10000']
            elif Instructions[i][1]=='sub':
                Mem[ins_count]=['00001']
            elif Instructions[i][1]=='subf':
                Mem[ins_count]=['10001']
            elif Instructions[i][1]=='mul':
                Mem[ins_count]=['00110']
            elif Instructions[i][1]=='xor':
                Mem[ins_count]=['01010']
            elif Instructions[i][1]=='or':
                Mem[ins_count]=['01011']
            elif Instructions[i][1]=='and':
                Mem[ins_count]=['01100']
            Mem[ins_count].append('00')
            Mem[ins_count].append(reg_add(Instructions[i][2]))
            Mem[ins_count].append(reg_add(Instructions[i][3]))
            Mem[ins_count].append(reg_add(Instructions[i][4]))
            ins_count=ins_count+1
        elif checktype(Instructions[i])=='B' or checktype(Instructions[i])=='B0':
            if Instructions[i][1]=='mov':
                Mem[ins_count]=['00010']
            elif Instructions[i][1]=='movf':
                Mem[ins_count]=['10010']
            elif Instructions[i][1]=='rs':
                Mem[ins_count]=['01000']
            elif Instructions[i][1]=='ls':
                Mem[ins_count]=['01001']
            if checktype(Instructions[i])=='B':
                Mem[ins_count].append('0')
            Mem[ins_count].append(reg_add(Instructions[i][2]))
            if checktype(Instructions[i])=='B':
                Mem[ins_count].append(tobinary((int(float(Instructions[i][3]))),7))
            else:
                Mem[ins_count].append(tobinary_f(float(Instructions[i][3]),8))
            ins_count=ins_count+1
        elif checktype(Instructions[i])=='C':
            if Instructions[i][1]=='mov':
                Mem[ins_count]=['00011']
            elif Instructions[i][1]=='div':
                Mem[ins_count]=['00111']
            elif Instructions[i][1]=='not':
                Mem[ins_count]=['01101']
            elif Instructions[i][1]=='cmp':
                Mem[ins_count]=['01110']
            Mem[ins_count].append('00000')
            Mem[ins_count].append(reg_add(Instructions[i][2]))
            Mem[ins_count].append(reg_add(Instructions[i][3]))
            ins_count=ins_count+1
        elif checktype(Instructions[i])=='D':
            if Instructions[i][1]=='ld':
                Mem[ins_count]=['00100']
            elif Instructions[i][1]=='st':
                Mem[ins_count]=['00101']
            Mem[ins_count].append('0')
            Mem[ins_count].append(reg_add(Instructions[i][2]))
            if Instructions[i][3] not in Mem:
                continue
            elif Instructions[i][3] in Mem:
                Mem[ins_count].append(tobinary(Mem.index(Instructions[i][3]),7))
            ins_count=ins_count+1
        elif checktype(Instructions[i])=='E':
            nn=Instructions[i][2]+':'
            if Instructions[i][1]=='jmp':
                Mem[ins_count]=['01111']
            if Instructions[i][1]=='jlt':
                Mem[ins_count]=['11100']
            if Instructions[i][1]=='jgt':
                Mem[ins_count]=['11101']
            if Instructions[i][1]=='je':
                Mem[ins_count]=['11111']
            Mem[ins_count].append('0000')
            if nn in Mem:
                Mem[ins_count].append(tobinary(Mem.index(nn),7))
            ins_count=ins_count+1
        elif checktype(Instructions[i])=='F':
            Mem[ins_count]=['11010']
            Mem[ins_count].append('00000000000')
            ins_count=ins_count+1
if ins_count+len(variables)>128:
    aa="Input has more than 128 instructions, Hence not executable!"
    Errors.append(aa)



#Error for variables and labels
for i in range(len(Instructions)):
    if checktype(Instructions[i])=='D':
        if Instructions[i][3] not in variables:
            pp=Instructions[i][3]+':'
            if pp in labels:
                aa="Line no:"+str(Instructions[i][0])+" - Label used in place of variable.-",Instructions[i][3]
                Errors.append(aa)
            else:
                aa="Line no:"+str(Instructions[i][0])+" - Variable not defined.-",Instructions[i][3]
                Errors.append(aa)
    if checktype(Instructions[i])=='E':
        pp=Instructions[i][2]+':'
        if pp not in labels:
            if Instructions[i][2] in variables:
                aa="Line no:"+str(Instructions[i][0])+" - Variable used in place of label.-",Instructions[i][2]
                Errors.append(aa)
            else:
                aa="Line no:"+str(Instructions[i][0])+" - Label not defined.-",Instructions[i][2]
                Errors.append(aa)'''


def takeout(n,m,o):
    if o-m == 1:
        return n[m]
    else:
        xx=n[m]
        for i in range(m+1,o):
            xx=xx+n[i]
        return xx
def typ(n):
    lst=['00000','00001','00110','01010','01011','01100']
    xx=takeout(n,0,5)
    if xx in lst:
        return 'A'
    lst=['00010','01000','01001']
    if xx in lst:
        return 'B'
    lst=['00011','00111','01101','01110']
    if xx in lst:
        return 'C'
    lst=['00100','00101']
    if xx in lst:
        return 'D'
    lst=['01111','11100','11101','11111']
    if xx in lst:
        return 'E'
    lst=['11010']
    if xx in lst:
        return 'F'
handle=open("D:\Padhai Likhai\My codes\Python\sim.txt")
i=0
for line in handle:
    line=str(line)
    Mem[i]=[]
    if typ(line)=='A':
        Mem[i].append(takeout(line,0,5))
        Mem[i].append('00')
        Mem[i].append(takeout(line,7,10))
        Mem[i].append(takeout(line,10,13))
        Mem[i].append(takeout(line,13,16))
    if typ(line)=='B':
        Mem[i].append(takeout(line,0,5))
        Mem[i].append('0')
        Mem[i].append(takeout(line,6,9))
        Mem[i].append(takeout(line,9,16))
    if typ(line)=='C':
        Mem[i].append(takeout(line,0,5))
        Mem[i].append('00000')
        Mem[i].append(takeout(line,10,13))
        Mem[i].append(takeout(line,13,16))
    if typ(line)=='D':
        Mem[i].append(takeout(line,0,5))
        Mem[i].append('0')
        Mem[i].append(takeout(line,6,9))
        Mem[i].append(takeout(line,9,16))
    if typ(line)=='E':
        Mem[i].append(takeout(line,0,5))
        Mem[i].append('0000')
        Mem[i].append(takeout(line,9,16))
    if typ(line)=='F':
        Mem[i].append(takeout(line,0,5))
        Mem[i].append('00000000000')
    i=i+1

        
        


#Working on Functions.
def repstr(a,n,tbr):
    va=a[0]
    for i in range(1,n):
        va=va+a[i]
    va=va+tbr
    for i in range(n+1,len(a)):
        va=va+a[i]
    return va

def add_(a,b,c):
    a=todecimal(a,3)
    b=todecimal(b,3)
    c=todecimal(c,3)
    b_val=todecimal(Registers[b],16)
    c_val=todecimal(Registers[c],16)
    v=b_val+c_val
    if todecimal(Registers[7],16)!=0:
        Registers[7]='0000000000000000'
    if v<0 or v>127:
        Registers[a]='0000000000000000'
        Registers[7]=repstr(Registers[7],12,'1')
        print("During execution of instruction in Mem[",program_counter,"] the value goes out of range.")
        quit()
    v=tobinary(v,16)
    Registers[a]=v

def addf_(a,b,c):
    a=todecimal(a,3)
    b=todecimal(b,3)
    c=todecimal(c,3)
    b_val=todecimalf(Registers[b],16)
    c_val=todecimalf(Registers[c],16)
    v=b_val+c_val
    if todecimal(Registers[7],16)!=0:
        Registers[7]='0000000000000000'
    if v<0 or v>127:
        Registers[a]='0000000000000000'
        Registers[7]=repstr(Registers[7],12,'1')
        print("During execution of instruction in Mem[",program_counter,"] the value goes out of range.")
        quit()
    v=tobinary_f(v,16)
    Registers[a]=v

def sub_(a,b,c):
    a=todecimal(a,3)
    b=todecimal(b,3)
    c=todecimal(c,3)
    b_val=todecimal(Registers[b],16)
    c_val=todecimal(Registers[c],16)
    v=b_val-c_val
    if todecimal(Registers[7],16)!=0:
        Registers[7]='0000000000000000'
    if v<0 or v>127:
        Registers[a]='0'*16
        Registers[7]=repstr(Registers[7],12,'1')
        print("During execution of instruction in Mem[",program_counter,"] the value goes out of range.")
        quit()
    v=tobinary(v,16)
    Registers[a]=v

def subf_(a,b,c):
    a=todecimal(a,3)
    b=todecimal(b,3)
    c=todecimal(c,3)
    b_val=todecimalf(Registers[b],16)
    c_val=todecimalf(Registers[c],16)
    v=b_val-c_val
    if todecimal(Registers[7],16)!=0:
        Registers[7]='0000000000000000'
    if v<0 or v>127:
        Registers[a]='0000000000000000'
        Registers[7]=repstr(Registers[7],12,'1')
        print("During execution of instruction in Mem[",program_counter,"] the value goes out of range.")
        quit()
    v=tobinary_f(v,16)
    Registers[a]=v

def mul_(a,b,c):
    a=todecimal(a,3)
    b=todecimal(b,3)
    c=todecimal(c,3)
    b_val=todecimal(Registers[b],16)
    c_val=todecimal(Registers[c],16)
    v=b_val*c_val
    if todecimal(Registers[7],16)!=0:
        Registers[7]='0000000000000000'
    if v<0 or v>127:
        Registers[a]='0000000000000000'
        Registers[7]=repstr(Registers[7],12,'1')
        print("During execution of instruction in Mem[",program_counter,"] the value goes out of range.")
        quit()
    v=tobinary(v,16)
    Registers[a]=v

def xor_2b(a,b):
    if a=='0' and b=='0':
        return '0'
    if a=='1' and b=='1':
        return '0'
    if a=='1' and b=='0':
        return '1'
    if a=='0' and b=='1':
        return '1'
def xor_(a,b,c):
    a=todecimal(a,3)
    b=todecimal(b,3)
    c=todecimal(c,3)
    b_v=Registers[b]
    c_v=Registers[c]
    va=xor_2b(b_v[0],c_v[0])
    for i in range(1,16):
        va=va+xor_2b(b_v[i],c_v[i])
    Registers[a]=va
    if todecimal(Registers[7],16)!=0:
        Registers[7]='0000000000000000'

def or_2b(a,b):
    if a=='0' and b=='0':
        return '0'
    if a=='1' and b=='1':
        return '1'
    if a=='1' and b=='0':
        return '1'
    if a=='0' and b=='1':
        return '1'
def or_(a,b,c):
    a=todecimal(a,3)
    b=todecimal(b,3)
    c=todecimal(c,3)
    b_v=Registers[b]
    c_v=Registers[c]
    va=or_2b(b_v[0],c_v[0])
    for i in range(1,16):
        va=va+or_2b(b_v[i],c_v[i])
    Registers[a]=va
    if todecimal(Registers[7],16)!=0:
        Registers[7]='0000000000000000'

def and_2b(a,b):
    if a=='0' and b=='0':
        return '0'
    if a=='1' and b=='1':
        return '1'
    if a=='1' and b=='0':
        return '0'
    if a=='0' and b=='1':
        return '0'
def and_(a,b,c):
    a=todecimal(a,3)
    b=todecimal(b,3)
    c=todecimal(c,3)
    b_v=Registers[b]
    c_v=Registers[c]
    va=and_2b(b_v[0],c_v[0])
    for i in range(1,16):
        va=va+and_2b(b_v[i],c_v[i])
    Registers[a]=va
    if todecimal(Registers[7],16)!=0:
        Registers[7]='0000000000000000'

def mov_B(a,b):
    a=todecimal(a,3)
    va='0'*9+b
    Registers[a]=va
    if todecimal(Registers[7],16)!=0:
        Registers[7]='0000000000000000'

def movf_(a,b):
    a=todecimal(a,3)
    va='0'*8+b
    Registers[a]=va
    if todecimal(Registers[7],16)!=0:
        Registers[7]='0000000000000000'

def rs_(a,b):
    a=todecimal(a,3)
    a_v=Registers[a]
    b=todecimal(b,7)
    va='0'*b
    for i in range(0,16-b):
        va=va+a_v[i]
    Registers[a]=va
    if todecimal(Registers[7],16)!=0:
        Registers[7]='0000000000000000'

def ls_(a,b):
    a=todecimal(a,3)
    a_v=Registers[a]
    b=todecimal(b,7)
    va=a_v[b]
    for i in range(b+1,16):
        va=va+a_v[i]
    va='0'*b
    Registers[a]=va
    if todecimal(Registers[7],16)!=0:
        Registers[7]='0000000000000000'

def mov_C(a,b):
    a=todecimal(a,3)
    b=todecimal(b,3)
    Registers[a]=Registers[b]
    if todecimal(Registers[7],16)!=0:
        Registers[7]='0000000000000000'

def div_(a,b):
    a=todecimal(a,3)
    b=todecimal(b,3)
    a_v=todecimal(Registers[a],16)
    b_v=todecimal(Registers[b],16)
    if todecimal(Registers[7],16)!=0:
        Registers[7]='0000000000000000'
    if b_v==0:
        Registers[7]=repstr(Registers[7],12,'1')
        Registers[0]='0000000000000000'
        Registers[1]='0000000000000000'
    else:
        Registers[0]=tobinary(a_v//b_v,16)
        Registers[1]=tobinary(a_v%b_v,16)

def not_b(a):
    if a=='0':
        return '1'
    if a=='1':
        return '0'
def not_(a,b):
    a=todecimal(a,3)
    b=todecimal(b,3)
    b_v=Registers[b]
    va=not_b(b_v[0])
    for i in range(1,16):
        va=va+not_b(b_v[i])
    Registers[a]=va
    if todecimal(Registers[7],16)!=0:
        Registers[7]='0000000000000000'

def cmp_(a,b):
    a=todecimal(a,3)
    b=todecimal(b,3)
    a_v=Registers[a]
    b_v=Registers[b]
    if todecimal(a_v,16)==todecimal(b_v,16):
        Registers[7]=repstr(Registers[7],15,'1')
        Registers[7]=repstr(Registers[7],13,'0')
        Registers[7]=repstr(Registers[7],14,'0')
    elif todecimal(a_v,16)<todecimal(b_v,16):
        Registers[7]=repstr(Registers[7],13,'1')
        Registers[7]=repstr(Registers[7],15,'0')
        Registers[7]=repstr(Registers[7],14,'0')
    elif todecimal(a_v,16)>todecimal(b_v,16):
        Registers[7]=repstr(Registers[7],14,'1')
        Registers[7]=repstr(Registers[7],15,'0')
        Registers[7]=repstr(Registers[7],13,'0')

def st_(a,b):
    a=todecimal(a,3)
    Mem[todecimal(b,7)]=Registers[a]
    if todecimal(Registers[7],16)!=0:
        Registers[7]='0000000000000000'
    if todecimal(Registers[7],16)!=0:
        Registers[7]='0000000000000000'
    return 1
    

def ld_(a,b):
    a=todecimal(a,3)
    b_v=Mem[todecimal(b,7)]
    if b_v==0:
        Registers[a]=tobinary(Mem[todecimal(b,7)],16)
    else:
        Registers[a]=Mem[todecimal(b,7)]
    if todecimal(Registers[7],16)!=0:
        Registers[7]='0000000000000000'
    return 1
    

def jmp_(a):
    try:
        Registers[7]='0000000000000000'
        return todecimal(a,7)
    except:
        return -1

def jlt_(a):
    try:
        if Registers[7][13]=='1':
            Registers[7]='0000000000000000'
            return todecimal(a,7)
        else:
            if todecimal(Registers[7],16)!=0:
                Registers[7]='0000000000000000'
            return -1
    except:
        return -1

def jgt_(a):
    try:
        if Registers[7][14]=='1':
            Registers[7]='0000000000000000'
            return todecimal(a,7)
        else:
            if todecimal(Registers[7],16)!=0:
                Registers[7]='0000000000000000'
            return -1
    except:
        return -1

def je_(a):
    try:
        if Registers[7][15]=='1':
            Registers[7]='0000000000000000'
            return todecimal(a,7)
        else:
            if todecimal(Registers[7],16)!=0:
                Registers[7]='0000000000000000'
            return -1
    except:
        return -1

#print("variables",variables)
#print("Mem",Mem)

#Execution
def exct(inss,pc):
    if inss[0]=='00000':
        add_(inss[2],inss[3],inss[4])
        return pc+1
    elif inss[0]=='10000':
        addf_(inss[2],inss[3],inss[4])
        return pc+1
    elif inss[0]=='10001':
        subf_(inss[2],inss[3],inss[4])
        return pc+1
    elif inss[0]=='00001':
        sub_(inss[2],inss[3],inss[4])
        return pc+1
    elif inss[0]=='00010':
        mov_B(inss[2],inss[3])
        return pc+1
    elif inss[0]=='10010':
        movf_(inss[1],inss[2])
        return pc+1
    elif inss[0]=='00011':
        mov_C(inss[2],inss[3])
        return pc+1
    elif inss[0]=='00100':
        if ld_(inss[2],inss[3])==1:
            return pc+1
    elif inss[0]=='00101':
        if st_(inss[2],inss[3])==1:
            return pc+1
    elif inss[0]=='00110':
        mul_(inss[2],inss[3],inss[4])
        return pc+1
    elif inss[0]=='00111':
        div_(inss[2],inss[3])
        return pc+1
    elif inss[0]=='01000':
        rs_(inss[2],inss[3])
        return pc+1
    elif inss[0]=='01001':
        ls_(inss[2],inss[3])
        return pc+1
    elif inss[0]=='01010':
        xor_(inss[2],inss[3],inss[4])
        return pc+1
    elif inss[0]=='01011':
        or_(inss[2],inss[3],inss[4])
        return pc+1
    elif inss[0]=='01100':
        and_(inss[2],inss[3],inss[4])
        return pc+1
    elif inss[0]=='01101':
        not_(inss[2],inss[3])
        return pc+1
    elif inss[0]=='01110':
        cmp_(inss[2],inss[3])
        return pc+1
    elif inss[0]=='01111':
        v=jmp_(inss[2])
        if v!=-1:
            return v
        else:
            return pc+1
    elif inss[0]=='11100':
        v=jlt_(inss[2])
        if v!=-1:
            return v
        else:
            return pc+1
    elif inss[0]=='11101':
        v=jgt_(inss[2])
        if v!=-1:
            return v
        else:
            return pc+1
    elif inss[0]=='11111':
        v=je_(inss[2])
        if v!=-1:
            return v
        else:
            return pc+1
if len(Errors)==0:
    #print("Initially:")
    #print("RF-",Registers)
    #print("PC-",program_counter)
    #print("")
    #print("SIMULATOR:")
    while Mem[program_counter][0]!='11010':
        if islabel(Mem[program_counter])==True:
            program_counter=program_counter+1
        print(tobinary(program_counter,7),end="        ")
        if islabel(Mem[program_counter])==False:
            program_counter=exct(Mem[program_counter],program_counter)
        '''print("RF-",Registers)
        print("PC-",program_counter)
        print("")'''
        for km in range(0,7):
            print(Registers[km],end=" ")
        print(Registers[7])

    print(tobinary(program_counter,7),end="        ")
    for km in range(0,8):
        print(Registers[km],end=" ")
    print("")
    for k in range(len(Mem)):
        if Mem[k]==0:
            MM[k]=Mem[k]
        elif islabel(Mem[k]):
            MM[k]=Mem[k]
        elif type(Mem[k])==str:
            MM[k]=Mem[k]
        else:
            nn=Mem[k][0]
            for l in range(1,len(Mem[k])):
                nn=nn+Mem[k][l]
            MM[k]=nn
    for km in range(len(MM)):
        if MM[km]==0:
            print(tobinary(MM[km],16))
        else:
            print(MM[km])
else:
    for i in range(len(Errors)):
        print("Error! ",Errors[i])
#print(MM)