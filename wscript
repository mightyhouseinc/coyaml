#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import Options, Scripting

APPNAME='coyaml'
VERSION='0.1.8'

top = '.'
out = 'build'

def set_options(opt):
    import distutils.sysconfig
    opt.tool_options('compiler_cc')
    opt.add_option('--build-shared', action="store_true", dest="build_shared",
        help="Build shared library instead of static")
    opt.add_option('--build-tests', action="store_true", dest="build_tests",
        help="Build test cases")
    opt.add_option('--python-lib', type="string", dest="python_lib",
        help="Path to python site-packages directory",
        default=distutils.sysconfig.get_python_lib())


def configure(conf):
    import coyaml.waf
    conf.check_tool('compiler_cc')
#    conf.check_tool('coyaml')
    conf.env.BUILD_TESTS = Options.options.build_tests
    conf.env.BUILD_SHARED = Options.options.build_shared

def build(bld):
    bld(
        features     = ['cc', ('cshlib'
            if bld.env.BUILD_SHARED else 'cstaticlib')],
        source       = [
            'src/parser.c',
            'src/commandline.c',
            ],
        target       = 'coyaml',
        includes     = ['include', 'src', bld.bdir + '/default'],
        defines      = [],
        ccflags      = ['-std=c99'],
        lib          = ['yaml'],
        )
    if bld.env.BUILD_SHARED:
        bld.install_files('${PREFIX}/lib', [bld.bdir+'/default/libcoyaml.so'])
    else:
        bld.install_files('${PREFIX}/lib', [bld.bdir+'/default/libcoyaml.a'])
    bld.install_files('${PREFIX}/include', [
        'include/coyaml_hdr.h',
        'include/coyaml_src.h',
        ])
    bld.install_files(Options.options.python_lib+'/coyaml', 'coyaml/*.py')
    bld.install_files('${PREFIX}/bin', 'scripts/coyaml', chmod=0o755)
    if bld.env.BUILD_TESTS:
        import coyaml.waf
        bld(
            features     = ['cc', 'cprogram', 'coyaml'],
            source       = [
                'test/tinytest.c',
                ],
            target       = 'tinytest',
            includes     = ['include', 'test'],
            ccflags      = ['-std=c99'],
            libpath      = [bld.bdir+'/default'],
            lib          = ['coyaml', 'yaml'],
            config       = 'test/tinyconfig.yaml',
            )
        bld(
            features     = ['cc', 'cprogram', 'coyaml'],
            source       = [
                'test/compr.c',
                ],
            target       = 'compr',
            includes     = ['include', 'test'],
            ccflags      = ['-std=c99'],
            libpath      = [bld.bdir+'/default'],
            lib          = ['coyaml', 'yaml'],
            config       = 'test/comprehensive.yaml',
            config_name  = 'cfg',
            )
        bld(
            features     = ['cc', 'cprogram', 'coyaml'],
            source       = [
                'test/recursive.c',
                ],
            target       = 'recursive',
            includes     = ['include', 'test'],
            ccflags      = ['-std=c99'],
            libpath      = [bld.bdir+'/default'],
            lib          = ['coyaml', 'yaml'],
            config       = 'test/recconfig.yaml',
            config_name  = 'cfg',
            )

def test(ctx):
    Scripting.commands += ['build']
    Options.options.build_tests = True
