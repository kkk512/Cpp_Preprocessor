# C++ Preprocessor Directive Analysis Report

**Generated:** 2025-10-03 00:05:06

## Summary

- **Files processed:** 1
- **Total directives:** 55
- **Define directives:** 23
- **Validation errors:** 0

## Files Analyzed

| File | Lines | Directives | Defines | Errors |
|------|-------|------------|---------|--------|
| `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 68 | 55 | 23 | 0 |

## Define Analysis

| Symbol | File | Line | Context |
|--------|------|------|---------|
| `CONFIG_H` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 2 | `!CONFIG_H` |
| `VERSION_MAJOR` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 5 | `!CONFIG_H` |
| `VERSION_MINOR` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 6 | `!CONFIG_H` |
| `VERSION_PATCH` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 7 | `!CONFIG_H` |
| `PLATFORM_NAME` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 11 | `!CONFIG_H && WINDOWS` |
| `PATH_SEPARATOR` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 12 | `!CONFIG_H && WINDOWS` |
| `LOG_LEVEL` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 14 | `!CONFIG_H && WINDOWS && DEBUG` |
| `LOG_LEVEL` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 16 | `!CONFIG_H && WINDOWS && !DEBUG` |
| `PLATFORM_NAME` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 19 | `!CONFIG_H && defined(LINUX)` |
| `PATH_SEPARATOR` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 20 | `!CONFIG_H && defined(LINUX)` |
| `LOG_LEVEL` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 22 | `!CONFIG_H && defined(LINUX) && DEBUG` |
| `LOG_LEVEL` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 24 | `!CONFIG_H && defined(LINUX) && !DEBUG` |
| `PLATFORM_NAME` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 27 | `!CONFIG_H && !defined(LINUX)` |
| `PATH_SEPARATOR` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 28 | `!CONFIG_H && !defined(LINUX)` |
| `LOG_LEVEL` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 29 | `!CONFIG_H && !defined(LINUX)` |
| `USE_FILE_LOGGING` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 34 | `!CONFIG_H && ENABLE_LOGGING` |
| `LOG_VERBOSE` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 36 | `!CONFIG_H && ENABLE_LOGGING && VERBOSE_LOGGING` |
| `MAX_CONNECTIONS` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 41 | `!CONFIG_H && ENABLE_NETWORKING` |
| `TIMEOUT_SECONDS` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 43 | `!CONFIG_H && ENABLE_NETWORKING && !TIMEOUT_SECONDS` |
| `BUILD_TYPE` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 54 | `!CONFIG_H && !BUILD_TYPE && DEBUG` |
| `BUILD_TYPE` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 56 | `!CONFIG_H && !BUILD_TYPE && !DEBUG` |
| `TRACK_ALLOCATIONS` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 62 | `!CONFIG_H && ENABLE_MEMORY_TRACKING` |
| `TRACK_CALL_STACK` | `C:\Users\Username\Desktop\Projects\vibe\Qoder\Project12\samples\config.h` | 64 | `!CONFIG_H && ENABLE_MEMORY_TRACKING && DETAILED_TRACKING` |

## Condition Usage

| Condition | Usage Count |
|-----------|-------------|
| `DEBUG` | 3 |
| `!CONFIG_H` | 1 |
| `WINDOWS` | 1 |
| `defined(LINUX)` | 1 |
| `ENABLE_LOGGING` | 1 |
| `VERBOSE_LOGGING` | 1 |
| `ENABLE_NETWORKING` | 1 |
| `!TIMEOUT_SECONDS` | 1 |
| `defined(DEBUG) && defined(RELEASE)` | 1 |
| `!BUILD_TYPE` | 1 |
| `ENABLE_MEMORY_TRACKING` | 1 |
| `DETAILED_TRACKING` | 1 |
