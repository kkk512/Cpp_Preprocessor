#include "config.h"
#include <iostream>

// Application-specific defines
#define APP_NAME "Sample Application"
#define MAX_BUFFER_SIZE 1024

// Conditional compilation examples
#ifdef DEBUG
    #define DBG_PRINT(x) std::cout << "[DEBUG] " << x << std::endl
#else
    #define DBG_PRINT(x)
#endif

#if LOG_LEVEL >= 2
    #define INFO_PRINT(x) std::cout << "[INFO] " << x << std::endl
#else
    #define INFO_PRINT(x)
#endif

#if LOG_LEVEL >= 3
    #define VERBOSE_PRINT(x) std::cout << "[VERBOSE] " << x << std::endl
#else
    #define VERBOSE_PRINT(x)
#endif

// Function-like macros
#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define MIN(a, b) ((a) < (b) ? (a) : (b))

// Platform-specific code
#ifdef WINDOWS
    #include <windows.h>
    #define SLEEP_MS(x) Sleep(x)
#elif defined(LINUX)
    #include <unistd.h>
    #define SLEEP_MS(x) usleep((x) * 1000)
#endif

// Nested conditional compilation
#ifdef ENABLE_NETWORKING
    #ifdef ENABLE_SSL
        #define SECURE_NETWORKING
        #ifdef SSL_VERSION_3
            #define SSL_PROTOCOL "TLS 1.3"
        #else
            #define SSL_PROTOCOL "TLS 1.2"
        #endif
    #else
        #define INSECURE_NETWORKING
    #endif
#endif

// Complex conditional logic
#if defined(WINDOWS) && defined(DEBUG)
    #define PLATFORM_DEBUG_FLAG 1
#elif defined(LINUX) && defined(DEBUG)
    #define PLATFORM_DEBUG_FLAG 2
#else
    #define PLATFORM_DEBUG_FLAG 0
#endif

// Error conditions (intentional for testing)
#ifdef MISSING_ENDIF
    #define BROKEN_BLOCK

// This will cause an unmatched directive error

#ifdef ANOTHER_CONDITION
    #define ANOTHER_DEFINE
// Missing endif for ANOTHER_CONDITION

int main() {
    DBG_PRINT("Application starting...");
    INFO_PRINT("Version: " << VERSION_MAJOR << "." << VERSION_MINOR << "." << VERSION_PATCH);
    
    #ifdef PLATFORM_NAME
        INFO_PRINT("Platform: " << PLATFORM_NAME);
    #endif
    
    #if MAX_BUFFER_SIZE > 512
        VERBOSE_PRINT("Large buffer size configured");
    #endif
    
    return 0;
}