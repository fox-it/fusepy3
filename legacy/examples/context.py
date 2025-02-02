#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

import logging
from errno import ENOENT
from stat import S_IFDIR, S_IFREG
from time import time

from fuse import FUSE3, FuseOSError, LoggingMixIn, Operations, fuse_get_context


class Context(LoggingMixIn, Operations):
    "Example filesystem to demonstrate fuse_get_context()"

    def getattr(self, path, fh=None):
        uid, gid, pid = fuse_get_context()
        if path == "/":
            st = dict(st_mode=(S_IFDIR | 0o755), st_nlink=2)
        elif path == "/uid":
            size = len("%s\n" % uid)
            st = dict(st_mode=(S_IFREG | 0o444), st_size=size)
        elif path == "/gid":
            size = len("%s\n" % gid)
            st = dict(st_mode=(S_IFREG | 0o444), st_size=size)
        elif path == "/pid":
            size = len("%s\n" % pid)
            st = dict(st_mode=(S_IFREG | 0o444), st_size=size)
        else:
            raise FuseOSError(ENOENT)
        st["st_ctime"] = st["st_mtime"] = st["st_atime"] = time()
        return st

    def read(self, path, size, offset, fh):
        uid, gid, pid = fuse_get_context()

        def encoded(x):
            return ("%s\n" % x).encode("utf-8")

        if path == "/uid":
            return encoded(uid)
        elif path == "/gid":
            return encoded(gid)
        elif path == "/pid":
            return encoded(pid)

        raise RuntimeError("unexpected path: %r" % path)

    def readdir(self, path, fh):
        return [".", "..", "uid", "gid", "pid"]

    # Disable unused operations:
    access = None
    flush = None
    getxattr = None
    listxattr = None
    open = None
    opendir = None
    release = None
    releasedir = None
    statfs = None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("mount")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE3(Context(), args.mount, foreground=True, ro=True, allow_other=True)
