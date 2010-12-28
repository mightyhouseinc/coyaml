#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from waflib.Build import BuildContext
from waflib import Options
import glob

APPNAME='coyaml'
VERSION='0.3.2'

top = '.'
out = 'build'

def options(opt):
    import distutils.sysconfig
    opt.load('compiler_c python')
    opt.add_option('--build-shared', action="store_true", dest="build_shared",
        help="Build shared library instead of static")

def configure(conf):
    conf.load('compiler_c python')
    conf.check_python_version((3,0,0))
    conf.env.CFLAGS = ['-O3']
    
    conf.setenv('test')
    conf.env.CFLAGS = ['-g']

def build(bld):
    bld(
        features     = ['c', ('cshlib'
            if bld.env.BUILD_SHARED else 'cstlib')],
        source       = [
            'src/parser.c',
            'src/commandline.c',
            'src/helpers.c',
            'src/vars.c',
            'src/types.c',
            'src/emitter.c',
            'src/copy.c',
            ],
        target       = 'coyaml',
        includes     = ['include', 'src'],
        defines      = ['COYAML_VERSION="%s"' % VERSION],
        cflags       = ['-std=c99'],
        lib          = ['yaml'],
        )
    if bld.env.BUILD_SHARED:
        bld.install_files('${PREFIX}/lib', ['libcoyaml.so'])
    else:
        bld.install_files('${PREFIX}/lib', ['libcoyaml.a'])
    bld.install_files('${PREFIX}/include', [
        'include/coyaml_hdr.h',
        'include/coyaml_src.h',
        ])
    bld(features='py',
        source=glob.glob('coyaml/*.py'),
        install_path='${PYTHONDIR}/coyaml')
    bld.install_files('${PREFIX}/bin', 'scripts/coyaml', chmod=0o755)
    
def build_tests(bld):
    import coyaml.waf
    build(bld)
    bld.add_group()
    bld(
        features     = ['c', 'cprogram', 'coyaml'],
        source       = [
            'test/tinytest.c',
            'test/tinyconfig.yaml',
            ],
        target       = 'tinytest',
        includes     = ['include', 'test'],
        libpath      = ['.'],
        cflags       = ['-std=c99'],
        lib          = ['coyaml', 'yaml'],
        )
    bld(
        features     = ['c', 'cprogram', 'coyaml'],
        source       = [
            'test/compr.c',
            'test/comprehensive.yaml',
            ],
        target       = 'compr',
        includes     = ['include', 'test'],
        libpath      = ['.'],
        cflags       = ['-std=c99'],
        lib          = ['coyaml', 'yaml'],
        config_name  = 'cfg',
        )
    bld(
        features     = ['c', 'cprogram', 'coyaml'],
        source       = [
            'test/recursive.c',
            'test/recconfig.yaml',
            ],
        target       = 'recursive',
        includes     = ['include', 'test'],
        libpath      = ['.'],
        cflags       = ['-std=c99'],
        lib          = ['coyaml', 'yaml'],
        config_name  = 'cfg',
        )
    bld.add_group()
    diff = 'diff -u ${SRC[0].abspath()} ${SRC[1]}'
    bld(rule='./${SRC[0]} -c ${SRC[1].abspath()} -C -P > ${TGT}',
        source=['tinytest', 'examples/tinyexample.yaml'],
        target='tinyexample.out',
        always=True)
    bld(rule=diff,
        source=['examples/tinyexample.out', 'tinyexample.out'],
        always=True)
    bld(rule='./${SRC[0]} -c ${SRC[1].abspath()} --config-var clivar=CLI -C -P > ${TGT}',
        source=['compr', 'examples/compexample.yaml'],
        target='compexample.out',
        always=True)
    bld(rule=diff,
        source=['examples/compexample.out', 'compexample.out'],
        always=True)
    bld(rule='./${SRC[0]} -c ${SRC[1].abspath()} -C -P > ${TGT}',
        source=['recursive', 'examples/recexample.yaml'],
        target='recexample.out',
        always=True)
    bld(rule=diff,
        source=['examples/recexample.out', 'recexample.out'],
        always=True)
    bld(rule='./${SRC[0]} -c ${SRC[1].abspath()} -Dclivar=CLI > ${TGT}',
        source=['compr', 'examples/compexample.yaml'],
        target='compr.out',
        always=True)
    bld(rule=diff,
        source=['examples/compr.out', 'compr.out'],
        always=True)
            
class test(BuildContext):
    cmd = 'test'
    fun = 'build_tests'
    variant = 'test'
