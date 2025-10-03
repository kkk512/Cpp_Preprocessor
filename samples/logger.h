#ifndef LOGGER_H
#define LOGGER_H

#include <string>
#include <fstream>

// Logger configuration
#ifndef LOG_BUFFER_SIZE
    #define LOG_BUFFER_SIZE 4096
#endif

// Log levels
#define LOG_LEVEL_ERROR   1
#define LOG_LEVEL_WARNING 2
#define LOG_LEVEL_INFO    3
#define LOG_LEVEL_DEBUG   4
#define LOG_LEVEL_VERBOSE 5

// Current log level from config
#ifndef CURRENT_LOG_LEVEL
    #ifdef DEBUG
        #define CURRENT_LOG_LEVEL LOG_LEVEL_DEBUG
    #else
        #define CURRENT_LOG_LEVEL LOG_LEVEL_INFO
    #endif
#endif

// Conditional logging macros
#if CURRENT_LOG_LEVEL >= LOG_LEVEL_ERROR
    #define LOG_ERROR(msg) Logger::instance().log(LOG_LEVEL_ERROR, msg, __FILE__, __LINE__)
#else
    #define LOG_ERROR(msg)
#endif

#if CURRENT_LOG_LEVEL >= LOG_LEVEL_WARNING
    #define LOG_WARNING(msg) Logger::instance().log(LOG_LEVEL_WARNING, msg, __FILE__, __LINE__)
#else
    #define LOG_WARNING(msg)
#endif

#if CURRENT_LOG_LEVEL >= LOG_LEVEL_INFO
    #define LOG_INFO(msg) Logger::instance().log(LOG_LEVEL_INFO, msg, __FILE__, __LINE__)
#else
    #define LOG_INFO(msg)
#endif

#if CURRENT_LOG_LEVEL >= LOG_LEVEL_DEBUG
    #define LOG_DEBUG(msg) Logger::instance().log(LOG_LEVEL_DEBUG, msg, __FILE__, __LINE__)
#else
    #define LOG_DEBUG(msg)
#endif

#if CURRENT_LOG_LEVEL >= LOG_LEVEL_VERBOSE
    #define LOG_VERBOSE(msg) Logger::instance().log(LOG_LEVEL_VERBOSE, msg, __FILE__, __LINE__)
#else
    #define LOG_VERBOSE(msg)
#endif

// Output destinations
#ifdef LOG_TO_FILE
    #define OUTPUT_FILE "application.log"
#endif

#ifdef LOG_TO_CONSOLE
    #define USE_CONSOLE_OUTPUT
#endif

// Thread safety
#ifdef ENABLE_THREADING
    #ifdef USE_MUTEX_LOGGING
        #define THREAD_SAFE_LOGGING
    #endif
#endif

// Performance optimizations
#ifdef OPTIMIZE_LOGGING
    #define FAST_LOGGING
    #ifdef BUFFER_LOGS
        #define USE_LOG_BUFFER
    #endif
#endif

class Logger {
public:
    static Logger& instance();
    
    void log(int level, const std::string& message, 
             const char* file = nullptr, int line = 0);
    
    #ifdef ENABLE_LOG_FILTERING
        void setFilter(const std::string& filter);
    #endif
    
    #ifdef ENABLE_LOG_ROTATION
        void rotateLog();
    #endif

private:
    Logger() = default;
    
    #ifdef LOG_TO_FILE
        std::ofstream m_logFile;
    #endif
    
    #ifdef USE_LOG_BUFFER
        char m_buffer[LOG_BUFFER_SIZE];
    #endif
};

// Utility macros
#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)

#ifdef DEBUG
    #define ASSERT(condition) \
        if (!(condition)) { \
            LOG_ERROR("Assertion failed: " #condition " at " __FILE__ ":" TOSTRING(__LINE__)); \
        }
#else
    #define ASSERT(condition)
#endif

#endif // LOGGER_H