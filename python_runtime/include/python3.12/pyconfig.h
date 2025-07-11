/* pyconfig.h.  Generated from pyconfig.h.in by configure.  */
/* pyconfig.h.in.  Generated from configure.in by autoheader.  */


#ifndef Py_PYCONFIG_H
#define Py_PYCONFIG_H


/* Define if building universal (internal helper macro) */
/* #undef AC_APPLE_UNIVERSAL_BUILD */

/* BUILD_GNU_TYPE + AIX_BUILDDATE are used to construct the PEP425 tag of the
   build system. [Python 3.9] */
/* #undef AIX_BUILDDATE */

/* Define for AIX if your compiler is a genuine IBM xlC/xlC_r and you want
   support for AIX C++ shared extension modules. */
/* #undef AIX_GENUINE_CPLUSPLUS */

/* Alternative SOABI used in debug build to load C extensions built in release
   mode [Python 3.8] */
/* #undef ALT_SOABI */

/* The Android API level. [Python 3.7] */
/* #undef ANDROID_API_LEVEL */

/* Define this if you have AtheOS threads. [Python 2.7] */
/* #undef ATHEOS_THREADS */

/* Define this if you have BeOS threads. [Python 2.7] */
/* #undef BEOS_THREADS */

/* Define if you have the Mach cthreads package [Python 2.7] */
/* #undef C_THREADS */

/* Define if C doubles are 64-bit IEEE 754 binary format, stored in ARM
   mixed-endian order (byte order 45670123) */
/* #undef DOUBLE_IS_ARM_MIXED_ENDIAN_IEEE754 */

/* Define if C doubles are 64-bit IEEE 754 binary format, stored with the most
   significant byte first */
/* #undef DOUBLE_IS_BIG_ENDIAN_IEEE754 */

/* Define if C doubles are 64-bit IEEE 754 binary format, stored with the
   least significant byte first */
#define DOUBLE_IS_LITTLE_ENDIAN_IEEE754 1

/* Define if --enable-ipv6 is specified */
#define ENABLE_IPV6 1

/* Define to 1 if your system stores words within floats with the most
   significant word first [Python 3.8] */
/* #undef FLOAT_WORDS_BIGENDIAN */

/* Define if flock needs to be linked with bsd library. */
/* #undef FLOCK_NEEDS_LIBBSD */

/* Define if getpgrp() must be called as getpgrp(0). */
/* #undef GETPGRP_HAVE_ARG */

/* Define if gettimeofday() does not have second (timezone) argument This is
   the case on Motorola V4 (R40V4.2) */
/* #undef GETTIMEOFDAY_NO_TZ */

/* Define to 1 if you have the `accept' function. [Python 3.11] */
#define HAVE_ACCEPT 1

/* Define to 1 if you have the `accept4' function. [Python 3] */
/* #undef HAVE_ACCEPT4 */

/* Define to 1 if you have the `acosh' function. */
#define HAVE_ACOSH 1

/* struct addrinfo (netdb.h) */
#define HAVE_ADDRINFO 1

/* Define to 1 if you have the `alarm' function. */
#define HAVE_ALARM 1

/* Define if aligned memory access is required [Python 3] */
/* #undef HAVE_ALIGNED_REQUIRED */

/* Define to 1 if you have the <alloca.h> header file. */
#define HAVE_ALLOCA_H 1

/* Define this if your time.h defines altzone. */
/* #undef HAVE_ALTZONE */

/* Define to 1 if you have the `asinh' function. */
#define HAVE_ASINH 1

/* Define to 1 if you have the <asm/types.h> header file. */
/* #undef HAVE_ASM_TYPES_H */

/* Define to 1 if you have the `atanh' function. */
#define HAVE_ATANH 1

/* Define if GCC supports __attribute__((format(PyArg_ParseTuple, 2, 3))) [Python 2.7] */
/* #undef HAVE_ATTRIBUTE_FORMAT_PARSETUPLE */

/* Define to 1 if you have the `bind' function. [Python 3.11] */
#define HAVE_BIND 1

/* Define to 1 if you have the `bind_textdomain_codeset' function. */
/* #undef HAVE_BIND_TEXTDOMAIN_CODESET */

/* Define to 1 if you have the <bluetooth/bluetooth.h> header file. */
/* #undef HAVE_BLUETOOTH_BLUETOOTH_H */

/* Define to 1 if you have the <bluetooth.h> header file. */
/* #undef HAVE_BLUETOOTH_H */

/* Define if mbstowcs(NULL, "text", 0) does not return the number of wide
   chars that would be converted. [Python 3] */
/* #undef HAVE_BROKEN_MBSTOWCS */

/* Define if nice() returns success/failure instead of the new priority. */
/* #undef HAVE_BROKEN_NICE */

/* Define if the system reports an invalid PIPE_BUF value. */
/* #undef HAVE_BROKEN_PIPE_BUF */

/* Define if poll() sets errno on invalid file descriptors. */
/* #undef HAVE_BROKEN_POLL */

/* Define if the Posix semaphores do not work on your system */
/* #undef HAVE_BROKEN_POSIX_SEMAPHORES */

/* Define if pthread_sigmask() does not work on your system. */
/* #undef HAVE_BROKEN_PTHREAD_SIGMASK */

/* define to 1 if your sem_getvalue is broken. */
#define HAVE_BROKEN_SEM_GETVALUE 1

/* Define if `unsetenv` does not return an int. */
/* #undef HAVE_BROKEN_UNSETENV */

/* Has builtin atomics [Python 3] */
#define HAVE_BUILTIN_ATOMIC 1

/* Define this if you have the type _Bool. */
#define HAVE_C99_BOOL 1

/* Define to 1 if you have the 'chflags' function. */
#define HAVE_CHFLAGS 1

/* Define to 1 if you have the `chmod' function. [Python 3.11] */
#define HAVE_CHMOD 1

/* Define to 1 if you have the `chown' function. */
#define HAVE_CHOWN 1

/* Define if you have the 'chroot' function. */
/* #undef HAVE_CHROOT */

/* Define to 1 if you have the `clock' function. */
#define HAVE_CLOCK 1

/* Define to 1 if you have the `clock_getres' function. [Python 3] */
/* #undef HAVE_CLOCK_GETRES */

/* Define to 1 if you have the `clock_gettime' function. [Python 3] */
/* #undef HAVE_CLOCK_GETTIME */

/* Define to 1 if you have the `clock_settime' function. [Python 3.6] */
/* #undef HAVE_CLOCK_SETTIME */

/* Define if the C compiler supports computed gotos. */
#define HAVE_COMPUTED_GOTOS 1

/* Define to 1 if you have the `confstr' function. */
#define HAVE_CONFSTR 1

/* Define to 1 if you have the <conio.h> header file. */
/* #undef HAVE_CONIO_H */

/* Define to 1 if you have the `connect' function. [Python 3.11] */
#define HAVE_CONNECT 1

/* Define to 1 if you have the `copysign' function. */
#define HAVE_COPYSIGN 1

/* Define to 1 if you have the `copy_file_range' function. [Python 3.8] */
/* #undef HAVE_COPY_FILE_RANGE */

/* Define to 1 if you have the <crypt.h> header file. [Python 3.6] */
/* #undef HAVE_CRYPT_H */

/* Define if you have the crypt_r() function. [Python 3.7] */
/* #undef HAVE_CRYPT_R */

/* Define to 1 if you have the `ctermid' function. */
#define HAVE_CTERMID 1

/* Define if you have the 'ctermid_r' function. */
#define HAVE_CTERMID_R 1

/* Define if you have the 'filter' function. [Python 3.6] */
#define HAVE_CURSES_FILTER 1

/* Define to 1 if you have the <curses.h> header file. */
#define HAVE_CURSES_H 1

/* Define if you have the 'has_key' function. [Python 3.6] */
#define HAVE_CURSES_HAS_KEY 1

/* Define if you have the 'immedok' function. [Python 3.6] */
#define HAVE_CURSES_IMMEDOK 1

/* Define if you have the 'is_pad' function or macro. [Python 3.6] */
#define HAVE_CURSES_IS_PAD 1

/* Define if you have the 'is_term_resized' function. */
#define HAVE_CURSES_IS_TERM_RESIZED 1

/* Define if you have the 'resizeterm' function. */
#define HAVE_CURSES_RESIZETERM 1

/* Define if you have the 'resize_term' function. */
#define HAVE_CURSES_RESIZE_TERM 1

/* Define if you have the 'syncok' function. [Python 3.6] */
#define HAVE_CURSES_SYNCOK 1

/* Define if you have the 'typeahead' function. [Python 3.6] */
#define HAVE_CURSES_TYPEAHEAD 1

/* Define if you have the 'use_env' function. [Python 3.6] */
#define HAVE_CURSES_USE_ENV 1

/* Define if you have the 'wchgat' function. [Python 3.6] */
#define HAVE_CURSES_WCHGAT 1

/* Define to 1 if you have the declaration of `isfinite', and to 0 if you
   don't. */
#define HAVE_DECL_ISFINITE 1

/* Define to 1 if you have the declaration of `isinf', and to 0 if you don't.
   */
#define HAVE_DECL_ISINF 1

