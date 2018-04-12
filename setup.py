#!/usr/bin/env python
""" X-SAPR Clutter

X-SAPR clutter package uses a directory of radar netCDF files and determines
which gates are clutter or not. Clutter values are set to 1 and non-clutter
to 0. Clutter field is added to a empty field radar object and the radar
object can then be written.

"""


import glob

from numpy.distutils.core import setup
from numpy.distutils.misc_util import Configuration


DOCLINES = __doc__.split("\n")

NAME = 'xsapr_clutter'
MAINTAINER = 'Scott Collis, Zach Sherman and Cory Weber'
DESCRIPTION = DOCLINES[0]
# INSTALL_REQUIRES = ['pyart', 'wradlib']
LONG_DESCRIPTION = "\n".join(DOCLINES[2:])
LICENSE = 'BSD'
PLATFORMS = "Linux"
MAJOR = 0
MINOR = 1
MICRO = 0
SCRIPTS = glob.glob('scripts/*')
TEST_SUITE = 'nose.collector'
TESTS_REQUIRE = ['nose']
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

def configuration(parent_package='', top_path=None):
    """ Configuration of xsapr clutter package. """
    config = Configuration(None, parent_package, top_path)
    config.set_options(ignore_setup_xxx_py=True,
                       assume_default_configuration=True,
                       delegate_options_to_subpackages=True,
                       quiet=True)

    config.add_subpackage('xsapr_clutter')
    return config


def setup_package():
    """ Setup of xsapr clutter package. """
    setup(
        name=NAME,
        maintainer=MAINTAINER,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        version=VERSION,
        license=LICENSE,
        platforms=PLATFORMS,
        configuration=configuration,
        include_package_data=True,
        # install_requires=INSTALL_REQUIRES,
        test_suite=TEST_SUITE,
        tests_require=TESTS_REQUIRE,
        scripts=SCRIPTS,
    )

if __name__ == '__main__':
    setup_package()
