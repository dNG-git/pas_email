# -*- coding: utf-8 -*-
##j## BOF

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;email

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
setup.py
"""

def get_version():
#
	"""
Returns the version currently in development.

:return: (str) Version string
:since:  v0.1.02
	"""

	return "v0.1.03"
#

from dNG.distutils.command.build_py import BuildPy
from dNG.distutils.command.install_data import InstallData
from dNG.distutils.temporary_directory import TemporaryDirectory

from distutils.core import setup
from os import path

with TemporaryDirectory(dir = ".") as build_directory:
#
	parameters = { "install_data_plain_copy_extensions": "json",
	               "pasEMailVersion": get_version()
	             }

	InstallData.add_install_data_callback(InstallData.plain_copy, [ "lang" ])
	InstallData.set_build_target_path(build_directory)
	InstallData.set_build_target_parameters(parameters)

	_build_path = path.join(build_directory, "src")

	setup(name = "pas_email",
	      version = get_version(),
	      description = "Python Application Services",
	      long_description = """"pas_email" provides a simple to use SMTP client based on "rfc_email.py".""",
	      author = "direct Netware Group et al.",
	      author_email = "web@direct-netware.de",
	      license = "MPL2",
	      url = "https://www.direct-netware.de/redirect?pas;email",

	      platforms = [ "any" ],

	      package_dir = { "": _build_path },
	      packages = [ "dNG" ],

	      data_files = [ ( "docs", [ "LICENSE", "README" ]) ],

	      # Override build_py to first run builder.py over all PAS modules
	      cmdclass = { "build_py": BuildPy,
	                   "install_data": InstallData
	                 }
	)
#

##j## EOF