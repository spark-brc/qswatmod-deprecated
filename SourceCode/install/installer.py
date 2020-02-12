# -*- coding: utf-8 -*-
# ===============================================================================
#
# QSWATMOD acknowledge the following for developing the installation routine: 
#
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Note from QSWATMOD:
# the original FREEWAT code was modified to install only pip, and numpy
# to allow the QSWATMOD install.
#
# ===============================================================================

import version
import sys
import os
import imp
from PyQt4.QtGui import QMessageBox
if 'linux' in sys.platform:
    QMessageBox.warning(None, "you are using Linux", "Please install dependencies manually before QSWATMOD can be used")
elif 'darwin' in sys.platform:
    QMessageBox.warning(None, "you are using Linux", "Please install dependencies manually before QSWATMOD can be used")
else:
    import installerWindows as inst

package = {
    # 'pip': False,
    'numpy': False,
    'pandas': False,
    'flopy': False,
    'cv2': False,
    'shapefile': False,
    # 'matplotlib': False
    }
def check_install():
    if os.path.isfile(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'install.txt')):
        print("Installation done!!!")
    else:
        try:
            import numpy
            ver = numpy.__version__
            if ver >= version.numpy:
                package['numpy'] = True
            else:
                print("installed: {} required: {}".format(ver, version.numpy))
                # inst.install_numpy()
                # inst.install_numpy() # not good idea
        except ImportError:
            pass
        try:
            import pandas
            ver = pandas.__version__
            if ver >= version.pandas:
                package['pandas'] = True
            else:
                print("installed: {} required: {}".format(ver, version.pandas))
        except ImportError:
            pass
        try:
            import flopy
            ver = flopy.__version__

            if ver >= version.flopy:
                package['flopy'] = True
            else:
                print("installed: {} required: {}".format(ver, version.flopy))
        except ImportError:
            pass
        try:
            import cv2
            ver = cv2.__version__

            if ver >= version.cv2:
                package['cv2'] = True
            else:
                print("installed: {} required: {}".format(ver, version.cv2))
        except ImportError:
            pass
        try:
            import shapefile
            ver = shapefile.__version__

            if ver >= version.shapefile:
                package['shapefile'] = True
            else:
                print("installed: {} required: {}".format(ver, version.shapefile))

        except ImportError:
            pass

        packs = [k for k, v in package.items() if v is False]
        inst.install_missing_dep(packs)
