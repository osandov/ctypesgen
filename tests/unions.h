union simple {
	int x;
	float y;
};

union empty {
};

union nested {
	union simple s;
	long long z;
};

union forward_declaration;

union simple binary(union simple a, union simple b);

void binary2(union simple *a, const union simple *b);

union bitty {
	int a : 1;
	int b : 2;
	int c : 4;
	int d : 8;
	int e : 16;
};

struct tagged_union {
	int type;
	union simple u;
};
