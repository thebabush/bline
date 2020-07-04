#!/usr/bin/env python3

from distutils.core import setup, Extension
import os
import shlex
import subprocess

from Cython.Distutils import build_ext


"""
I swear to God, I fucking hate python some fucking times.
"""


def run_cmd(cmd, custom_env=None):
    env = dict(os.environ)
    if custom_env:
        env.update(custom_env)
    return subprocess.run(shlex.split(cmd), cwd='./zlib', env=env, check=True)


def make_zlib():
    #os.remove('./zlib/libz.a')
    if not os.path.isfile('./zlib/libz.a'):
        env = dict(os.environ)
        env['CFLAGS'] = '-fPIC -DNO_GZIP'
        # env['CFLAGS'] = '-fPIC -DNO_GZIP -DZLIB_DEBUG=1 -Dverbose=1'
        run_cmd('./configure --static', env)
        run_cmd('make')


class CustomBuildExt(build_ext):
    def run(self):
        make_zlib()
        super().run()


ext_modules = [
    Extension(
        'bline.zstream',
        ['bline/zstream.pyx'],
        depends=['bline/_zlib.pxd'],
        extra_objects=['zlib/libz.a'],
        include_dirs=['./zlib/'],
    )
]

setup(
    name='bline',
    setup_requires=['cython'],
    version='0.1',
    cmdclass={'build_ext': CustomBuildExt},
    ext_modules=ext_modules,
    scripts=[
        'scripts/bline',
    ],
    packages=['bline'],
    package_dir={
        'bline': 'bline',
    },
    package_data={
        'bline': ['_dictionary.bin'],
    },
)
