struct outer {
	struct inner {
		int x;
		int y;
	} p;
	int z;
};

struct tagged {
	enum type {
		STRING,
		INT,
	} t;
	union var {
		char *s;
		int i;
	} u;
};
