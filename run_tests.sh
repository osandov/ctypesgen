#!/bin/sh

if [ $# -eq 0 ]; then
	TESTS=tests/*.h
else
	TESTS=$@
fi

for file in $TESTS; do
	echo "$file"
	if ./ctypesgen.py --ignore-included libtest.so "$file" | diff "${file}.out" -; then
		echo -e "\033[32mPASSED\033[0m"
	else
		echo -e "\033[31mFAILED\033[0m"
	fi
	if ! pep8 --ignore=E501 "${file}.out"; then
		echo -e "\033[31mPEP8 FAILED\033[0m"
	fi
done
