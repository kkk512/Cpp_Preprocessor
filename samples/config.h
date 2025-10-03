#ifndef CONFIG_H
#define CONFIG_H

// Basic configuration defines
#define VERSION_MAJOR 1
#define VERSION_MINOR 2
#define VERSION_PATCH 3

// Platform-specific configurations
#ifdef WINDOWS
    #define PLATFORM_NAME "Windows"
    #define PATH_SEPARATOR "\\"
    #ifdef DEBUG
        #define LOG_LEVEL 3
    #else
        #define LOG_LEVEL 1
    #endif
#elif defined(LINUX)
    #define PLATFORM_NAME "Linux"
    #define PATH_SEPARATOR "/"
    #ifdef DEBUG
        #define LOG_LEVEL 3
    #else
        #define LOG_LEVEL 1
    #endif
#else
    #define PLATFORM_NAME "Unknown"
    #define PATH_SEPARATOR "/"
    #define LOG_LEVEL 0
#endif

// Feature flags
#ifdef ENABLE_LOGGING
    #define USE_FILE_LOGGING
    #ifdef VERBOSE_LOGGING
        #define LOG_VERBOSE
    #endif
#endif

#ifdef ENABLE_NETWORKING
    #define MAX_CONNECTIONS 100
    #ifndef TIMEOUT_SECONDS
        #define TIMEOUT_SECONDS 30
    #endif
#endif

// Build configuration
#if defined(DEBUG) && defined(RELEASE)
    #error "Cannot define both DEBUG and RELEASE"
#endif

#ifndef BUILD_TYPE
    #ifdef DEBUG
        #define BUILD_TYPE "Debug"
    #else
        #define BUILD_TYPE "Release"
    #endif
#endif

// Memory management
#ifdef ENABLE_MEMORY_TRACKING
    #define TRACK_ALLOCATIONS
    #ifdef DETAILED_TRACKING
        #define TRACK_CALL_STACK
    #endif
#endif

#endif // CONFIG_H