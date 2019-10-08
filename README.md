# Fly libc Checker

Fly libc Checker is a lightweight tool that allows you to check that your libc
contains all standard complaint functions. N.B. **contains**, it does not check
the correctness of them (at least at this moment).

## General Idea
The idea is to take all functions from the standard and try to compile it
statically without optimization. If a linker is able to find all required
symbols -- congrats, library is complaint. To achieve it, we generate .c file
with all functions that successfully compiles.

## History
This tool was written when the author wanted to ensure that mingw-w64 has all
c99 functions mapped on msvcrt.

## How to Use
To check libc on c99 standard, just compile `checkers\c99_main.c` e.g.:

```bash
gcc c99_main.c -O0 -lm
```

If you need to test on another set of functions, you can use the format
similar to `standards\c99.std` and the python script `fly_gen.py`. The script
allows you to generate the similar .c file to test the library.