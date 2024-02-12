#!/bin/sh

if [ $# -eq 0 ]; then
	TESTS=tests/*.h
else
	TESTS=$@
fi

failed=0
for file in $TESTS; do
	echo "$file"
	if ./ctypesgen.py --clang-flags \"-Wno-error=implicit-int\" --ignore-included --library libtest.so --headers "$file" | diff "${file}.out" -; then
		echo -e "\033[32mPASSED\033[0m"
	else
		echo -e "\033[31mFAILED\033[0m"
		failed=1
	fi
	if ! autopep8 --ignore=E501,E305 "${file}.out"; then
		echo -e "\033[31mPEP8 FAILED\033[0m"
		failed=1
	fi
done

exit $failed
