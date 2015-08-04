typedef int (*compar_t)(const void *, const void *);

extern compar_t default_cmp;

void my_qsort(void *base, unsigned long nmemb, unsigned long size, compar_t compar);

struct vtable {
	compar_t cmp;
	void *(*add)(const void *, const void *);
};

typedef void (*meta_t)(void (*)(void));

void (*signal(int signum, void (*handler)(int)))(int);

typedef int (*noproto_t)();

typedef (*defaultrettype_t)(char *);

typedef (*blasphemy_t)();

#if 0
/*
 * TODO: not sure why the compar_t parameter comes up as a function pointer and
 * not a typedef.
 */
typedef void (*wrapper_t)(compar_t);
#endif
