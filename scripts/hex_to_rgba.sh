#!/usr/bin/env bash
#set -x

hextoi() {
	value=${1}
	result=$(echo "ibase=16; ${value}" | bc)
	echo "${result}"
}


darker() {
	hexinput=$(echo $1 | tr '[:lower:]' '[:upper:]')
	alpha=${2-1.0}

    a=`echo $hexinput | cut -c-2`
    b=`echo $hexinput | cut -c3-4`
    c=`echo $hexinput | cut -c5-6`

	r=$(hextoi ${a})
	g=$(hextoi ${b})
	b=$(hextoi ${c})

	printf 'rgba(%i, %i, %i, %0.2f)\n' ${r} ${g} ${b} ${alpha}
}

darker $@
