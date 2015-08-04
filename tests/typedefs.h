typedef int gint;

int gint_to_int(gint i);

gint int_to_gint(int i);

enum color {
	RED,
	GREEN,
	BLUE,
};

typedef enum color color_t;

int rank_color(color_t color);

color_t best_color(void);

struct point {
	int x;
	int y;
};

typedef struct point point_t;

point_t add_points(point_t a, point_t b);

void add_points2(point_t *a, const point_t *b);

typedef struct {
	int x, y;
} point2_t;

typedef enum {
	YELLOW,
	CYAN,
	MAGENTA,
} color2_t;

typedef union {
	char *s;
	int i;
	double d;
} type_t;

typedef struct point *point_pointer_t;

void process(point_pointer_t p);
