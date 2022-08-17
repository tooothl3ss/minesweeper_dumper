from ctypes import *
from ctypes.wintypes import *
from pprint import pprint
from pprint import pprint


def readMemory(process,process_addres, strlen=16, vAddres=10, memoryStep=0x10):
    tmp = []
    buf = create_string_buffer(strlen)
    s = c_size_t()
    for i in range(0,vAddres+1):
        k32.ReadProcessMemory(process, process_addres, buf, strlen, byref(s))
        tmp.append(buf.raw)
        process_addres += memoryStep
    return tmp


def createMap(dump):
    wall = 0x10
    mine = 0x8f
    map = ''
    for x in dump:
        stmp = ''
        for ch in range(0,len(x)):
            #print("[!] Debug: {}".format(ch))
            if int.from_bytes(x[ch], "big") == wall:
                stmp += '#'
            elif int.from_bytes(x[ch], "big") == mine:
                stmp += '!'
            else:
                stmp += '*'
        map +=stmp + '\n'
    return map


def dumpMap(process, baseaddres, lenstr,hight):
    resmap=[]
    tmpaddres = baseaddres
    for i in range(0,hight):
        tmp1 = []
        for x in range(0,lenstr):
           tmp1.append(readMemory(process,process_addres=tmpaddres,vAddres=0,strlen=1,memoryStep=0x00)[0])
           tmpaddres+=0x01
        baseaddres+=0x20
        tmpaddres = baseaddres
        resmap.append(tmp1)
    return resmap


if __name__=='__main__':

    PROCESS_ID = 15352 # From TaskManager for Notepad.exe
    PROCESS_HEADER_ADDR = 0x01005340 # From SysInternals VMMap utility
    PROCESS_VM_READ = 0x0010
    k32 = WinDLL('kernel32')
    k32.OpenProcess.argtypes = DWORD,BOOL,DWORD
    k32.OpenProcess.restype = HANDLE
    k32.ReadProcessMemory.argtypes = HANDLE,LPVOID,LPVOID,c_size_t,POINTER(c_size_t)
    k32.ReadProcessMemory.restype = BOOL
    process = k32.OpenProcess(PROCESS_VM_READ, 0, PROCESS_ID)

    lenmines = int.from_bytes(readMemory(process=process,process_addres=0x01005194,vAddres=1,strlen=1)[0], "big")
    print("[*] Count of mines: {}".format(lenmines))
    baseaddres = PROCESS_HEADER_ADDR
    if lenmines == 99:
        tmp1 = dumpMap(process=process,lenstr=32,baseaddres=PROCESS_HEADER_ADDR,hight=18)
    elif lenmines == 10:
        tmp1 = dumpMap(process=process,lenstr=11,baseaddres=PROCESS_HEADER_ADDR,hight=11)
    elif lenmines == 40:
        tmp1 = dumpMap(process=process,lenstr=18,baseaddres=PROCESS_HEADER_ADDR,hight=18)
    print(createMap(tmp1))