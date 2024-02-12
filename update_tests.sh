if [ $# -eq 0 ]; then
	TESTS=tests/*.h
else
	TESTS=$@
fi

failed=0
for file in $TESTS; do
	echo "$file"
	./ctypesgen.py --clang-flags \"-Wno-error=implicit-int\" --ignore-included --library libtest.so --headers "$file" > $file.out
done

exit $failed