/* Define to 1 if you have the declaration of `isnan', and to 0 if you don't.
   */
#define HAVE_DECL_ISNAN 1

/* Define to 1 if you have the declaration of `RTLD_DEEPBIND', and to 0 if you
   don't. [Python 3.6] */
/* #undef HAVE_DECL_RTLD_DEEPBIND */

/* Define to 1 if you have the declaration of `RTLD_GLOBAL', and to 0 if you
   don't. [Python 3.6] */
#define HAVE_DECL_RTLD_GLOBAL 1

/* Define to 1 if you have the declaration of `RTLD_LAZY', and to 0 if you
   don't. [Python 3.6] */
#define HAVE_DECL_RTLD_LAZY 1

/* Define to 1 if you have the declaration of `RTLD_LOCAL', and to 0 if you
   don't. [Python 3.6] */
#define HAVE_DECL_RTLD_LOCAL 1

/* Define to 1 if you have the declaration of `RTLD_MEMBER', and to 0 if you
   don't. [Python 3.7] */
/* #undef HAVE_DECL_RTLD_MEMBER */

/* Define to 1 if you have the declaration of `RTLD_NODELETE', and to 0 if you
   don't. [Python 3.6] */
#define HAVE_DECL_RTLD_NODELETE 1

/* Define to 1 if you have the declaration of `RTLD_NOLOAD', and to 0 if you
   don't. [Python 3.6] */
#define HAVE_DECL_RTLD_NOLOAD 1

/* Define to 1 if you have the declaration of `RTLD_NOW', and to 0 if you
   don't. [Python 3.6] */
#define HAVE_DECL_RTLD_NOW 1

/* Define to 1 if you have the declaration of `tzname', and to 0 if you don't.
   */
/* #undef HAVE_DECL_TZNAME */

/* Define to 1 if you have the device macros. */
#define HAVE_DEVICE_MACROS 1

/* Define to 1 if you have the /dev/ptc device file. */
/* #undef HAVE_DEV_PTC */

/* Define to 1 if you have the /dev/ptmx device file. */
#define HAVE_DEV_PTMX 1

/* Define to 1 if you have the <direct.h> header file. */
/* #undef HAVE_DIRECT_H */

/* Define to 1 if the dirent structure has a d_type field [Python 3] */
#define HAVE_DIRENT_D_TYPE 1

/* Define to 1 if you have the <dirent.h> header file, and it defines `DIR'.
   */
#define HAVE_DIRENT_H 1

/* Define if you have the 'dirfd' function or macro. [Python 3] */
#define HAVE_DIRFD 1

/* Define to 1 if you have the <dlfcn.h> header file. */
#define HAVE_DLFCN_H 1

/* Define to 1 if you have the `dlopen' function. */
#define HAVE_DLOPEN 1

/* Define to 1 if you have the `dup2' function. */
#define HAVE_DUP2 1

/* Define to 1 if you have the `dup3' function. [Python 3] */
/* #undef HAVE_DUP3 */

/* Define if you have the '_dyld_shared_cache_contains_path' function. [Python 3.8] */
#define HAVE_DYLD_SHARED_CACHE_CONTAINS_PATH 1

/* Defined when any dynamic module loading is enabled. */
#define HAVE_DYNAMIC_LOADING 1

/* Define to 1 if you have the <endian.h> header file. [Python 3] */
/* #undef HAVE_ENDIAN_H */

/* Define if you have the 'epoll' functions. */
/* #undef HAVE_EPOLL */

/* Define if you have the 'epoll_create1' function. [Python 3] */
/* #undef HAVE_EPOLL_CREATE1 */

/* Define to 1 if you have the `erf' function. */
#define HAVE_ERF 1

/* Define to 1 if you have the `erfc' function. */
#define HAVE_ERFC 1

/* Define to 1 if you have the <errno.h> header file. */
#define HAVE_ERRNO_H 1

/* Define to 1 if you have the `execv' function. */
#define HAVE_EXECV 1

/* Define to 1 if you have the `explicit_bzero' function. [Python 3.8] */
/* #undef HAVE_EXPLICIT_BZERO */

/* Define to 1 if you have the `explicit_memset' function. [Python 3.8] */
/* #undef HAVE_EXPLICIT_MEMSET */

/* Define to 1 if you have the `expm1' function. */
#define HAVE_EXPM1 1

/* Define to 1 if you have the `faccessat' function. [Python 3] */
#define HAVE_FACCESSAT 1

/* Define if you have the 'fchdir' function. */
#define HAVE_FCHDIR 1

/* Define to 1 if you have the `fchmod' function. */
#define HAVE_FCHMOD 1

/* Define to 1 if you have the `fchmodat' function. [Python 3] */
#define HAVE_FCHMODAT 1

/* Define to 1 if you have the `fchown' function. */
#define HAVE_FCHOWN 1

/* Define to 1 if you have the `fchownat' function. [Python 3] */
#define HAVE_FCHOWNAT 1

/* Define to 1 if you have the <fcntl.h> header file. */
#define HAVE_FCNTL_H 1

/* Define if you have the 'fdatasync' function. */
/* #undef HAVE_FDATASYNC */

/* Define to 1 if you have the `fdopendir' function. [Python 3] */
#define HAVE_FDOPENDIR 1

/* Define to 1 if you have the `fdwalk' function. [Python 3.8] */
/* #undef HAVE_FDWALK */

/* Define to 1 if you have the `fexecve' function. [Python 3] */
/* #undef HAVE_FEXECVE */

/* Define to 1 if you have the `finite' function. */
/* #undef HAVE_FINITE */

/* Define to 1 if you have the `flock' function. */
#define HAVE_FLOCK 1

/* Define to 1 if you have the `fork' function. */
#define HAVE_FORK 1

/* Define to 1 if you have the `forkpty' function. */
#define HAVE_FORKPTY 1

/* Define to 1 if you have the `fpathconf' function. */
#define HAVE_FPATHCONF 1

/* Define to 1 if you have the `fseek64' function. */
/* #undef HAVE_FSEEK64 */

/* Define to 1 if you have the `fseeko' function. */
#define HAVE_FSEEKO 1

/* Define to 1 if you have the `fstatat' function. [Python 3] */
#define HAVE_FSTATAT 1

/* Define to 1 if you have the `fstatvfs' function. */
#define HAVE_FSTATVFS 1

/* Define if you have the 'fsync' function. */
#define HAVE_FSYNC 1

/* Define to 1 if you have the `ftell64' function. */
/* #undef HAVE_FTELL64 */

/* Define to 1 if you have the `ftello' function. */
#define HAVE_FTELLO 1

/* Define to 1 if you have the `ftime' function. */
#define HAVE_FTIME 1

/* Define to 1 if you have the `ftruncate' function. */
#define HAVE_FTRUNCATE 1

/* Define to 1 if you have the `futimens' function. [Python 3] */
#define HAVE_FUTIMENS 1

/* Define to 1 if you have the `futimes' function. [Python 3] */
#define HAVE_FUTIMES 1

/* Define to 1 if you have the `futimesat' function. [Python 3] */
/* #undef HAVE_FUTIMESAT */

/* Define to 1 if you have the `gai_strerror' function. */
#define HAVE_GAI_STRERROR 1

/* Define to 1 if you have the `gamma' function. */
/* #undef HAVE_GAMMA */

/* Define if we can use gcc inline assembler to get and set mc68881 fpcr [Python 3] */
/* #undef HAVE_GCC_ASM_FOR_MC68881 */

/* Define if we can use x64 gcc inline assembler [Python 3] */
/* #undef HAVE_GCC_ASM_FOR_X64 */

/* Define if we can use gcc inline assembler to get and set x87 control word
   */
/* #undef HAVE_GCC_ASM_FOR_X87 */

/* Define if your compiler provides __uint128_t [Python 3] */
#define HAVE_GCC_UINT128_T 1

/* Define if you have the getaddrinfo function. */
#define HAVE_GETADDRINFO 1

/* Define to 1 if you have the `getcwd' function. [Python 2.7] */
/* #undef HAVE_GETCWD */

/* Define this if you have flockfile(), getc_unlocked(), and funlockfile() */
#define HAVE_GETC_UNLOCKED 1

/* Define to 1 if you have the `getegid' function. [Python 3.11] */
#define HAVE_GETEGID 1

/* Define to 1 if you have the `geteuid' function. [Python 3.11] */
#define HAVE_GETEUID 1

/* Define to 1 if you have the `getentropy' function. [Python 3] */
#define HAVE_GETENTROPY 1

/* Define to 1 if you have the `getgid' function. [Python 3.1] */
#define HAVE_GETGID 1

/* Define to 1 if you have the `getgrgid_r' function. [Python 3.8] */
#define HAVE_GETGRGID_R 1

/* Define to 1 if you have the `getgrnam_r' function. [Python 3.8] */
#define HAVE_GETGRNAM_R 1

/* Define to 1 if you have the `getgrouplist' function. [Python 3] */
#define HAVE_GETGROUPLIST 1

/* Define to 1 if you have the `getgroups' function. */
#define HAVE_GETGROUPS 1

