# === Variables set by makesetup ===

MODOBJS=
MODLIBS=

# === Variables set by configure
VERSION=    3.12
srcdir=     /Users/runner/work/portable-python/portable-python/build/Python-3.12.11


CC=		/Applications/Xcode_15.2.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc  -pthread
CXX=		  -pthread
MAINCC=		$(CC)
LINKCC=		$(PURIFY) $(MAINCC)
AR=		/Applications/Xcode_15.2.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/ar
RANLIB=		/Applications/Xcode_15.2.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/ranlib
SOABI=		cpython-312-darwin
LDVERSION=	$(VERSION)$(ABIFLAGS)
SVNVERSION=	svnversion $(srcdir)
HGVERSION=
HGTAG=
HGBRANCH=

GNULD=          yes

# Shell used by make (some versions default to the login shell, which is bad)
SHELL=      /bin/sh

# Use this to make a link between python$(VERSION) and python in $(BINDIR)
LN=         ln

# Portable install script (configure doesn't always guess right)
INSTALL=    /usr/bin/install -c
INSTALL_PROGRAM=${INSTALL}
INSTALL_SCRIPT= ${INSTALL}
INSTALL_DATA=	${INSTALL} -m 644
# Shared libraries must be installed with executable mode on some systems;
# rather than figuring out exactly which, we always give them executable mode.
# Also, making them read-only seems to be a good idea...
INSTALL_SHARED= ${INSTALL} -m 555

MAKESETUP=      $(srcdir)/Modules/makesetup

# Compiler options
OPT=            -I/Users/runner/work/portable-python/portable-python/deps/include -Wall -g -DNDEBUG
BASECFLAGS=	 -Wno-unused-result -Wsign-compare -Wunreachable-code
CFLAGS=         -I/Users/runner/work/portable-python/portable-python/deps/include -Wall -g
# Both CPPFLAGS and LDFLAGS need to contain the shell's value for setup.py to
# be able to build extension modules using the directories specified in the
# environment variables
CPPFLAGS=       
LDFLAGS=
LDLAST=
SGI_ABI=
CCSHARED=       -fPIC
LINKFORSHARED=  -Xlinker -export-dynamic
ARFLAGS=        rc
# Extra C flags added for building the interpreter object files.
CFLAGSFORSHARED=
# C flags used for building the interpreter object files
PY_CFLAGS=      -I/Users/runner/work/portable-python/portable-python/deps/include -Wall -g -DPy_BUILD_CORE


# Machine-dependent subdirectories
MACHDEP=        darwin

# Install prefix for architecture-independent files
prefix=         /Users/runner/work/portable-python/portable-python/build/python-install-3.12.11

# Install prefix for architecture-dependent files
exec_prefix=    ${prefix}

# Install prefix for data files
datarootdir=    ${prefix}/share

# Expanded directories
BINDIR=		${exec_prefix}/bin
LIBDIR=		${exec_prefix}/lib
MANDIR=		${datarootdir}/man
INCLUDEDIR=	${prefix}/include
CONFINCLUDEDIR=	$(exec_prefix)/include
SCRIPTDIR=	$(prefix)/lib
ABIFLAGS=	

# Detailed destination directories
BINLIBDEST=	$(LIBDIR)/python$(VERSION)
LIBDEST=	$(SCRIPTDIR)/python$(VERSION)
INCLUDEPY=	$(INCLUDEDIR)/python$(LDVERSION)
CONFINCLUDEPY=	$(CONFINCLUDEDIR)/python$(LDVERSION)
LIBP=		$(LIBDIR)/python$(VERSION)

# Symbols used for using shared libraries
SHLIB_SUFFIX=	.so
EXT_SUFFIX=	.$(SOABI).so
SO=		.so
LDSHARED=	$(CC) -dynamiclib -headerpad_max_install_names -undefined dynamic_lookup $(LDFLAGS)
BLDSHARED=	$(CC) -dynamiclib -headerpad_max_install_names -undefined dynamic_lookup $(LDFLAGS)
LDCXXSHARED=	$(CXX) -dynamiclib -headerpad_max_install_names -undefined dynamic_lookup
DESTSHARED=	$(BINLIBDEST)/lib-dynload

