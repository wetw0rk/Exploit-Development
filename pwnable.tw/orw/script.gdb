target remote challenge:9001
add-symbol-file types.o 0
b *_start
c
b *orw_seccomp
c
$$b *main+66
$$c
