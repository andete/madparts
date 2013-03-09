def _reset_sys_path():
    # Clear generic sys.path[0]
    import sys, os
    resources = os.environ['RESOURCEPATH']
    while sys.path[0] == resources:
        del sys.path[0]
_reset_sys_path()


def _update_path():
    import os, sys
    resources = os.environ['RESOURCEPATH']
    sys.path.append(os.path.join(
        resources, 'lib', 'python%d.%d'%(sys.version_info[:2]), 'lib-dynload'))
    sys.path.append(os.path.join(
        resources, 'lib', 'python%d.%d'%(sys.version_info[:2])))

_update_path()


def _site_packages():
    import site, sys, os
    paths = []
    prefixes = [sys.prefix]
    if sys.exec_prefix != sys.prefix:
        prefixes.append(sys.exec_prefix)
    for prefix in prefixes:
        paths.append(os.path.join(prefix, 'lib', 'python' + sys.version[:3],
            'site-packages'))
    if os.path.join('.framework', '') in os.path.join(sys.prefix, ''):
        home = os.environ.get('HOME')
        if home:
            paths.append(os.path.join(home, 'Library', 'Python',
                sys.version[:3], 'site-packages'))

    # Work around for a misfeature in setuptools: easy_install.pth places
    # site-packages way to early on sys.path and that breaks py2app bundles.
    # NOTE: this is hacks into an undocumented feature of setuptools and
    # might stop to work without warning.
    sys.__egginsert = len(sys.path)

    for path in paths:
        site.addsitedir(path)
_site_packages()


""" Add Apple's additional packages to sys.path """
def add_system_python_extras():
    import site, sys

    ver = '%s.%s'%(sys.version_info[:2])

    site.addsitedir('/System/Library/Frameworks/Python.framework/Versions/%s/Extras/lib/python'%(ver,))

add_system_python_extras()


def _chdir_resource():
    import os
    os.chdir(os.environ['RESOURCEPATH'])
_chdir_resource()


def _path_inject(paths):
    import sys
    sys.path[:0] = paths


_path_inject(['/Users/joost/madparts', '/Users/joost/madparts/build/bdist.macosx-10.8-intel/lib.macosx-10.8-intel-2.7', '/Users/joost/madparts/build/bdist.macosx-10.8-intel/lib'])


def _run():
    global __file__
    import os, sys, site
    sys.frozen = 'macosx_app'

    argv0 = os.path.basename(os.environ['ARGVZERO'])
    script = SCRIPT_MAP.get(argv0, DEFAULT_SCRIPT)

    sys.argv[0] = __file__ = script
    with open(script, 'rU') as fp:
        source = fp.read() + "\n"

    exec(compile(source, script, 'exec'), globals(), globals())



DEFAULT_SCRIPT='/Users/joost/madparts/madparts'
SCRIPT_MAP={}
try:
    _run()
except KeyboardInterrupt:
    pass
