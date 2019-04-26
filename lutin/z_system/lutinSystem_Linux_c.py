#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##

from realog import debug
from lutin import system
from lutin import tools
from lutin import env
import os

class System(system.System):
	def __init__(self, target):
		system.System.__init__(self)
		# create some HELP:
		self.set_help("C: Generic C library")
		self.set_valid(True)
		if env.get_isolate_system() == False:
			# We must have it ... all time
			self.add_flag("c-remove", "-nostdinc")
			pass
		else:
			# grep "This file is part of the GNU C Library" /usr/include/*
			self.add_header_file([
			    '/usr/include/aio.h*',
			    '/usr/include/aliases.h*',
			    '/usr/include/alloca.h*',
			    '/usr/include/ansidecl.h*',
			    '/usr/include/argp.h*',
			    '/usr/include/argz.h*',
			    '/usr/include/ar.h*',
			    '/usr/include/assert.h*',
			    '/usr/include/byteswap.h*',
			    '/usr/include/complex.h*',
			    '/usr/include/cpio.h*',
			    '/usr/include/ctype.h*',
			    '/usr/include/dirent.h*',
			    '/usr/include/dlfcn.h*',
			    '/usr/include/elf.h*',
			    '/usr/include/endian.h*',
			    '/usr/include/envz.h*',
			    '/usr/include/err.h*',
			    '/usr/include/errno.h*',
			    '/usr/include/error.h*',
			    '/usr/include/execinfo.h*',
			    '/usr/include/fcntl.h*',
			    '/usr/include/features.h*',
			    '/usr/include/fenv.h*',
			    '/usr/include/fmtmsg.h*',
			    '/usr/include/fnmatch.h*',
			    '/usr/include/fpu_control.h*',
			    '/usr/include/fts.h*',
			    '/usr/include/ftw.h*',
			    '/usr/include/gconv.h*',
			    '/usr/include/getopt.h*',
			    '/usr/include/glob.h*',
			    '/usr/include/gnu-versions.h*',
			    '/usr/include/grp.h*',
			    '/usr/include/gshadow.h*',
			    '/usr/include/iconv.h*',
			    '/usr/include/ieee754.h*',
			    '/usr/include/ifaddrs.h*',
			    '/usr/include/inttypes.h*',
			    '/usr/include/langinfo.h*',
			    '/usr/include/libgen.h*',
			    '/usr/include/libintl.h*',
			    '/usr/include/libio.h*',
			    '/usr/include/limits.h*',
			    '/usr/include/link.h*',
			    '/usr/include/locale.h*',
			    '/usr/include/malloc.h*',
			    '/usr/include/mcheck.h*',
			    '/usr/include/memory.h*',
			    '/usr/include/mntent.h*',
			    '/usr/include/monetary.h*',
			    '/usr/include/mqueue.h*',
			    '/usr/include/netdb.h*',
			    '/usr/include/nl_types.h*',
			    '/usr/include/nss.h*',
			    '/usr/include/obstack.h*',
			    '/usr/include/printf.h*',
			    '/usr/include/pthread.h*',
			    '/usr/include/pty.h*',
			    '/usr/include/pwd.h*',
			    '/usr/include/re_comp.h*',
			    '/usr/include/regex.h*',
			    '/usr/include/regexp.h*',
			    '/usr/include/sched.h*',
			    '/usr/include/search.h*',
			    '/usr/include/semaphore.h*',
			    '/usr/include/setjmp.h*',
			    '/usr/include/sgtty.h*',
			    '/usr/include/shadow.h*',
			    '/usr/include/signal.h*',
			    '/usr/include/spawn.h*',
			    '/usr/include/stdc-predef.h*',
			    '/usr/include/stdint.h*',
			    '/usr/include/stdio_ext.h*',
			    '/usr/include/stdio.h*',
			    '/usr/include/stdlib.h*',
			    '/usr/include/string.h*',
			    '/usr/include/strings.h*',
			    '/usr/include/stropts.h*',
			    '/usr/include/tar.h*',
			    '/usr/include/termios.h*',
			    '/usr/include/tgmath.h*',
			    '/usr/include/thread_db.h*',
			    '/usr/include/time.h*',
			    '/usr/include/uchar.h*',
			    '/usr/include/ucontext.h*',
			    '/usr/include/ulimit.h*',
			    '/usr/include/unistd.h*',
			    '/usr/include/utime.h*',
			    '/usr/include/utmp.h*',
			    '/usr/include/utmpx.h*',
			    '/usr/include/values.h*',
			    '/usr/include/wchar.h*',
			    '/usr/include/wctype.h*',
			    '/usr/include/wordexp.h*',
			    '/usr/include/xlocale.h*',
			    ],
			    destination_path="")
			self.add_header_file([
			    '/usr/include/poll.h*',
			    '/usr/include/unistdio.h*',
			    '/usr/include/syslog.h*',
			    '/usr/include/_G_config.h*',
			    ],
			    destination_path="")
			self.add_header_file([
			    "/usr/include/sys/*",
			    ],
			    destination_path="sys",
			    recursive=True)
			self.add_header_file([
			    "/usr/include/bits/*",
			    ],
			    destination_path="bits",
			    recursive=True)
			self.add_header_file([
			    "/usr/include/gnu/*",
			    ],
			    destination_path="gnu",
			    recursive=True)
			self.add_header_file([
			    "/usr/include/linux/*",
			    ],
			    destination_path="",
			    recursive=True)
			self.add_header_file([
			    "/usr/include/asm/*",
			    ],
			    destination_path="asm",
			    recursive=True)
			self.add_header_file([
			    "/usr/include/asm-generic/*",
			    ],
			    destination_path="asm-generic",
			    recursive=True)
			self.add_header_file([
			    "/usr/include/netinet/*",
			    ],
			    destination_path="netinet",
			    recursive=True)
			self.add_header_file([
			    "/usr/include/net/*",
			    ],
			    destination_path="net",
			    recursive=True)
			# remove dependency of libc to lib std c++ when compile with g++
			#self.add_header_file([
			#    "stdarg.h",
			#    ],
			#    destination_path="",
			#    recursive=True)
			self.add_flag("link", "-B/usr/lib")