/* Define to 1 if you have the `gethostbyaddr' function. [Python 3.11] */
#define HAVE_GETHOSTBYADDR 1

/* Define to 1 if you have the `gethostbyname' function. */
#define HAVE_GETHOSTBYNAME 1

/* Define this if you have some version of gethostbyname_r() */
/* #undef HAVE_GETHOSTBYNAME_R */

/* Define this if you have the 3-arg version of gethostbyname_r(). */
/* #undef HAVE_GETHOSTBYNAME_R_3_ARG */

/* Define this if you have the 5-arg version of gethostbyname_r(). */
/* #undef HAVE_GETHOSTBYNAME_R_5_ARG */

/* Define this if you have the 6-arg version of gethostbyname_r(). */
/* #undef HAVE_GETHOSTBYNAME_R_6_ARG */

/* Define if you have the gethostname function. [Python 3.11] */
#define HAVE_GETHOSTNAME 1

/* Define to 1 if you have the `getitimer' function. */
#define HAVE_GETITIMER 1

/* Define to 1 if you have the `getloadavg' function. */
#define HAVE_GETLOADAVG 1

/* Define to 1 if you have the `getlogin' function. */
#define HAVE_GETLOGIN 1

/* Define to 1 if you have the `getnameinfo' function. */
#define HAVE_GETNAMEINFO 1

/* Define if you have the 'getppid' function. [Python 3.11] */
#define HAVE_GETPPID 1

/* Define if you have the 'getpagesize' function. */
/* #undef HAVE_GETPAGESIZE */

/* Define to 1 if you have the `getpeername' function. */
#define HAVE_GETPEERNAME 1

/* Define to 1 if you have the `getpgid' function. */
#define HAVE_GETPGID 1

/* Define to 1 if you have the `getpgrp' function. */
#define HAVE_GETPGRP 1

/* Define to 1 if you have the `getpid' function. */
#define HAVE_GETPID 1

/* Define to 1 if you have the `getpriority' function. */
#define HAVE_GETPRIORITY 1

/* Define to 1 if you have the `getpwent' function. */
#define HAVE_GETPWENT 1

/* Define to 1 if you have the `getpwnam_r' function. [Python 3.8] */
#define HAVE_GETPWNAM_R 1

/* Define to 1 if you have the `getpwuid_r' function. [Python 3.8] */
#define HAVE_GETPWUID_R 1

/* Define to 1 if the getrandom() function is available [Python 3] */
/* #undef HAVE_GETRANDOM */

/* Define to 1 if the Linux getrandom() syscall is available [Python 3] */
/* #undef HAVE_GETRANDOM_SYSCALL */

/* Define to 1 if you have the `getresgid' function. */
/* #undef HAVE_GETRESGID */

/* Define to 1 if you have the `getresuid' function. */
/* #undef HAVE_GETRESUID */

/* Define to 1 if you have the `getrusage' function. [Python 3.11] */
#define HAVE_GETRUSAGE 1

/* Define to 1 if you have the `getservbyname' function. [Python 3.11] */
#define HAVE_GETSERVBYNAME 1

/* Define if you have the 'getservbyport' function. [Python 3.11] */
#define HAVE_GETSERVBYPORT 1

/* Define to 1 if you have the `getsid' function. */
#define HAVE_GETSID 1

/* Define to 1 if you have the `getsockname' function. [Python 3.11] */
#define HAVE_GETSOCKNAME 1

/* Define to 1 if you have the `getspent' function. */
/* #undef HAVE_GETSPENT */

/* Define to 1 if you have the `getspnam' function. */
/* #undef HAVE_GETSPNAM */

/* Define to 1 if you have the `gettimeofday' function. */
#define HAVE_GETTIMEOFDAY 1

/* Define to 1 if you have the `getuid' function. [Python 3.11] */
#define HAVE_GETUID 1

/* Define to 1 if you have the `getwd' function. */
/* #undef HAVE_GETWD */

/* Define if glibc has incorrect _FORTIFY_SOURCE wrappers for memmove and
   bcopy. [Python 3] */
/* #undef HAVE_GLIBC_MEMMOVE_BUG */

/* Define to 1 if you have the <grp.h> header file. */
#define HAVE_GRP_H 1

/* Define if you have the 'hstrerror' function. */
#define HAVE_HSTRERROR 1

/* Define this if you have le64toh() [Python 3] */
/* #undef HAVE_HTOLE64 */

/* Define to 1 if you have the `hypot' function. */
#define HAVE_HYPOT 1

/* Define to 1 if you have the <ieeefp.h> header file. */
/* #undef HAVE_IEEEFP_H */

/* Define to 1 if you have the `if_nameindex' function. [Python 3] */
#define HAVE_IF_NAMEINDEX 1

/* Define if you have the 'inet_aton' function. */
#define HAVE_INET_ATON 1

/* Define if you have the 'inet_pton' function. */
#define HAVE_INET_PTON 1

/* Define to 1 if you have the `initgroups' function. */
#define HAVE_INITGROUPS 1

/* Define if your compiler provides int32_t. */
#define HAVE_INT32_T 1

/* Define if your compiler provides int64_t. */
#define HAVE_INT64_T 1

/* Define to 1 if you have the <inttypes.h> header file. */
#define HAVE_INTTYPES_H 1

/* Define to 1 if you have the <io.h> header file. */
/* #undef HAVE_IO_H */

/* Define if gcc has the ipa-pure-const bug. [Python 3] */
/* #undef HAVE_IPA_PURE_CONST_BUG */

/* Define to 1 if you have the `kill' function. */
#define HAVE_KILL 1

/* Define to 1 if you have the `killpg' function. */
#define HAVE_KILLPG 1

/* Define if you have the 'kqueue' functions. */
#define HAVE_KQUEUE 1

/* Define to 1 if you have the <langinfo.h> header file. */
#define HAVE_LANGINFO_H 1

/* Defined to enable large file support when an off_t is bigger than a long
   and long long is available and at least as big as an off_t. You may need to
   add some flags for configuration and compilation to enable this mode. (For
   Solaris and Linux, the necessary defines are already defined.) */
/* #undef HAVE_LARGEFILE_SUPPORT */

/* Define to 1 if you have the 'lchflags' function. */
#define HAVE_LCHFLAGS 1

/* Define to 1 if you have the `lchmod' function. */
#define HAVE_LCHMOD 1

/* Define to 1 if you have the `lchown' function. */
#define HAVE_LCHOWN 1

/* Define to 1 if you have the `lgamma' function. */
#define HAVE_LGAMMA 1

/* Define to 1 if you have the `dl' library (-ldl). */
/* #undef HAVE_LIBDL */

/* Define to 1 if you have the `dld' library (-ldld). */
/* #undef HAVE_LIBDLD */

/* Define to 1 if you have the `ieee' library (-lieee). */
/* #undef HAVE_LIBIEEE */

/* Define to 1 if you have the <libintl.h> header file. */
/* #undef HAVE_LIBINTL_H */

/* Define if you have the readline library (-lreadline). */
#define HAVE_LIBREADLINE 1

/* Define to 1 if you have the `resolv' library (-lresolv). */
/* #undef HAVE_LIBRESOLV */

/* Define to 1 if you have the `sendfile' library (-lsendfile). [Python 3] */
/* #undef HAVE_LIBSENDFILE */

/* Define to 1 if you have the <libutil.h> header file. */
/* #undef HAVE_LIBUTIL_H */

/* Define to 1 if you have the `uuid' library (-luuid). [Python 3.9] */
/* #undef HAVE_LIBUUID */

/* Define if you have the 'link' function. */
#define HAVE_LINK 1

/* Define to 1 if you have the `linkat' function. [Python 3] */
#define HAVE_LINKAT 1

/* Define to 1 if you have the <linux/auxvec.h> header file. [Python 3.9] */
/* #undef HAVE_LINUX_AUXVEC_H */

/* Define to 1 if you have the <linux/can/bcm.h> header file. [Python 3] */
/* #undef HAVE_LINUX_CAN_BCM_H */

/* Define to 1 if you have the <linux/can.h> header file. [Python 3] */
/* #undef HAVE_LINUX_CAN_H */

/* Define to 1 if you have the <linux/can/j1939.h> header file. [Python 3.9] */
/* #undef HAVE_LINUX_CAN_J1939_H */

/* Define if compiling using Linux 3.6 or later. [Python 3] */
/* #undef HAVE_LINUX_CAN_RAW_FD_FRAMES */

/* Define to 1 if you have the <linux/can/raw.h> header file. [Python 3] */
/* #undef HAVE_LINUX_CAN_RAW_H */

/* Define if compiling using Linux 4.1 or later. [Python 3.9] */
/* #undef HAVE_LINUX_CAN_RAW_JOIN_FILTERS */

/* Define to 1 if you have the <linux/memfd.h> header file. [Python 3.8] */
/* #undef HAVE_LINUX_MEMFD_H */

/* Define to 1 if you have the <linux/netlink.h> header file. */
/* #undef HAVE_LINUX_NETLINK_H */

/* Define to 1 if you have the <linux/qrtr.h> header file. [Python 3.8] */
/* #undef HAVE_LINUX_QRTR_H */

