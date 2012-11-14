_VERSION = (4, 0, 0, 'final', 0)
_AUTHOR = "Nicolas Rebagliati"
_AUTHOR_EMAIL = "nicolas.rebagliati@aenima-x.com.ar"

def get_version(version=None):
    """Derives a PEP386-compliant version number from VERSION."""
    if version is None:
        version = _VERSION
    assert len(version) == 5
    assert version[3] in ('alpha', 'beta', 'rc', 'final')

    # Now build the two parts of the version number:
    # main = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #     | {a|b|c}N - for alpha, beta and rc releases

    parts = 2 if version[2] == 0 else 3
    main = '.'.join(str(x) for x in version[:parts])

    sub = ''
    if version[3] == 'alpha' and version[4] == 0:
        # At the toplevel, this would cause an import loop.
        from django.utils.version import get_svn_revision
        svn_revision = get_svn_revision()[4:]
        if svn_revision != 'unknown':
            sub = '.dev%s' % svn_revision

    elif version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[version[3]] + str(version[4])

    return main + sub

def get_author():
    return _AUTHOR

def get_author_email():
    return _AUTHOR_EMAIL
