# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QSWATMOD
                                 A QGIS plugin
 This plugin helps link SWAT and MODFLOW model.
                             -------------------
        begin                : 2017-08-23
        copyright            : (C) 2017 by Seonggyu and Dr. Anders
        email                : envpsg@colostate.edu
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load QSWATMOD class from file QSWATMOD.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .QSWATMOD import QSWATMOD
    return QSWATMOD(iface)