/* Define to 1 if you have the <linux/random.h> header file. */
/* #undef HAVE_LINUX_RANDOM_H */

/* Define to 1 if you have the <linux/tipc.h> header file. */
/* #undef HAVE_LINUX_TIPC_H */

/* Define to 1 if you have the <linux/vm_sockets.h> header file. [Python 3.7] */
/* #undef HAVE_LINUX_VM_SOCKETS_H */

/* Define to 1 if you have the <linux/wait.h> header file. [Python 3.9] */
/* #undef HAVE_LINUX_WAIT_H */

/* Define to 1 if you have the `listen' function. [Python 3.11] */
#define HAVE_LISTEN 1

/* Define to 1 if you have the `lockf' function. [Python 3] */
#define HAVE_LOCKF 1

/* Define to 1 if you have the `log1p' function. */
#define HAVE_LOG1P 1

/* Define to 1 if you have the `log2' function. [Python 3] */
#define HAVE_LOG2 1

/* Define this if you have the type long double. */
/* #undef HAVE_LONG_DOUBLE */

/* Define this if you have the type long long. */
#define HAVE_LONG_LONG 1

/* Define to 1 if you have the `lstat' function. */
#define HAVE_LSTAT 1

/* Define to 1 if you have the `lutimes' function. [Python 3] */
#define HAVE_LUTIMES 1

/* Define to 1 if you have the `madvise' function. [Python 3.8] */
#define HAVE_MADVISE 1

/* Define this if you have the makedev macro. */
#define HAVE_MAKEDEV 1

/* Define to 1 if you have the `mbrtowc' function. [Python 3] */
#define HAVE_MBRTOWC 1

/* Define if you have the 'memfd_create' function. [Python 3.8] */
/* #undef HAVE_MEMFD_CREATE */

/* Define to 1 if you have the `memmove' function. */
#define HAVE_MEMMOVE 1

/* Define to 1 if you have the <memory.h> header file. */
#define HAVE_MEMORY_H 1

/* Define to 1 if you have the `memrchr' function. [Python 3] */
/* #undef HAVE_MEMRCHR */

/* Define to 1 if you have the `mkdirat' function. [Python 3] */
#define HAVE_MKDIRAT 1

/* Define to 1 if you have the `mkfifo' function. */
#define HAVE_MKFIFO 1

/* Define to 1 if you have the `mkfifoat' function. [Python 3] */
#define HAVE_MKFIFOAT 1

/* Define to 1 if you have the `mknod' function. */
#define HAVE_MKNOD 1

/* Define to 1 if you have the `mknodat' function. [Python 3] */
#define HAVE_MKNODAT 1

/* Define to 1 if you have the `mktime' function. */
#define HAVE_MKTIME 1

/* Define to 1 if you have the `mmap' function. */
#define HAVE_MMAP 1

/* Define to 1 if you have the `mremap' function. */
/* #undef HAVE_MREMAP */

/* Define to 1 if you have the <ncurses.h> header file. */
#define HAVE_NCURSES_H 1

/* Define to 1 if you have the <ncurses/panel.h> header file. */
/* #undef HAVE_NCURSES_PANEL_H */

/* Define to 1 if you have the <ncursesw/panel.h> header file. */
/* #undef HAVE_NCURSESW_PANEL_H */

/* Define to 1 if you have the <panel.h> header file. */
#define HAVE_PANEL_H 1

/* Define to 1 if you have the <netdb.h> header file. */
#define HAVE_NETDB_H 1

/* Define to 1 if you have the <ndir.h> header file, and it defines `DIR'. */
/* #undef HAVE_NDIR_H */

/* Define to 1 if you have the <netpacket/packet.h> header file. */
/* #undef HAVE_NETPACKET_PACKET_H */

/* Define to 1 if you have the <net/if.h> header file. [Python 3] */
#define HAVE_NET_IF_H 1

/* Define to 1 if you have the `nice' function. */
#define HAVE_NICE 1

/* Define if the internal form of wchar_t in non-Unicode locales is not
   Unicode. [Python 3.9] */
/* #undef HAVE_NON_UNICODE_WCHAR_T_REPRESENTATION */

/* Define to 1 if you have the `openat' function. [Python 3] */
#define HAVE_OPENAT 1

/* Define to 1 if you have the `opendir' function. [Python 3.11] */
#define HAVE_OPENDIR 1

/* Define to 1 if you have the `openpty' function. */
#define HAVE_OPENPTY 1

/* Define if compiling using MacOS X 10.5 SDK or later. */
/* #undef HAVE_OSX105_SDK */

/* Define to 1 if you have the `pathconf' function. */
#define HAVE_PATHCONF 1

/* Define to 1 if you have the `pause' function. */
#define HAVE_PAUSE 1

/* Define to 1 if you have the `pipe' function. [Python 3.11] */
#define HAVE_PIPE 1

/* Define to 1 if you have the `pipe2' function. [Python 3] */
/* #undef HAVE_PIPE2 */

/* Define to 1 if you have the `plock' function. */
/* #undef HAVE_PLOCK */

/* Define to 1 if you have the `poll' function. */
#define HAVE_POLL 1

/* Define to 1 if you have the <poll.h> header file. */
#define HAVE_POLL_H 1

/* Define to 1 if you have the `posix_fadvise' function. [Python 3] */
/* #undef HAVE_POSIX_FADVISE */

/* Define to 1 if you have the `posix_fallocate' function. [Python 3] */
/* #undef HAVE_POSIX_FALLOCATE */

/* Define to 1 if you have the `posix_spawn' function. [Python 3.7] */
/* #undef HAVE_POSIX_SPAWN */

/* Define to 1 if you have the `posix_spawnp' function. [Python 3.8] */
/* #undef HAVE_POSIX_SPAWNP */

/* Define to 1 if you have the `pread' function. [Python 3] */
#define HAVE_PREAD 1

/* Define to 1 if you have the `preadv' function. [Python 3.7] */
#define HAVE_PREADV 1

/* Define to 1 if you have the `preadv2' function. [Python 3.7] */
/* #undef HAVE_PREADV2 */

/* Define if you have the 'prlimit' functions. [Python 3] */
/* #undef HAVE_PRLIMIT */

/* Define if you have the '_dyld_shared_cache_contains_path' function. [Python 3.8] */
#define HAVE_DYLD_SHARED_CACHE_CONTAINS_PATH 1

/* Define to 1 if you have the <process.h> header file. */
/* #undef HAVE_PROCESS_H */

/* Define if your compiler supports function prototype */
#define HAVE_PROTOTYPES 1

/* Define if you have GNU PTH threads. [Python 2.7] */
/* #undef HAVE_PTH */

/* Define to 1 if you have the `pthread_atfork' function. */
#define HAVE_PTHREAD_ATFORK 1

/* Define to 1 if you have the `pthread_condattr_setclock' function. [Python 3.8] */
/* #undef HAVE_PTHREAD_CONDATTR_SETCLOCK */

/* Defined for Solaris 2.6 bug in pthread header. */
/* #undef HAVE_PTHREAD_DESTRUCTOR */

/* Define to 1 if you have the `pthread_getcpuclockid' function. [Python 3.7] */
/* #undef HAVE_PTHREAD_GETCPUCLOCKID */

/* Define to 1 if you have the <pthread.h> header file. */
#define HAVE_PTHREAD_H 1

/* Define to 1 if you have the `pthread_init' function. */
#define HAVE_PTHREAD_INIT 1

/* Define to 1 if you have the `pthread_kill' function. [Python 3] */
#define HAVE_PTHREAD_KILL 1

/* Define to 1 if you have the `pthread_sigmask' function. */
#define HAVE_PTHREAD_SIGMASK 1

/* Define to 1 if you have the <pty.h> header file. */
/* #undef HAVE_PTY_H */

/* Define to 1 if you have the `putenv' function. */
#define HAVE_PUTENV 1

/* Define to 1 if you have the `pwrite' function. [Python 3] */
#define HAVE_PWRITE 1

/* Define to 1 if you have the `pwritev' function. [Python 3.7] */
#define HAVE_PWRITEV 1

/* Define to 1 if you have the `pwritev2' function. [Python 3.7] */
/* #undef HAVE_PWRITEV2 */

/* Define if the libcrypto has RAND_egd [Python 3] */
/* #undef HAVE_RAND_EGD */

/* Define to 1 if you have the `readlink' function. */
#define HAVE_READLINK 1

/* Define to 1 if you have the `readlinkat' function. [Python 3] */
#define HAVE_READLINKAT 1

/* Define to 1 if you have the `readv' function. [Python 3] */
#define HAVE_READV 1

/* Define to 1 if you have the `realpath' function. */
#define HAVE_REALPATH 1

/* Define to 1 if you have the `recvfrom' function. [Python 3.11] */
#define HAVE_RECVFROM 1

/* Define to 1 if you have the `renameat' function. [Python 3] */
#define HAVE_RENAMEAT 1

/* Define if readline supports append_history [Python 3] */
#define HAVE_RL_APPEND_HISTORY 1

/* Define if you have readline 2.1 */
#define HAVE_RL_CALLBACK 1

/* Define if you can turn off readline's signal handling. */
/* #undef HAVE_RL_CATCH_SIGNAL */

