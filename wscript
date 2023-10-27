#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from waflib.Build import BuildContext
from waflib import Utils, Options
import os.path
import subprocess

APPNAME='coyaml'
if os.path.exists('.git'):
    VERSION=subprocess.getoutput('git describe').lstrip('v').replace('-', '_')
else:
    VERSION='0.3.14'

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
    conf.env.BUILD_SHARED = Options.options.build_shared


def build_only(bld):
    bld(
        features=['c', ('cshlib' if bld.env.BUILD_SHARED else 'cstlib')],
        source=[
            'src/parser.c',
            'src/commandline.c',
            'src/helpers.c',
            'src/vars.c',
            'src/types.c',
            'src/emitter.c',
            'src/copy.c',
            'src/eval.c',
        ],
        target='coyaml',
        includes=['include', 'src'],
        defines=[f'COYAML_VERSION="{VERSION}"'],
        cflags=['-std=c99', '-Wall'],
        lib=['yaml'],
    )


def build(bld):
    build_only(bld)
    if bld.env.BUILD_SHARED:
        bld.install_files('${PREFIX}/lib', 'libcoyaml.so')
    else:
        bld.install_files('${PREFIX}/lib', 'libcoyaml.a')
    bld.install_files('${PREFIX}/include', [
        'include/coyaml_hdr.h',
        'include/coyaml_src.h',
        ])
    bld(features='py',
        source=bld.path.ant_glob('coyaml/*.py'),
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
        cflags       = ['-std=c99', '-Wall'],
        lib          = ['coyaml', 'yaml'],
        )
    bld(
        features     = ['c', 'cprogram', 'coyaml'],
        source       = [
            'test/vartest.c',
            'test/vars.yaml',
            ],
        target       = 'vartest',
        includes     = ['include', 'test'],
        libpath      = ['.'],
        cflags       = ['-std=c99', '-Wall'],
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
        cflags       = ['-std=c99', '-Wall'],
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
        cflags       = ['-std=c99', '-Wall'],
        lib          = ['coyaml', 'yaml'],
        config_name  = 'cfg',
        )
    bld.add_group()
    diff = 'diff -u ${SRC[0].abspath()} ${SRC[1]}'
    bld(rule='./${SRC[0]} -c ${SRC[1].abspath()} -v -C -P > ${TGT[0]}',
        source=['tinytest', 'examples/tinyexample.yaml'],
        target='tinyexample.out',
        always=True)
    bld(rule=diff,
        source=['examples/tinyexample.out', 'tinyexample.out'],
        always=True)

    bld(rule='./${SRC[0]} -c ${SRC[1].abspath()} -C -P > ${TGT[0]}',
        source=['vartest', 'examples/varexample.yaml'],
        target='varexample.out',
        always=True)
    bld(rule=diff,
        source=['examples/varexample.out', 'varexample.out'],
        always=True)

    bld(rule='./${SRC[0]} -c ${SRC[1].abspath()} --config-var clivar=CLI -C -P > ${TGT[0]}',
        source=['compr', 'examples/compexample.yaml'],
        target='compexample.out.ws',
        always=True)
    bld(rule="sed -r 's/\s+$//g' ${SRC[0]} > ${TGT[0]}",
        source='compexample.out.ws',
        target='compexample.out',
        always=True)
    bld(rule=diff,
        source=['examples/compexample.out', 'compexample.out'],
        always=True)

    bld(rule='COMPR_LOGLEVEL=7 ./${SRC[0]} -c ${SRC[1].abspath()} --config-var clivar=CLI -C -PP > ${TGT[0]}',
        source=['compr', 'examples/compexample.yaml'],
        target='compexample.out.ws1',
        always=True)
    bld(rule="sed -r 's/\s+$//g' ${SRC[0]} > ${TGT[0]}",
        source='compexample.out.ws1',
        target='compexample.out1',
        always=True)
    bld(rule=diff,
        source=['examples/compexample_comments.out', 'compexample.out1'],
        always=True)

    bld(rule='./${SRC[0]} -c ${SRC[1].abspath()} -C -P > ${TGT[0]}',
        source=['recursive', 'examples/recexample.yaml'],
        target='recexample.out',
        always=True)
    bld(rule=diff,
        source=['examples/recexample.out', 'recexample.out'],
        always=True)
    bld(rule='COMPR_CFG=${SRC[1].abspath()} ./${SRC[0]} -Dclivar=CLI > ${TGT[0]}',
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

def dist(ctx):
    ctx.excl = ['.waf*', '*.tar.bz2', '*.zip', 'build',
        '.git*', '.lock*', '**/*.pyc']
    ctx.algo = 'tar.bz2'

def make_pkgbuild(task):
    import hashlib
    task.outputs[0].write(Utils.subst_vars(task.inputs[0].read(), {
        'VERSION': VERSION,
        'DIST_MD5': hashlib.md5(task.inputs[1].read('rb')).hexdigest(),
        }))

class makepkg(BuildContext):
    cmd = 'archpkg'
    fun = 'archpkg'
    variant = 'archpkg'

def archpkg(bld):
    distfile = f'{APPNAME}-{VERSION}.tar.bz2'
    bld(rule=make_pkgbuild,
        source=['PKGBUILD.tpl', distfile, 'wscript'],
        target='PKGBUILD')
    bld(rule='cp ${SRC} ${TGT}', source=distfile, target='.')
    bld.add_group()
    bld(rule='makepkg -f', source=distfile)
    bld.add_group()
    bld(rule='makepkg -f --source', source=distfile)

def bumpver(ctx):
    ctx.exec_command(r"sed -ri.bak 's/(X-Version[^0-9]*)[0-9.]+/\1"+VERSION+"/'"
        " examples/compr.out examples/compexample.out")
