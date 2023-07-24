from ctypes import c_size_t, create_string_buffer, byref, WinDLL, POINTER
from ctypes.wintypes import HANDLE, DWORD, BOOL, LPVOID


WALL = 0x10
MINE = 0x8f
FLAG = b'\x0E'


def read_memory(process, process_address, strlen=16, v_address=0, memory_step=0x10):
    temp = []
    buf = create_string_buffer(strlen)
    s = c_size_t()

    for _ in range(0, v_address + 1):
        k32.ReadProcessMemory(process, process_address, buf, strlen, byref(s))
        temp.append(buf.raw)
        process_address += memory_step

    return temp


def write_memory(process, process_address, buff):
    buf = create_string_buffer(1)
    buf[0] = buff
    k32.WriteProcessMemory(process, process_address, buf, 1, None)


def create_map(dump):
    map_repr = ''

    for x in dump:
        temp_str = ''

        for ch in range(0, len(x)):
            if int.from_bytes(x[ch][0], "big") == WALL:
                temp_str += '#'
            elif int.from_bytes(x[ch][0], "big") == MINE:
                temp_str += '!'
            else:
                temp_str += '*'

        map_repr += temp_str + '\n'

    return map_repr


def mark_mines(process, tmap, mark=FLAG):  # \x0E - flag
    for x in tmap:
        for ch in range(0, len(x)):
            if int.from_bytes(x[ch][0], "big") == MINE:
                write_memory(process=process, process_address=x[ch][1], buff=mark)


def dump_map(process, base_address, len_str, height):
    res_map = []
    tmp_address = base_address

    for _ in range(0, height):
        tmp1 = []

        for _ in range(0, len_str):
            tmp1.append([read_memory(process, process_address=tmp_address, v_address=0, strlen=1, memory_step=0x00)[0], tmp_address])
            tmp_address += 0x01

        base_address += 0x20
        res_map.append(tmp1)
        tmp_address = base_address

    return res_map


if __name__ == '__main__':
    PROCESS_ID = 17952  # From Task Manager for minesam.exe
    PROCESS_HEADER_ADDR = 0x01005340  # From SysInternals VMMap utility
    PROCESS_VM_READ = 0x0010
    PROCESS_VM_WRITE = 0x0020 | 0x0008

    k32 = WinDLL('kernel32')
    k32.OpenProcess.argtypes = DWORD, BOOL, DWORD
    k32.OpenProcess.restype = HANDLE
    k32.ReadProcessMemory.argtypes = HANDLE, LPVOID, LPVOID, c_size_t, POINTER(c_size_t)
    k32.ReadProcessMemory.restype = BOOL
    k32.WriteProcessMemory.argtypes = HANDLE, LPVOID, LPVOID, c_size_t, POINTER(c_size_t)
    k32.WriteProcessMemory.restype = BOOL

    process_read = k32.OpenProcess(PROCESS_VM_READ, 0, PROCESS_ID)
    process_write = k32.OpenProcess(PROCESS_VM_WRITE, 0, PROCESS_ID)

    len_mines = int.from_bytes(read_memory(process=process_read, process_address=0x01005194, v_address=1, strlen=1)[0], "big")

    print(f"[*] Count of mines: {len_mines}")

    base_address = PROCESS_HEADER_ADDR

    if len_mines == 99:
        map_dump = dump_map(process=process_read, len_str=32, base_address=PROCESS_HEADER_ADDR, height=18)
    elif len_mines == 10:
        map_dump = dump_map(process=process_read, len_str=11, base_address=PROCESS_HEADER_ADDR, height=11)
    elif len_mines == 40:
        map_dump = dump_map(process=process_read, len_str=18, base_address=PROCESS_HEADER_ADDR, height=18)

    print("[*] Marking mines...")
    mark_mines(process=process_write, tmap=map_dump)  # default marks = autosolver / 0
    print("[*] Printing map...")
    print(create_map(map_dump))
