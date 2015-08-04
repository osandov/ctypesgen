struct point {
	int x;
	int y;
};

struct empty {
};

struct nested {
	struct point p;
	int z;
};

struct forward_declaration;

struct point add_points(struct point a, struct point b);

void add_points2(struct point *a, const struct point *b);

struct bitty {
	int a : 1;
	int b : 2;
	int c : 4;
	int d : 8;
	int e : 16;
};

struct list {
	struct list *next;
};
