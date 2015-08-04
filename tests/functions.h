int strcmp(const char *s1, const char *s2);

void gcd(int *x, int *y);

char *my_strchr(const char *s, char c);

char *byte_to_hex(unsigned char b);

char *sbyte_to_hex(signed char s);

int pipe2(int pipefd[2], int flags);

double sin(double x);

float cosf(float x);

long int strtol(const char *nptr, char **endptr, int base);

long long int strtoll(const char *nptr, char **endptr, int base);

unsigned long int strtoul(const char *nptr, char **endptr, int base);

unsigned long long int strtoull(const char *nptr, char **endptr, int base);

int my_memcmp(const void *s1, const void *s2, unsigned int n);

int short_add_with_overflow(short a, short b, short *c);

int unsigned_short_add_with_overflow(unsigned short a, unsigned short b, unsigned short *c);

int getid(void);

int printf(const char *format, ...);

int execve(const char *path, char *const argv[], char *const envp[]);

int noproto();

defaultrettype(char *s);

blasphemy();

static inline int invisible(void);