/* Define if you have readline 2.2 */
#define HAVE_RL_COMPLETION_APPEND_CHARACTER 1

/* Define if you have readline 4.0 */
#define HAVE_RL_COMPLETION_DISPLAY_MATCHES_HOOK 1

/* Define if you have readline 4.2 */
#define HAVE_RL_COMPLETION_MATCHES 1

/* Define if you have rl_completion_suppress_append */
/* #undef HAVE_RL_COMPLETION_SUPPRESS_APPEND */

/* Define if you have readline 4.0 */
#define HAVE_RL_PRE_INPUT_HOOK 1

/* Define if you have readline 4.0 */
/* #undef HAVE_RL_RESIZE_TERMINAL */

/* Define to 1 if you have the `round' function. */
#define HAVE_ROUND 1

/* Define to 1 if you have the `rtpSpawn' function. [Python 3.8] */
/* #undef HAVE_RTPSPAWN */

/* Define to 1 if you have the `sched_get_priority_max' function. [Python 3] */
#define HAVE_SCHED_GET_PRIORITY_MAX 1

/* Define to 1 if you have the <sched.h> header file. [Python 3] */
#define HAVE_SCHED_H 1

/* Define to 1 if you have the `sched_rr_get_interval' function. [Python 3] */
/* #undef HAVE_SCHED_RR_GET_INTERVAL */

/* Define to 1 if you have the `sched_setaffinity' function. [Python 3] */
/* #undef HAVE_SCHED_SETAFFINITY */

/* Define to 1 if you have the `sched_setparam' function. [Python 3] */
/* #undef HAVE_SCHED_SETPARAM */

/* Define to 1 if you have the `sched_setscheduler' function. [Python 3] */
/* #undef HAVE_SCHED_SETSCHEDULER */

/* Define to 1 if you have the `select' function. */
#define HAVE_SELECT 1

/* Define to 1 if you have the `sem_clockwait' function. [Python 3.9] */
/* #undef HAVE_SEM_CLOCKWAIT */

/* Define to 1 if you have the `sem_getvalue' function. */
#define HAVE_SEM_GETVALUE 1

/* Define to 1 if you have the `sem_open' function. */
#define HAVE_SEM_OPEN 1

/* Define to 1 if you have the `sem_timedwait' function. */
/* #undef HAVE_SEM_TIMEDWAIT */

/* Define to 1 if you have the `sem_unlink' function. */
#define HAVE_SEM_UNLINK 1

/* Define to 1 if you have the `sendfile' function. [Python 3] */
/* #undef HAVE_SENDFILE */

/* Define to 1 if you have the `sendto' function. [Python 3.11] */
#define HAVE_SENDTO 1

/* Define to 1 if you have the `setegid' function. */
#define HAVE_SETEGID 1

/* Define to 1 if you have the `seteuid' function. */
#define HAVE_SETEUID 1

/* Define to 1 if you have the `setgid' function. */
#define HAVE_SETGID 1

/* Define if you have the 'setgroups' function. */
#define HAVE_SETGROUPS 1

/* Define to 1 if you have the `sethostname' function. [Python 3] */
#define HAVE_SETHOSTNAME 1

/* Define to 1 if you have the `setitimer' function. */
#define HAVE_SETITIMER 1

/* Define to 1 if you have the `setlocale' function. */
#define HAVE_SETLOCALE 1

/* Define to 1 if you have the `setpgid' function. */
#define HAVE_SETPGID 1

/* Define to 1 if you have the `setpgrp' function. */
#define HAVE_SETPGRP 1

/* Define to 1 if you have the `setpriority' function. [Python 3] */
#define HAVE_SETPRIORITY 1

/* Define to 1 if you have the `setregid' function. */
#define HAVE_SETREGID 1

/* Define to 1 if you have the `setresgid' function. */
/* #undef HAVE_SETRESGID */

/* Define to 1 if you have the `setresuid' function. */
/* #undef HAVE_SETRESUID */

/* Define to 1 if you have the `setreuid' function. */
#define HAVE_SETREUID 1

/* Define to 1 if you have the `setsid' function. */
#define HAVE_SETSID 1

/* Define to 1 if you have the `setsockopt' function. */
#define HAVE_SETSOCKOPT 1

/* Define to 1 if you have the `setuid' function. */
#define HAVE_SETUID 1

/* Define to 1 if you have the `setvbuf' function. */
#define HAVE_SETVBUF 1

/* Define to 1 if you have the <shadow.h> header file. */
/* #undef HAVE_SHADOW_H */

/* Define to 1 if you have the `shm_open' function. [Python 3.8] */
#define HAVE_SHM_OPEN 1

/* Define to 1 if you have the `shm_unlink' function. [Python 3.8] */
#define HAVE_SHM_UNLINK 1

/* Define to 1 if you have the `shutdown' function. [Python 3.11] */
#define HAVE_SHUTDOWN 1

/* Define to 1 if you have the `sigaction' function. */
#define HAVE_SIGACTION 1

/* Define to 1 if you have the `sigaltstack' function. [Python 3] */
#define HAVE_SIGALTSTACK 1

/* Define to 1 if you have the `sigfillset' function. [Python 3.8] */
#define HAVE_SIGFILLSET 1

/* Define to 1 if `si_band' is a member of `siginfo_t'. [Python 3.7] */
/* #undef HAVE_SIGINFO_T_SI_BAND */

/* Define to 1 if you have the `siginterrupt' function. */
#define HAVE_SIGINTERRUPT 1

/* Define to 1 if you have the <signal.h> header file. */
#define HAVE_SIGNAL_H 1

/* Define to 1 if you have the `sigfillset' function. */
#define HAVE_SIGFILLSET 1

/* Define to 1 if you have the `sigpending' function. [Python 3] */
#define HAVE_SIGPENDING 1

/* Define to 1 if you have the `sigrelse' function. */
#define HAVE_SIGRELSE 1

/* Define to 1 if you have the `sigtimedwait' function. [Python 3] */
/* #undef HAVE_SIGTIMEDWAIT */

/* Define to 1 if you have the `sigwait' function. [Python 3] */
#define HAVE_SIGWAIT 1

/* Define to 1 if you have the `sigwaitinfo' function. [Python 3] */
/* #undef HAVE_SIGWAITINFO */

/* Define to 1 if you have the `snprintf' function. */
#define HAVE_SNPRINTF 1

/* struct sockaddr_alg (linux/if_alg.h) [Python 3.6] */
/* #undef HAVE_SOCKADDR_ALG */

/* Define if sockaddr has sa_len member */
#define HAVE_SOCKADDR_SA_LEN 1

/* struct sockaddr_storage (sys/socket.h) */
#define HAVE_SOCKADDR_STORAGE 1

/* Define if you have the 'socket' function. [Python 3.11] */
#define HAVE_SOCKET 1

/* Define if you have the 'socketpair' function. */
#define HAVE_SOCKETPAIR 1

/* Define to 1 if you have the <spawn.h> header file. */
#define HAVE_SPAWN_H 1

/* Define if your compiler provides ssize_t */
#define HAVE_SSIZE_T 1

/* Define to 1 if you have the `statvfs' function. */
#define HAVE_STATVFS 1

/* Define if you have struct stat.st_mtim.tv_nsec */
/* #undef HAVE_STAT_TV_NSEC */

/* Define if you have struct stat.st_mtimensec */
#define HAVE_STAT_TV_NSEC2 1

/* Define if your compiler supports variable length function prototypes (e.g.
   void fprintf(FILE *, char *, ...);) *and* <stdarg.h> */
#define HAVE_STDARG_PROTOTYPES 1

/* Define to 1 if you have the <stdint.h> header file. */
#define HAVE_STDINT_H 1

/* Define to 1 if you have the <stdlib.h> header file. */
#define HAVE_STDLIB_H 1

/* Has stdatomic.h, atomic_int and _Atomic void* types work [Python 3] */
/* #undef HAVE_STD_ATOMIC */

/* Define to 1 if you have the `strdup' function. */
#define HAVE_STRDUP 1

/* Define to 1 if you have the `strftime' function. */
#define HAVE_STRFTIME 1

/* Define to 1 if you have the <strings.h> header file. */
#define HAVE_STRINGS_H 1

/* Define to 1 if you have the <string.h> header file. */
#define HAVE_STRING_H 1

/* Define to 1 if you have the `strlcpy' function. [Python 3] */
#define HAVE_STRLCPY 1

/* Define to 1 if you have the <stropts.h> header file. */
/* #undef HAVE_STROPTS_H */

/* Define to 1 if you have the `strsignal' function. [Python 3.8] */
#define HAVE_STRSIGNAL 1

/* Define to 1 if `pw_gecos' is a member of `struct passwd'. [Python 3.6] */
#define HAVE_STRUCT_PASSWD_PW_GECOS 1

/* Define to 1 if `pw_passwd' is a member of `struct passwd'. [Python 3.6] */
#define HAVE_STRUCT_PASSWD_PW_PASSWD 1

/* Define to 1 if `st_birthtime' is a member of `struct stat'. */
#define HAVE_STRUCT_STAT_ST_BIRTHTIME 1

