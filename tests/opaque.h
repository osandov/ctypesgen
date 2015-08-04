struct handle;

typedef struct handle handle_t;

struct handle {
	char *name;
};

struct opaque;

typedef struct opaque *opaque_t;

opaque_t opaque_new(void);

void opaque_free(opaque_t opaque);
