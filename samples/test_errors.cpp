// Test file with various preprocessor directive patterns and errors
#ifndef TEST_FILE_H
#define TEST_FILE_H

// Simple defines
#define SIMPLE_CONSTANT 42
#define STRING_CONSTANT "Hello World"

// Redefinition (should trigger warning)
#define SIMPLE_CONSTANT 43

// Invalid identifier names (should trigger errors)
#define 123_INVALID "invalid"
#define _RESERVED_NAME "reserved"

// Basic conditional compilation
#ifdef FEATURE_A
    #define FEATURE_A_ENABLED 1
    #ifdef FEATURE_A_ADVANCED
        #define ADVANCED_FEATURES 1
    #endif
#else
    #define FEATURE_A_ENABLED 0
#endif

// Unbalanced directives (errors)
#ifdef UNBALANCED_START
    #define INSIDE_UNBALANCED

// Missing #endif above

#ifdef ANOTHER_UNBALANCED
    #define MORE_DEFINES
#endif
// This endif doesn't match

#endif // This endif has no matching opening

// Orphaned else/elif
#else
    #define ORPHANED_ELSE

#elif defined(ORPHANED_ELIF)
    #define ORPHANED_ELIF_DEFINE

// Complex nesting
#ifdef LEVEL_1
    #define LEVEL_1_DEFINE
    #ifdef LEVEL_2
        #define LEVEL_2_DEFINE
        #ifdef LEVEL_3
            #define LEVEL_3_DEFINE
            #ifdef LEVEL_4
                #define LEVEL_4_DEFINE
            #endif
        #endif
    #endif
#endif

// Contradictory conditions (unreachable code)
#ifdef DEBUG
    #ifndef DEBUG
        #define UNREACHABLE_CODE 1  // This should never be reached
    #endif
#endif

// Complex conditional expressions
#if defined(WINDOWS) && defined(DEBUG) && !defined(RELEASE)
    #define COMPLEX_CONDITION_1
#elif defined(LINUX) || defined(UNIX)
    #define COMPLEX_CONDITION_2
#elif defined(MACOS)
    #define COMPLEX_CONDITION_3
#else
    #define DEFAULT_CONDITION
#endif

// Malformed conditions
#if MISSING_PARENTHESIS && (CONDITION
    #define SYNTAX_ERROR_1
#endif

#if ASSIGNMENT = 1  // Should be ==
    #define SYNTAX_ERROR_2
#endif

// Empty conditions
#if
    #define EMPTY_CONDITION
#endif

#ifdef
    #define EMPTY_IFDEF
#endif

// Function-like macros
#define FUNCTION_MACRO(x, y) ((x) + (y))
#define UNSAFE_MACRO(x) x * 2  // Should be ((x) * 2)

// Multi-line defines (complex parsing)
#define MULTI_LINE_MACRO(x) \
    do { \
        printf("Value: %d\n", x); \
        fflush(stdout); \
    } while(0)

// Include directives
#include <stdio.h>
#include "missing_file.h"  // File doesn't exist
#include   // Missing filename

// Undef directives
#undef SIMPLE_CONSTANT
#undef UNDEFINED_SYMBOL  // Warning: symbol was never defined

// Missing symbol names
#define
#ifdef
#ifndef
#undef

// Circular dependencies (if we had a dependency tracker)
#ifdef CIRCULAR_A
    #define DEPENDS_ON_B CIRCULAR_B
#endif

#ifdef CIRCULAR_B  
    #define DEPENDS_ON_A CIRCULAR_A
#endif

// Very deep nesting (stress test)
#ifdef DEEP_1
#ifdef DEEP_2
#ifdef DEEP_3
#ifdef DEEP_4
#ifdef DEEP_5
#ifdef DEEP_6
#ifdef DEEP_7
#ifdef DEEP_8
#ifdef DEEP_9
#ifdef DEEP_10
    #define DEEPLY_NESTED_DEFINE
#endif
#endif
#endif
#endif
#endif
#endif
#endif
#endif
#endif
#endif

// Mixed valid and invalid content
#ifdef MIXED_CONTENT
    #define VALID_IN_MIXED
    #if SYNTAX ERROR HERE
        #define INVALID_IN_MIXED
    #endif
    #define ANOTHER_VALID
#endif

// Comments in directives (should be handled correctly)
#ifdef DEBUG_MODE  // This is a comment
    #define DEBUG_LEVEL 3  /* Another comment style */
#endif /* End of block comment */

// #endif // TEST_FILE_H
// Missing the actual #endif for the include guard