/* Define to 1 if `st_blksize' is a member of `struct stat'. */
#define HAVE_STRUCT_STAT_ST_BLKSIZE 1

/* Define to 1 if `st_blocks' is a member of `struct stat'. */
#define HAVE_STRUCT_STAT_ST_BLOCKS 1

/* Define to 1 if `st_flags' is a member of `struct stat'. */
#define HAVE_STRUCT_STAT_ST_FLAGS 1

/* Define to 1 if `st_gen' is a member of `struct stat'. */
#define HAVE_STRUCT_STAT_ST_GEN 1

/* Define to 1 if `st_rdev' is a member of `struct stat'. */
#define HAVE_STRUCT_STAT_ST_RDEV 1

/* Define to 1 if `tm_zone' is a member of `struct tm'. */
#define HAVE_STRUCT_TM_TM_ZONE 1

/* Define to 1 if your `struct stat' has `st_blocks'. Deprecated, use
   `HAVE_STRUCT_STAT_ST_BLOCKS' instead. */
#define HAVE_ST_BLOCKS 1

/* Define if you have the 'symlink' function. */
#define HAVE_SYMLINK 1

/* Define to 1 if you have the `symlinkat' function. [Python 3] */
#define HAVE_SYMLINKAT 1

/* Define to 1 if you have the `sync' function. [Python 3] */
#define HAVE_SYNC 1

/* Define to 1 if you have the `sysconf' function. */
#define HAVE_SYSCONF 1

/* Define to 1 if you have the `system' function. [Python 3.11] */
#define HAVE_SYSTEM 1

/* Define to 1 if you have the <sysexits.h> header file. */
#define HAVE_SYSEXITS_H 1

/* Define to 1 if you have the <sys/audioio.h> header file. */
/* #undef HAVE_SYS_AUDIOIO_H */

/* Define to 1 if you have the <sys/auxv.h> header file. [Python 3.9] */
/* #undef HAVE_SYS_AUXV_H */

/* Define to 1 if you have the <sys/bsdtty.h> header file. */
/* #undef HAVE_SYS_BSDTTY_H */

/* Define to 1 if you have the <sys/devpoll.h> header file. [Python 3] */
/* #undef HAVE_SYS_DEVPOLL_H */

/* Define to 1 if you have the <sys/dir.h> header file, and it defines `DIR'.
   */
/* #undef HAVE_SYS_DIR_H */

/* Define to 1 if you have the <sys/endian.h> header file. [Python 3] */
/* #undef HAVE_SYS_ENDIAN_H */

/* Define to 1 if you have the <sys/epoll.h> header file. */
/* #undef HAVE_SYS_EPOLL_H */

/* Define to 1 if you have the <sys/event.h> header file. */
#define HAVE_SYS_EVENT_H 1

/* Define to 1 if you have the <sys/file.h> header file. */
#define HAVE_SYS_FILE_H 1

/* Define to 1 if you have the <sys/ioctl.h> header file. [Python 3] */
#define HAVE_SYS_IOCTL_H 1

/* Define to 1 if you have the <sys/kern_control.h> header file. [Python 3] */
#define HAVE_SYS_KERN_CONTROL_H 1

/* Define to 1 if you have the <sys/loadavg.h> header file. */
/* #undef HAVE_SYS_LOADAVG_H */

/* Define to 1 if you have the <sys/lock.h> header file. */
#define HAVE_SYS_LOCK_H 1

/* Define to 1 if you have the <sys/memfd.h> header file. [Python 3.8] */
/* #undef HAVE_SYS_MEMFD_H */

/* Define to 1 if you have the <sys/mkdev.h> header file. */
/* #undef HAVE_SYS_MKDEV_H */

/* Define to 1 if you have the <sys/mman.h> header file. [Python 3.8] */
#define HAVE_SYS_MMAN_H 1

/* Define to 1 if you have the <sys/modem.h> header file. */
/* #undef HAVE_SYS_MODEM_H */

/* Define to 1 if you have the <sys/ndir.h> header file, and it defines `DIR'.
   */
/* #undef HAVE_SYS_NDIR_H */

/* Define to 1 if you have the <sys/param.h> header file. */
#define HAVE_SYS_PARAM_H 1

/* Define to 1 if you have the <sys/poll.h> header file. */
#define HAVE_SYS_POLL_H 1

/* Define to 1 if you have the <sys/random.h> header file. */
#define HAVE_SYS_RANDOM_H 1

/* Define to 1 if you have the <sys/resource.h> header file. */
#define HAVE_SYS_RESOURCE_H 1

/* Define to 1 if you have the <sys/select.h> header file. */
#define HAVE_SYS_SELECT_H 1

/* Define to 1 if you have the <sys/sendfile.h> header file. [Python 3] */
/* #undef HAVE_SYS_SENDFILE_H */

/* Define to 1 if you have the <sys/socket.h> header file. */
#define HAVE_SYS_SOCKET_H 1

/* Define to 1 if you have the <sys/statvfs.h> header file. */
#define HAVE_SYS_STATVFS_H 1

/* Define to 1 if you have the <sys/stat.h> header file. */
#define HAVE_SYS_STAT_H 1

/* Define to 1 if you have the <sys/syscall.h> header file. [Python 3] */
#define HAVE_SYS_SYSCALL_H 1

/* Define to 1 if you have the <sys/sys_domain.h> header file. [Python 3] */
#define HAVE_SYS_SYS_DOMAIN_H 1

/* Define to 1 if you have the <sys/sysmacros.h> header file. [Python 3.6] */
/* #undef HAVE_SYS_SYSMACROS_H */

/* Define to 1 if you have the <sys/termio.h> header file. */
/* #undef HAVE_SYS_TERMIO_H */

/* Define to 1 if you have the <sys/times.h> header file. */
#define HAVE_SYS_TIMES_H 1

/* Define to 1 if you have the <sys/time.h> header file. */
#define HAVE_SYS_TIME_H 1

/* Define to 1 if you have the <sys/types.h> header file. */
#define HAVE_SYS_TYPES_H 1

/* Define to 1 if you have the <sys/uio.h> header file. [Python 3] */
#define HAVE_SYS_UIO_H 1

/* Define to 1 if you have the <sys/un.h> header file. */
#define HAVE_SYS_UN_H 1

/* Define to 1 if you have the <sys/utsname.h> header file. */
#define HAVE_SYS_UTSNAME_H 1

/* Define to 1 if you have the <sys/wait.h> header file. */
#define HAVE_SYS_WAIT_H 1

/* Define to 1 if you have the <sys/xattr.h> header file. [Python 3] */
#define HAVE_SYS_XATTR_H 1

/* Define to 1 if you have the `tcgetpgrp' function. */
#define HAVE_TCGETPGRP 1

/* Define to 1 if you have the `tcsetpgrp' function. */
#define HAVE_TCSETPGRP 1

/* Define to 1 if you have the `tempnam' function. */
#define HAVE_TEMPNAM 1

/* Define to 1 if you have the <termios.h> header file. */
#define HAVE_TERMIOS_H 1

/* Define to 1 if you have the <term.h> header file. */
#define HAVE_TERM_H 1

/* Define to 1 if you have the `tgamma' function. */
#define HAVE_TGAMMA 1

/* Define to 1 if you have the <thread.h> header file. [Python 2.7] */
/* #undef HAVE_THREAD_H */

/* Define to 1 if you have the `timegm' function. */
#define HAVE_TIMEGM 1

/* Define to 1 if you have the `times' function. */
#define HAVE_TIMES 1

/* Define to 1 if you have the `tmpfile' function. */
#define HAVE_TMPFILE 1

/* Define to 1 if you have the `tmpnam' function. */
#define HAVE_TMPNAM 1

/* Define to 1 if you have the `tmpnam_r' function. */
/* #undef HAVE_TMPNAM_R */

/* Define to 1 if your `struct tm' has `tm_zone'. Deprecated, use
   `HAVE_STRUCT_TM_TM_ZONE' instead. */
#define HAVE_TM_ZONE 1

/* Define to 1 if you have the `truncate' function. */
#define HAVE_TRUNCATE 1

/* Define to 1 if you have the `ttyname' function. */
#define HAVE_TTYNAME 1

/* Define to 1 if you don't have `tm_zone' but do have the external array
   `tzname'. */
/* #undef HAVE_TZNAME */

/* Define this if you have tcl and TCL_UTF_MAX==6 */
/* #undef HAVE_UCS4_TCL */

/* Define if your compiler provides uint32_t. */
#define HAVE_UINT32_T 1

/* Define if your compiler provides uint64_t. */
#define HAVE_UINT64_T 1

/* Define to 1 if the system has the type `uintptr_t'. */
#define HAVE_UINTPTR_T 1

/* Define to 1 if you have the `umask' function. [Python 3.11] */
#define HAVE_UMASK 1

/* Define to 1 if you have the `uname' function. */
#define HAVE_UNAME 1

/* Define to 1 if you have the <unistd.h> header file. */
#define HAVE_UNISTD_H 1

/* Define to 1 if you have the `unlinkat' function. [Python 3] */
#define HAVE_UNLINKAT 1

/* Define to 1 if you have the `unsetenv' function. */
#define HAVE_UNSETENV 1

