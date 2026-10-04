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
 SYSPANE_CONFLICT=3, SYSPANE_UNAVAILABLE=4, SYSPANE_FAILED=5,
 SYSPANE_BUFFER_TOO_SMALL=6, SYSPANE_RESULT_EXPIRED=7,
 SYSPANE_BUSY=8 } syspane_result;
typedef struct { uint32_t struct_size; uint32_t api_version;
 size_t max_record_bytes; } syspane_options;
syspane_result syspane_create(const syspane_options *options, syspane_context **out);
void syspane_destroy(syspane_context *context);
/* Experimental synchronous sketch: one caller at a time per context; no reentry.
 * Input slices are borrowed for this call. Output is caller-owned UTF-8 bytes,
 * not NUL-terminated; required_size excludes any terminator and is always set.
 * The request may commit before BUFFER_TOO_SMALL is returned. Its terminal result
 * is retained under request_id until release_result or context destruction.
 * A null output with capacity zero is allowed, but is NOT a mutation-free preview.
 * Insufficient capacity writes no partial response. Retrieve via read_result;
 * never submit a fresh mutation simply to obtain a larger response buffer.
 * Admission returns BUSY before mutation if result retention cannot be reserved.
 * Destroying a context does not undo committed changes. Reconcile durable request
 * records after process loss; RESULT_EXPIRED is not permission for blind replay.
 * Export/calling-convention and asynchronous cancellation remain target admission
 * decisions; this header does not establish a stable binary interface. */
syspane_result syspane_request(syspane_context *context, syspane_utf8_view request,
 char *response, size_t capacity, size_t *required_size);
/* Read-only result retrieval never executes the original operation. */
syspane_result syspane_read_result(syspane_context *context, syspane_utf8_view request_id,
 char *response, size_t capacity, size_t *required_size);
/* Ends the retrieval guarantee, not the transaction or its durable audit record. */
syspane_result syspane_release_result(syspane_context *context, syspane_utf8_view request_id);
#ifdef __cplusplus
}
#endif
#endif
