/* SysPane experimental embedding sketch, 0.1. NOT a stable ABI or implementation.
 * Ownership: create/free use the same module. Input UTF-8 slices are borrowed only
 * for the duration of a call. No exceptions may cross this C boundary.
 * Old toolchains require a separately qualified width/ABI adaptation.
 */
#ifndef SYSPANE_EXPERIMENTAL_API_H
#define SYSPANE_EXPERIMENTAL_API_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#define SYSPANE_API_EXPERIMENTAL_VERSION 1u
typedef struct syspane_context syspane_context;
typedef struct { const char *data; size_t size; } syspane_utf8_view;
typedef enum { SYSPANE_OK=0, SYSPANE_INVALID=1, SYSPANE_DENIED=2,
 SYSPANE_CONFLICT=3, SYSPANE_UNAVAILABLE=4, SYSPANE_FAILED=5 } syspane_result;
typedef struct { uint32_t struct_size; uint32_t api_version;
 size_t max_record_bytes; } syspane_options;
syspane_result syspane_create(const syspane_options *options, syspane_context **out);
void syspane_destroy(syspane_context *context);
/* Reentrant/threading/async cancellation contracts must be qualified before v1.
 * JSON response is caller-owned; required_size is set on insufficient capacity. */
syspane_result syspane_request(syspane_context *context, syspane_utf8_view request,
 char *response, size_t capacity, size_t *required_size);
#ifdef __cplusplus
}
#endif
#endif
