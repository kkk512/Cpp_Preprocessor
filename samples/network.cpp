// Network module with complex preprocessor directives
#include "config.h"

// Protocol definitions
#define HTTP_PORT 80
#define HTTPS_PORT 443
#define FTP_PORT 21

// Feature detection
#ifdef ENABLE_NETWORKING

    // SSL/TLS support
    #ifdef ENABLE_SSL
        #include <openssl/ssl.h>
        #define SSL_ENABLED 1
        
        #if SSL_VERSION >= 3
            #define USE_TLS_1_3
        #elif SSL_VERSION == 2
            #define USE_TLS_1_2
        #else
            #define USE_TLS_1_1
        #endif
        
        #ifndef SSL_CERT_PATH
            #ifdef WINDOWS
                #define SSL_CERT_PATH "C:\\certs\\server.crt"
            #else
                #define SSL_CERT_PATH "/etc/ssl/certs/server.crt"
            #endif
        #endif
    #else
        #define SSL_ENABLED 0
        #warning "SSL is disabled - connections will not be secure"
    #endif

    // Compression support
    #ifdef ENABLE_COMPRESSION
        #ifdef USE_ZLIB
            #include <zlib.h>
            #define COMPRESSION_TYPE "zlib"
        #elif defined(USE_GZIP)
            #include <gzip.h>
            #define COMPRESSION_TYPE "gzip"
        #else
            #define COMPRESSION_TYPE "none"
        #endif
    #endif

    // IPv6 support
    #ifdef ENABLE_IPV6
        #define SOCKET_FAMILY AF_INET6
        #define ADDRESS_SIZE sizeof(struct sockaddr_in6)
    #else
        #define SOCKET_FAMILY AF_INET
        #define ADDRESS_SIZE sizeof(struct sockaddr_in)
    #endif

    // Performance tuning
    #ifndef MAX_CONNECTIONS
        #ifdef HIGH_PERFORMANCE_MODE
            #define MAX_CONNECTIONS 1000
        #else
            #define MAX_CONNECTIONS 100
        #endif
    #endif

    #ifndef BUFFER_SIZE
        #ifdef LARGE_TRANSFERS
            #define BUFFER_SIZE 65536
        #else
            #define BUFFER_SIZE 4096
        #endif
    #endif

    // Timeout configurations
    #ifdef ENABLE_TIMEOUTS
        #ifndef CONNECT_TIMEOUT
            #define CONNECT_TIMEOUT 30
        #endif
        
        #ifndef READ_TIMEOUT
            #define READ_TIMEOUT 60
        #endif
        
        #ifndef WRITE_TIMEOUT
            #define WRITE_TIMEOUT 60
        #endif
    #endif

    // Debug networking
    #ifdef DEBUG_NETWORKING
        #define NET_DEBUG(x) printf("[NET_DEBUG] %s\n", x)
        #ifdef VERBOSE_NETWORKING
            #define NET_VERBOSE(x) printf("[NET_VERBOSE] %s\n", x)
        #else
            #define NET_VERBOSE(x)
        #endif
    #else
        #define NET_DEBUG(x)
        #define NET_VERBOSE(x)
    #endif

    // Error handling
    #ifdef STRICT_ERROR_HANDLING
        #define HANDLE_NET_ERROR(err) \
            do { \
                fprintf(stderr, "Network error: %s at %s:%d\n", err, __FILE__, __LINE__); \
                exit(1); \
            } while(0)
    #else
        #define HANDLE_NET_ERROR(err) \
            fprintf(stderr, "Network error: %s\n", err)
    #endif

#else
    // Networking disabled - provide stub definitions
    #define SSL_ENABLED 0
    #define MAX_CONNECTIONS 0
    #define NET_DEBUG(x)
    #define NET_VERBOSE(x)
    #define HANDLE_NET_ERROR(err)
    
    #warning "Networking is disabled"
#endif

// Conditional compilation for different platforms
#ifdef WINDOWS
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #define SOCKET_TYPE SOCKET
    #define CLOSE_SOCKET closesocket
    #define GET_LAST_ERROR() WSAGetLastError()
    
    #ifdef ENABLE_NETWORKING
        #pragma comment(lib, "ws2_32.lib")
        #ifdef ENABLE_SSL
            #pragma comment(lib, "ssleay32.lib")
            #pragma comment(lib, "libeay32.lib")
        #endif
    #endif
    
#elif defined(LINUX) || defined(UNIX)
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <unistd.h>
    #include <errno.h>
    #define SOCKET_TYPE int
    #define CLOSE_SOCKET close
    #define GET_LAST_ERROR() errno
    #define INVALID_SOCKET -1
    
#else
    #error "Unsupported platform for networking"
#endif

// Function declarations based on enabled features
#ifdef ENABLE_NETWORKING

    int initialize_network();
    void cleanup_network();
    
    #ifdef ENABLE_SSL
        int initialize_ssl();
        void cleanup_ssl();
    #endif
    
    #ifdef ENABLE_COMPRESSION
        int compress_data(const void* input, size_t input_size, 
                         void* output, size_t* output_size);
        int decompress_data(const void* input, size_t input_size,
                           void* output, size_t* output_size);
    #endif

#endif

// Version information
#define NETWORK_MODULE_VERSION_MAJOR 2
#define NETWORK_MODULE_VERSION_MINOR 1
#define NETWORK_MODULE_VERSION_PATCH 0

// Some intentional errors for validation testing
#ifdef ENABLE_TESTING_ERRORS
    #ifdef UNMATCHED_CONDITION
        #define ERROR_DEFINE
    // Missing #endif
    
    #ifndef ANOTHER_ERROR
        #define SYNTAX_ERROR "missing quote
    #endif
#endif