/* Define if you have a useable wchar_t type defined in wchar.h; useable means
   wchar_t must be an unsigned type with at least 16 bits. (see
   Include/unicodeobject.h). */
/* #undef HAVE_USABLE_WCHAR_T */

/* Define to 1 if you have the <util.h> header file. */
#define HAVE_UTIL_H 1

/* Define to 1 if you have the `utimensat' function. [Python 3] */
#define HAVE_UTIMENSAT 1

/* Define to 1 if you have the `utimes' function. */
#define HAVE_UTIMES 1

/* Define to 1 if you have the <utime.h> header file. */
#define HAVE_UTIME_H 1

/* Define if uuid_create() exists. [Python 3.7] */
/* #undef HAVE_UUID_CREATE */

/* Define if uuid_enc_be() exists. [Python 3.7] */
/* #undef HAVE_UUID_ENC_BE */

/* Define if uuid_generate_time_safe() exists. [Python 3.7] */
#define HAVE_UUID_GENERATE_TIME_SAFE 1

/* Define to 1 if you have the <uuid.h> header file. [Python 3.7] */
/* #undef HAVE_UUID_H */

/* Define to 1 if you have the <uuid/uuid.h> header file. [Python 3.7] */
#define HAVE_UUID_UUID_H 1

/* Define to 1 if you have the `wait' function. [Python 3.11] */
#define HAVE_WAIT 1

/* Define to 1 if you have the `wait3' function. */
#define HAVE_WAIT3 1

/* Define to 1 if you have the `wait4' function. */
#define HAVE_WAIT4 1

/* Define to 1 if you have the `waitid' function. [Python 3] */
#define HAVE_WAITID 1

/* Define to 1 if you have the `waitpid' function. */
#define HAVE_WAITPID 1

/* Define if the compiler provides a wchar.h header file. */
#define HAVE_WCHAR_H 1

/* Define to 1 if you have the `wcscoll' function. */
#define HAVE_WCSCOLL 1

/* Define to 1 if you have the `wcsftime' function. [Python 3] */
#define HAVE_WCSFTIME 1

/* Define to 1 if you have the `wcsxfrm' function. [Python 3] */
#define HAVE_WCSXFRM 1

/* Define to 1 if you have the `wmemcmp' function. [Python 3] */
#define HAVE_WMEMCMP 1

/* Define if tzset() actually switches the local timezone in a meaningful way.
   */
#define HAVE_WORKING_TZSET 1

/* Define to 1 if you have the `writev' function. [Python 3] */
#define HAVE_WRITEV 1

/* Define if libssl has X509_VERIFY_PARAM_set1_host and related function [Python 3.7] */
#define HAVE_X509_VERIFY_PARAM_SET1_HOST 1

/* Define if the zlib library has inflateCopy */
/* #undef HAVE_ZLIB_COPY */

/* Define to 1 if you have the `_getpty' function. */
/* #undef HAVE__GETPTY */

/* Define if you are using Mach cthreads directly under /include [Python 2.7] */
/* #undef HURD_C_THREADS */

/* Define if you are using Mach cthreads under mach / [Python 2.7] */
/* #undef MACH_C_THREADS */

/* Define if log1p(-0.) is 0. rather than -0. [Python 3] */
/* #undef LOG1P_DROPS_ZERO_SIGN */

/* Define to 1 if `major', `minor', and `makedev' are declared in <mkdev.h>.
   */
/* #undef MAJOR_IN_MKDEV */

/* Define to 1 if `major', `minor', and `makedev' are declared in
   <sysmacros.h>. */
/* #undef MAJOR_IN_SYSMACROS */

/* Define if mvwdelch in curses.h is an expression. */
#define MVWDELCH_IS_EXPRESSION 1

/* Define to the address where bug reports for this package should be sent. */
/* #undef PACKAGE_BUGREPORT */

/* Define to the full name of this package. */
/* #undef PACKAGE_NAME */

/* Define to the full name and version of this package. */
/* #undef PACKAGE_STRING */

/* Define to the one symbol short name of this package. */
/* #undef PACKAGE_TARNAME */

/* Define to the home page for this package. */
/* #undef PACKAGE_URL */

/* Define to the version of this package. */
/* #undef PACKAGE_VERSION */

/* Define if POSIX semaphores aren't enabled on your system */
/* #undef POSIX_SEMAPHORES_NOT_ENABLED */

/* Define if pthread_key_t is compatible with int. [Python 3.7] */
/* #undef PTHREAD_KEY_T_IS_COMPATIBLE_WITH_INT */

/* Defined if PTHREAD_SCOPE_SYSTEM supported. */
#define PTHREAD_SYSTEM_SCHED_SUPPORTED 1

/* Define as the preferred size in bits of long digits */
/* #undef PYLONG_BITS_IN_DIGIT */

/* Define to printf format modifier for long long type */
#define PY_FORMAT_LONG_LONG "ll"

/* Define if you want to coerce the C locale to a UTF-8 based locale */
#define PY_COERCE_C_LOCALE 1

/* Define to printf format modifier for Py_ssize_t */
#define PY_FORMAT_SIZE_T "z"

/* Default cipher suites list for ssl module. 1: Python's preferred selection,
   2: leave OpenSSL defaults untouched, 0: custom string [Python 3.7] */
#define PY_SSL_DEFAULT_CIPHERS 1

/* Cipher suite string for PY_SSL_DEFAULT_CIPHERS=0 [Python 3.7] */
/* #undef PY_SSL_DEFAULT_CIPHER_STRING */

/* Define as the integral type used for Unicode representation. [Python 2.7] */
/* #undef PY_UNICODE_TYPE */

/* Define if you want to build an interpreter with many run-time checks. */
/* #undef Py_DEBUG */

/* Defined if Python is built as a shared library. */
/* #undef Py_ENABLE_SHARED */

/* Define if you want to disable the GIL */
/* #undef Py_GIL_DISABLED */

/* Define as the size of the unicode type. [Python 2.7] */
/* #undef Py_UNICODE_SIZE */

/* Define if you want to have a Unicode type. [Python 2.7] */
/* #undef Py_USING_UNICODE */

/* assume C89 semantics that RETSIGTYPE is always void */
#define RETSIGTYPE void

/* Define hash algorithm for str, bytes and memoryview. SipHash24: 1, FNV: 2,
   externally defined: 0 [Python 3] */
/* #undef Py_HASH_ALGORITHM */

/* Define if you want to enable tracing references for debugging purpose [Python 3.8] */
/* #undef Py_TRACE_REFS */

/* Define if setpgrp() must be called as setpgrp(0, 0). */
/* #undef SETPGRP_HAVE_ARG */

/* Define this to be extension of shared libraries (including the dot!).[Python 2.7]  */
#define SHLIB_EXT ".so"

/* Define to 1 if you must link with -lrt for shm_open(). [Python 3.8] */
/* #undef SHM_NEEDS_LIBRT */

/* Define if i>>j for signed int i does not extend the sign bit when i < 0 */
/* #undef SIGNED_RIGHT_SHIFT_ZERO_FILLS */

/* The size of `double', as computed by sizeof. */
#define SIZEOF_DOUBLE 8

/* The size of `float', as computed by sizeof. */
#define SIZEOF_FLOAT 4

/* The size of `fpos_t', as computed by sizeof. */
#define SIZEOF_FPOS_T 8

/* The size of `int', as computed by sizeof. */
#define SIZEOF_INT 4

/* The size of `long', as computed by sizeof. */
#define SIZEOF_LONG 8
#define ALIGNOF_LONG 8

/* The size of `long', as computed by alignof. */
#define ALIGNOF_LONG 8

/* The size of `long double', as computed by sizeof. */
/* #undef SIZEOF_LONG_DOUBLE */

/* The size of `long long', as computed by sizeof. */
#define SIZEOF_LONG_LONG 8

/* The size of `off_t', as computed by sizeof. */
#define SIZEOF_OFF_T 8

/* The size of `pid_t', as computed by sizeof. */
#define SIZEOF_PID_T 4

/* The size of `pthread_key_t', as computed by sizeof. [Python 3.7] */
#define SIZEOF_PTHREAD_KEY_T 8

/* The size of `pthread_t', as computed by sizeof. */
#define SIZEOF_PTHREAD_T 8

/* The size of `short', as computed by sizeof. */
#define SIZEOF_SHORT 2

/* The size of `size_t', as computed by sizeof. */
#define SIZEOF_SIZE_T 8
#define ALIGNOF_SIZE_T 8

/* The size of `size_t', as computed by alignof. */
#define ALIGNOF_SIZE_T 8

/* The size of `time_t', as computed by sizeof. */
#define SIZEOF_TIME_T 8

/* The size of `uintptr_t', as computed by sizeof. */
#define SIZEOF_UINTPTR_T 8

/* The size of `void *', as computed by sizeof. */
#define SIZEOF_VOID_P 8

/* The size of `wchar_t', as computed by sizeof. */
#define SIZEOF_WCHAR_T 4

/* The size of `_Bool', as computed by sizeof. */
#define SIZEOF__BOOL 1

/* Define to 1 if you have the ANSI C header files. */
#define STDC_HEADERS 1