# Executable suffix (.exe on Windows and Mac OS X)
EXE=            
BUILDEXE=       

# Short name and location for Mac OS X Python framework
UNIVERSALSDK=
PYTHONFRAMEWORK=
PYTHONFRAMEWORKDIR=    no-framework
PYTHONFRAMEWORKPREFIX=
PYTHONFRAMEWORKINSTALLDIR=
# Deployment target selected during configure, to be checked
# by distutils. The export statement is needed to ensure that the
# deployment target is active during build.
MACOSX_DEPLOYMENT_TARGET=10.9
#export MACOSX_DEPLOYMENT_TARGET

# Environment to run shared python without installed libraries
RUNSHARED=

# Modes for directories, executables and data files created by the
# install process.  Default to user-only-writable for all file types.
DIRMODE=    755
EXEMODE=    755
FILEMODE=    644

# configure script arguments
CONFIG_ARGS=	 '--prefix' '/Users/runner/work/portable-python/portable-python/build/python-install-3.12.11'

# Subdirectories with code
SRCDIRS= 	Parser Grammar Objects Python Modules Mac

# Other subdirectories
SUBDIRSTOO=	Include Lib Misc Demo

# Files and directories to be distributed
CONFIGFILES=	configure configure.in acconfig.h pyconfig.h.in Makefile.pre.in
DISTFILES=	README ChangeLog $(CONFIGFILES)
DISTDIRS=	$(SUBDIRS) $(SUBDIRSTOO) Ext-dummy
DIST=		$(DISTFILES) $(DISTDIRS)

LIBRARY=	libpython$(VERSION)$(ABIFLAGS).a
LDLIBRARY=      libpython$(VERSION)$(ABIFLAGS).a
BLDLIBRARY=     $(LDLIBRARY)
DLLLIBRARY=
LDLIBRARYDIR=
INSTSONAME=	$(LDLIBRARY)


LIBS=		-lpthread -ldl  -lutil
LIBM=		-lm
LIBC=
SYSLIBS=	$(LIBM) $(LIBC)
SHLIBS=		$(LIBS)

PYTHON=		python$(EXE)
BUILDPYTHON=	python$(BUILDEXE)

PYTHON_FOR_BUILD=./$(BUILDPYTHON) -E
_PYTHON_HOST_PLATFORM=
BUILD_GNU_TYPE=	x86_64-unknown-linux-gnu
HOST_GNU_TYPE=	x86_64-unknown-linux-gnu

# === Definitions added by makesetup ===

LOCALMODLIBS=
BASEMODLIBS=
GLHACK=-Dclear=__GLclear
PYTHONPATH=$(COREPYTHONPATH)
COREPYTHONPATH=$(DESTPATH)$(SITEPATH)$(TESTPATH)$(MACHDEPPATH)$(EXTRAMACHDEPPATH)$(TKPATH)$(OLDPATH)
OLDPATH=:lib-old
TKPATH=:lib-tk
EXTRAMACHDEPPATH=
MACHDEPPATH=:plat-$(MACHDEP)
TESTPATH=
SITEPATH=
DESTPATH=
MACHDESTLIB=$(BINLIBDEST)
DESTLIB=$(LIBDEST)


LIBFFI_INCLUDEDIR=


#########################################################################
# Rules

# This rule is here for OPENSTEP/Rhapsody/MacOSX. It builds a temporary
# minimal framework (not including the Lib directory and such) in the current
# directory.
RESSRCDIR=Mac/Resources/framework

# Install the library
PLATDIR=	plat-$(MACHDEP)
EXTRAPLATDIR=
EXTRAMACHDEPPATH=

# Install the library and miscellaneous stuff needed for extending/embedding
# This goes into $(exec_prefix)
LIBPL=		$(LIBP)/config

# pkgconfig directory
LIBPC=		$(LIBDIR)/pkgconfig

