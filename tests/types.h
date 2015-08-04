#include <complex.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <uchar.h>
#include <sys/types.h>

void int_types(signed char b, short s, int i, long l, long long ll);

void intx_types(int8_t b, int16_t s, int32_t l, int64_t ll);

void uint_types(unsigned char b, unsigned short s, unsigned int i, unsigned long l, unsigned long long ll);

void uintx_types(uint8_t b, uint16_t s, uint32_t l, uint64_t ll);

void float_types(float f, double d, long double ld);

void char_types(char c, char *s, char16_t c16, char16_t *s16, char32_t c32, char32_t *s32);

void wchar_types(wchar_t wc, wchar_t *wcs);

void bool_types(_Bool b, bool b2);

void complex_types(float _Complex fc, double _Complex dc, long double _Complex ldc);

void complex_types2(float complex fc, double complex dc, long double complex ldc);

void big_int_types(__int128 i, unsigned __int128 u);

void big_int_typedefs(__int128_t i,  __uint128_t u);

void size_types(size_t s, ssize_t ss); 