/* Define if you can safely include both <sys/select.h> and <sys/time.h>
   (which you can't on SCO ODT 3.0). */
#define SYS_SELECT_WITH_SYS_TIME 1

/* Define if tanh(-0.) is -0., or if platform doesn't have signed zeros */
#define TANH_PRESERVES_ZERO_SIGN 1

/* Library needed by timemodule.c: librt may be needed for clock_gettime() */
/* #undef TIMEMODULE_LIB */

/* Define to 1 if you can safely include both <sys/time.h> and <time.h>. */
#define TIME_WITH_SYS_TIME 1

/* Define to 1 if your <sys/time.h> declares `struct tm'. */
/* #undef TM_IN_SYS_TIME */

/* Define if you want to use computed gotos in ceval.c. */
/* #undef USE_COMPUTED_GOTOS */

/* Define to use the C99 inline keyword. [Python 3] */
#define USE_INLINE 1

/* Enable extensions on AIX 3, Interix.  */
#ifndef _ALL_SOURCE
#define _ALL_SOURCE 1
#endif
/* Enable GNU extensions on systems that have them.  */
#ifndef _GNU_SOURCE
#define _GNU_SOURCE 1
#endif
/* Enable threading extensions on Solaris.  */
#ifndef _POSIX_PTHREAD_SEMANTICS
#define _POSIX_PTHREAD_SEMANTICS 1
#endif
/* Enable extensions on HP NonStop.  */
#ifndef _TANDEM_SOURCE
#define _TANDEM_SOURCE 1
#endif
/* Enable general extensions on Solaris.  */
#ifndef __EXTENSIONS__
#define __EXTENSIONS__ 1
#endif


/* Define if you want to use MacPython modules on MacOSX in unix-Python. [Python 2.7] */
/* #undef USE_TOOLBOX_OBJECT_GLUE */

/* Define if a va_list is an array of some kind */
#define VA_LIST_IS_ARRAY 1

/* Define if you want SIGFPE handled (see Include/pyfpe.h). */
/* #undef WANT_SIGFPE_HANDLER */

/* Define if you want wctype.h functions to be used instead of the one
   supplied by Python itself. (see Include/unicodectype.h). [Python 2.7] */
/* #undef WANT_WCTYPE_FUNCTIONS */

/* Define if WINDOW in curses.h offers a field _flags. */
#define WINDOW_HAS_FLAGS 1

/* Define if you want build the _decimal module using a coroutine-local rather
   than a thread-local context [Python 3.8] */
#define WITH_DECIMAL_CONTEXTVAR 1

/* Define if you want documentation strings in extension modules */
#define WITH_DOC_STRINGS 1

/* Define if you want to compile in DTrace support [Python 3.6] */
/* #undef WITH_DTRACE */

/* Define if you want to use the new-style (Openstep, Rhapsody, MacOS) dynamic
   linker (dyld) instead of the old-style (NextStep) dynamic linker (rld).
   Dyld is necessary to support frameworks. */
#define WITH_DYLD 1

/* Define if you want to compile in object freelists optimization */
#define WITH_FREELISTS 1

/* Define to 1 if libintl is needed for locale functions. */
/* #undef WITH_LIBINTL */

/* Define if you want to produce an OpenStep/Rhapsody framework (shared
   library plus accessory files). */
/* #undef WITH_NEXT_FRAMEWORK */

/* Define if you want to compile in Python-specific mallocs */
#define WITH_PYMALLOC 1

/* Define if you want to compile in rudimentary thread support */
/* #undef WITH_THREAD */

/* Define to profile with the Pentium timestamp counter */
/* #undef WITH_TSC */

/* Define if you want pymalloc to be disabled when running under valgrind */
/* #undef WITH_VALGRIND */

/* Define WORDS_BIGENDIAN to 1 if your processor stores words with the most
   significant byte first (like Motorola and SPARC, unlike Intel). */
#if defined AC_APPLE_UNIVERSAL_BUILD
# if defined __BIG_ENDIAN__
#  define WORDS_BIGENDIAN 1
# endif
#else
# ifndef WORDS_BIGENDIAN
/* #undef WORDS_BIGENDIAN */
#  if WORDS_BIGENDIAN == 0
#   undef WORDS_BIGENDIAN
#  endif
# endif
#endif

/* Define if arithmetic is subject to x87-style double rounding issue */
/* #undef X87_DOUBLE_ROUNDING */

/* Define on OpenBSD to activate all library features */
/* #undef _BSD_SOURCE */

/* Define on Irix to enable u_int */
#define _BSD_TYPES 1

/* Define on Darwin to activate all library features */
#define _DARWIN_C_SOURCE 1

/* This must be set to 64 on some systems to enable large file support. */
#define _FILE_OFFSET_BITS 64

/* Define on Linux to activate all library features */
#define _GNU_SOURCE 1

/* Define to include mbstate_t for mbrtowc */
/* #undef _INCLUDE__STDC_A1_SOURCE */

/* This must be defined on some systems to enable large file support. */
#ifndef _LARGEFILE_SOURCE
#define _LARGEFILE_SOURCE 1
#endif

/* This must be defined on AIX systems to enable large file support. */
/* #undef _LARGE_FILES */

/* Define to 1 if on MINIX. */
/* #undef _MINIX */

/* Define on NetBSD to activate all library features */
#define _NETBSD_SOURCE 1

/* Define _OSF_SOURCE to get the makedev macro. [Python 2.7] */
/* #undef _OSF_SOURCE */

/* Define to 2 if the system does not provide POSIX.1 features except with
   this defined. */
/* #undef _POSIX_1_SOURCE */

/* Define to activate features from IEEE Stds [Python 2.7: IEEE Stds 1003.1-2001] or [Python 3.x: IEEE Stds 1003.1-2008]*/
#define _POSIX_C_SOURCE 200809L

/* Define to 1 if you need to in order for `stat' and other things to work. */
#define _POSIX_SOURCE

/* Define if you have POSIX threads, and your system does not define that. */
#define _POSIX_THREADS

/* framework name [Python 3.7] */
#define _PYTHONFRAMEWORK ""

/* Define to force use of thread-safe errno, h_errno, and other functions */
/* #undef _REENTRANT */

/* Define for Solaris 2.5.1 so the uint32_t typedef from <sys/synch.h>,
   <pthread.h>, or <semaphore.h> is not used. If the typedef were allowed, the
   #define below would cause a syntax error. */
/* #undef _UINT32_T */

/* Define for Solaris 2.5.1 so the uint64_t typedef from <sys/synch.h>,
   <pthread.h>, or <semaphore.h> is not used. If the typedef were allowed, the
   #define below would cause a syntax error. */
/* #undef _UINT64_T */

/* Define to the level of X/Open that your system supports */
#define _XOPEN_SOURCE 700

/* Define to activate Unix95-and-earlier features */
#define _XOPEN_SOURCE_EXTENDED 1

/* Define on FreeBSD to activate all library features */
#define __BSD_VISIBLE 1

/* Define to 1 if type `char' is unsigned and you are not using gcc.  */
#ifndef __CHAR_UNSIGNED__
/* #undef __CHAR_UNSIGNED__ */
#endif

/* Define to 'long' if <time.h> doesn't define. */
/* #undef clock_t */

/* Define to empty if `const' does not conform to ANSI C. */
/* #undef const */

/* Define to `int' if <sys/types.h> doesn't define. */
/* #undef gid_t */

/* Define to `__inline__' or `__inline' if that's what the C compiler
   calls it, or to nothing if 'inline' is not supported under any name.  */
#ifndef __cplusplus
/* #undef inline */
#endif

/* Define to the type of a signed integer type of width exactly 32 bits if
   such a type exists and the standard includes do not define it. */
/* #undef int32_t */

/* Define to the type of a signed integer type of width exactly 64 bits if
   such a type exists and the standard includes do not define it. */
/* #undef int64_t */

/* Define to `int' if <sys/types.h> does not define. */
/* #undef mode_t */

/* Define to `long int' if <sys/types.h> does not define. */
/* #undef off_t */

/* Define to `int' if <sys/types.h> does not define. */
/* #undef pid_t */

/* Define to empty if the keyword does not work. */
/* #undef signed */

/* Define to `unsigned int' if <sys/types.h> does not define. */
/* #undef size_t */

/* Define to `int' if <sys/socket.h> does not define. */
/* #undef socklen_t */

/* Define to `int' if <sys/types.h> doesn't define. */
/* #undef uid_t */

/* Define to the type of an unsigned integer type of width exactly 32 bits if
   such a type exists and the standard includes do not define it. */
/* #undef uint32_t */

/* Define to the type of an unsigned integer type of width exactly 64 bits if
   such a type exists and the standard includes do not define it. */
/* #undef uint64_t */

/* Define to empty if the keyword does not work. */
/* #undef volatile */


/* Define the macros needed if on a UnixWare 7.x system. */
#if defined(__USLC__) && defined(__SCO_VERSION__)
#define STRICT_SYSV_CURSES /* Don't use ncurses extensions */
#endif

#define PLATLIBDIR "lib"

#endif /*Py_PYCONFIG_H*/

