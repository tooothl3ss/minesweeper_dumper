from ctypes import *
from ctypes.wintypes import *
from pprint import pprint
from pprint import pprint


def readMemory(process,process_addres, strlen=16, vAddres=0, memoryStep=0x10):
    tmp = []
    buf = create_string_buffer(strlen)
    s = c_size_t()
    for i in range(0,vAddres+1):
        k32.ReadProcessMemory(process, process_addres, buf, strlen, byref(s))
        tmp.append(buf.raw)
        process_addres += memoryStep
    return tmp

def writeMemory(process, process_addres, buff):
    buf = create_string_buffer(1)
    #print('[!] Debug: buff is {} type, buf is {} type '.format(type(buff),type(buf)))
    #print(buf[0])
    buf[0] = buff
    #print("[!] Degug: {}".format(readMemory(process=process, process_addres=process_addres, strlen=1, vAddres=1)))
    k32.WriteProcessMemory(process, process_addres,buf,1,None)
    
def createMap(dump):
    wall = 0x10
    mine = 0x8f
    map = ''
    #print(dump)
    for x in dump:
        #print(x)
        stmp = ''
        for ch in range(0,len(x)):
            if int.from_bytes(x[ch][0], "big") == wall:
                stmp += '#'
            elif int.from_bytes(x[ch][0], "big") == mine:
                stmp += '!'
            else:
                stmp += '*'
        map +=stmp + '\n'
    return map

def markMines(process, tmap, mark=b'\x0E'): # \x0E - flag
    mine = 0x8f
    for x in tmap:
        #print(x)
        stmp = ''
        for ch in range(0,len(x)):
            if int.from_bytes(x[ch][0], "big") == mine:
                writeMemory(process=process,process_addres=x[ch][1],buff=mark)

def dumpMap(process, baseaddres, lenstr, hight):
    resmap=[]
    tmpaddres = baseaddres
    for i in range(0,hight):
        tmp1 = []
        for x in range(0,lenstr):
           tmp1.append([readMemory(process,process_addres=tmpaddres,vAddres=0,strlen=1,memoryStep=0x00)[0],tmpaddres])
           tmpaddres+=0x01
        baseaddres+=0x20
        resmap.append(tmp1)
        tmpaddres = baseaddres
    return resmap

if __name__=='__main__':

    PROCESS_ID = 2056 # From T askManager for Notepad.exe
    PROCESS_HEADER_ADDR = 0x01005340 # From SysInternals VMMap utility
    PROCESS_VM_READ = 0x0010
    PROCESS_VM_WRITE = 0x0020 | 0x0008
    k32 = WinDLL('kernel32')
    k32.OpenProcess.argtypes = DWORD,BOOL,DWORD
    k32.OpenProcess.restype = HANDLE
    k32.ReadProcessMemory.argtypes = HANDLE,LPVOID,LPVOID,c_size_t,POINTER(c_size_t)
    k32.ReadProcessMemory.restype = BOOL
    k32.WriteProcessMemory.argtypes = HANDLE,LPVOID,LPVOID,c_size_t,POINTER(c_size_t)
    k32.WriteProcessMemory.restype = BOOL
    processRead = k32.OpenProcess(PROCESS_VM_READ, 0, PROCESS_ID)
    processWrite = k32.OpenProcess(PROCESS_VM_WRITE, 0, PROCESS_ID)

    #writeMemory(process=processWrite,process_addres=0x01005382, buff=b'\x8C')
    lenmines = int.from_bytes(readMemory(process=processRead,process_addres=0x01005194,vAddres=1,strlen=1)[0], "big")
    print("[*] Count of mines: {}".format(lenmines))
    baseaddres = PROCESS_HEADER_ADDR
    if lenmines == 99:
        tmp1 = dumpMap(process=processRead,lenstr=32,baseaddres=PROCESS_HEADER_ADDR,hight=18)
    elif lenmines == 10:
        tmp1 = dumpMap(process=processRead,lenstr=11,baseaddres=PROCESS_HEADER_ADDR,hight=11)
    elif lenmines == 40:
        tmp1 = dumpMap(process=processRead,lenstr=18,baseaddres=PROCESS_HEADER_ADDR,hight=18)
    print(createMap(tmp1))
    markMines(process=processWrite, tmap=tmp1)
