enum color {
	RED,
	GREEN,
	BLUE,
};

enum more_color {
	YELLOW = 3,
	CYAN,
	MAGENTA,
	BLACK = 10,
};

int rank_color(enum color color);

enum color best_color(void);

enum {
	READ,
	WRITE,
	APPEND,
};
