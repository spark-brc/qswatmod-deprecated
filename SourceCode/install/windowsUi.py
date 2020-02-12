# -*- coding: utf-8 -*-
# ===============================================================================
#
# WET acknowledge the following for developing the installation routine:
#
# Copyright (c) 2015 IST-SUPSI (www.supsi.ch/ist)
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
# Note from WET:
# As of now the proxy is not enabled but kept in the code for reference.
#
# ===============================================================================
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

import os

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'windows.ui'))


class Windows_dialog(QDialog, FORM_CLASS):

    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.proxy = None

        self.manage_gui()

    def manage_gui(self):
        """
            Gui init
        """
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.read_proxy)

        self.checkProxy.stateChanged.connect(self.enable_proxy_frame)
        self.checkUser.stateChanged.connect(self.enable_user_frame)

    def enable_proxy_frame(self, state):
        """
            Enable proxy frame
        """
        if state == Qt.Checked:
            self.proxyFrame.setEnabled(True)
        else:
            self.proxyFrame.setEnabled(False)

    def enable_user_frame(self, state):
        """
            Enable user frame
        """

        if state == Qt.Checked:
            self.userFrame.setEnabled(True)
        else:
            self.userFrame.setEnabled(False)

    def read_proxy(self):
        """
            If necessary compose proxy string
        """
        if self.checkProxy.checkState() == Qt.Unchecked:
            self.close()
            return

        server_proxy = self.proxyServer.text()
        server_port = self.proxyPort.text()

        if self.checkUser.checkState() == Qt.Checked:
            user = self.proxyUser.text()
            pwd = self.proxyPass.text()

            self.proxy = "{}:{}@{}:{}".format(user, pwd, server_proxy, server_port)
        else:
            self.proxy = "{}:{}".format(server_proxy, server_port)

        self.close()

    def get_proxy(self):
        return self.proxy
