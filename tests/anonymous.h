#if 0
/*
 * TODO: there's no easy way to implement this with libclang 3.6; trunk adds a
 * feature that will make it possible.
 */
struct tagged1 {
	enum type1 {
		STRING1,
		INT1,
	} t;
	union var1 {
		char *s;
		int i;
	};
};
#endif

struct body {
	struct {
		int x, y;
	} point;
	struct {
		int mass;
		int volume;
	} size;
	union {
		int liquid;
		int gas;
	} state;
};

struct nested {
	struct {
		struct {
			int a;
		} A;
		int b;
	} B;
	int c;
};
