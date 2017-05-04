#!/bin/bash
out=""
for octet in ${1:0:2} ${1:2:2} ${1:4:2}; do
    out+=$(printf %x $(printf "(%d * $2 + 0.5) / 1\n" 0x$octet | bc))
done; echo $out
