# -*- Mode: Cython -*-

import os

from libc.stdlib cimport malloc, free

cimport _zlib as zlib


class ZlibError(Exception):
    "A problem with zlib"

    def __init__(self, errno, msg=None):
        if msg:
            super().__init__('{} ({})'.format(errno, msg))
        else:
            super().__init__(errno)


# cdef unsigned char* _dict = NULL
cdef bytes _dict = None
cdef int _dict_len = -1


cdef load_dictionary():
    global _dict
    global _dict_len
    here = os.path.dirname(os.path.realpath(__file__))
    data = open(os.path.join(here, '_dictionary.bin'), 'rb').read()
    _dict = data
    _dict_len = len(data)


def compress_gen(block, int level=zlib.Z_BEST_SPEED, int size=16384):
    cdef zlib.z_stream zstr
    cdef unsigned char *buff
    cdef int flush = zlib.Z_FINISH
    cdef int r

    if not _dict:
        load_dictionary()

    zstr.zalloc = NULL
    zstr.zfree = NULL
    zstr.opaque = NULL

    r = zlib.deflateInit2(&zstr, level, zlib.Z_DEFLATED, 13, 7, zlib.Z_DEFAULT_STRATEGY)
    if r != zlib.Z_OK:
        raise ZlibError(r)

    buff = <unsigned char *>malloc(size)
    if not buff:
        raise MemoryError

    r = zlib.deflateSetDictionary(&zstr, _dict, _dict_len)
    if r != zlib.Z_OK:
       raise ZlibError(r)

    zstr.next_in = block
    zstr.avail_in = len(block)
    zstr.next_out = &buff[0]
    zstr.avail_out = size

    try:
        zstr.next_in = <unsigned char *> block
        zstr.avail_in = len(block)
        while zstr.avail_in or flush == zlib.Z_FINISH:
            zstr.next_out = <unsigned char *>(&buff[0])
            zstr.avail_out = size
            r = zlib.deflate(&zstr, flush)
            if r == zlib.Z_STREAM_END:
                yield buff[:size - zstr.avail_out]
                return
            elif r != zlib.Z_OK:
                raise ZlibError(r, zstr.msg)
            elif size - zstr.avail_out > 0:
                yield buff[:size - zstr.avail_out]
            else:
                # Z_OK, but no data
                pass
    except Exception as e:
        print(e)
    finally:
        zlib.deflateEnd(&zstr)
        free(buff)


def uncompress_gen(bytes block, int size=16384):
    cdef zlib.z_stream zstr
    cdef char *buff
    cdef int flush = zlib.Z_NO_FLUSH
    cdef int r

    if not _dict:
        load_dictionary()

    zstr.zalloc = NULL
    zstr.zfree = NULL
    zstr.opaque = NULL
    zstr.avail_in = 0
    zstr.next_in = NULL

    r = zlib.inflateInit(&zstr)
    if r != zlib.Z_OK:
        raise ZlibError(r)
    
    buff = <char *>malloc(size)
    if not buff:
        raise MemoryError
    try:
        zstr.next_in = <unsigned char *> block
        zstr.avail_in = len(block)
        while zstr.avail_in or flush == zlib.Z_FINISH:
            zstr.next_out = <unsigned char *>(&buff[0])
            zstr.avail_out = size
            r = zlib.inflate(&zstr, flush)
            if r == zlib.Z_NEED_DICT:
                r = zlib.inflateSetDictionary(&zstr, _dict, _dict_len)
                if r != zlib.Z_OK:
                    raise ZlibError(r)
            elif r == zlib.Z_STREAM_END:
                yield buff[:size - zstr.avail_out]
            elif r != zlib.Z_OK:
                raise ZlibError(r, zstr.msg.decode('utf-8'))
            elif size - zstr.avail_out > 0:
                yield buff[:size - zstr.avail_out]
            else:
                # Z_OK, but no data
                pass
    finally:
        zlib.inflateEnd(&zstr)
        free(buff)


def compress(data):
    return b''.join(compress_gen(data))


def uncompress(data):
    return b''.join(uncompress_gen(data))


def compress_str(s):
    return compress(s.encode('utf8'))


def uncompress_str(data):
    return uncompress(data).decode('utf8')

