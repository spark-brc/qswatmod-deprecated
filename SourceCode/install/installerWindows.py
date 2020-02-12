import sys, os, types
import windowsUi

import version
import platform
from PyQt4.QtGui import QApplication, QMessageBox
import sys

command = None
proxy = None


def run_as_admin(cmd_line=None, wait=True):
    try:
        if os.name != 'nt':
            raise RuntimeError, "This function is only implemented on Windows."

        import win32con, win32event, win32process
        from win32com.shell.shell import ShellExecuteEx
        from win32com.shell import shellcon

        python_exe = sys.executable

        if cmd_line is None:
            cmd_line = [python_exe] + sys.argv
        elif type(cmd_line) not in (types.TupleType, types.ListType):
            raise ValueError, "cmdLine is not a sequence."
        cmd = '%s' % (cmd_line[0],)
        # TODO: isn't there a function or something we can call to massage command line params?
        params = " ".join(['%s' % (x,) for x in cmd_line[1:]])
        # cmdDir = ''
        show_cmd = win32con.SW_SHOWNORMAL
        # showCmd = win32con.SW_HIDE
        lp_verb = 'runas'  # causes UAC elevation prompt.

        # print "Running", cmd, params

        # ShellExecute() doesn't seem to allow us to fetch the PID or handle
        # of the process, so we can't get anything useful from it. Therefore
        # the more complex ShellExecuteEx() must be used.

        # procHandle = win32api.ShellExecute(0, lpVerb, cmd, params, cmdDir, showCmd)

        print "cmd: ", cmd
        print "Params: ", params

        proc_info = ShellExecuteEx(
                                nShow=show_cmd,
                                fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                                lpVerb=lp_verb,
                                lpFile=cmd,
                                lpParameters=params)

        if wait:
            proc_handle = proc_info['hProcess']
            win32event.WaitForSingleObject(proc_handle, win32event.INFINITE)
            rc = win32process.GetExitCodeProcess(proc_handle)
            # print "Process handle %s returned code %s" % (proc_handle, rc)
            return rc
        else:
            return -1
    except Exception as _:
        return -1


def open_ui():
    """
        Open UI to inform the user
    """

    # app = QApplication(sys.argv)  # only dev
    pass_ui = windowsUi.Windows_dialog()
    pass_ui.show()

    if pass_ui.exec_():

        global proxy
        if pass_ui.get_proxy():
            proxy = '--proxy="{}"'.format(pass_ui.get_proxy())
        else:
            proxy = ""

    del pass_ui
    global command

    osgeo_root = os.popen('echo %OSGEO4W_ROOT%').read().replace('\n', '')
    command = os.path.join(osgeo_root, 'OSGeo4W.bat')


def install_pip():
    """
        Install pip from local get-pip.py
    """
    if not command:
        open_ui()

    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'get_pip', 'get-pip.py')

    params = 'python {}'.format(path)
    rc = run_as_admin([command, params], wait=True)
    if rc != 0:
        QMessageBox.warning(None, "Problem during installation", "Problem installing pip")
        return False
    return True

def uninstall_numpy():
    """
        uninstall numpy in python
    """
    
    if not command:
        open_ui()
    params = 'python -m pip uninstall numpy'
    rc = run_as_admin([command, params], wait=True)
    if rc != 0:
        QMessageBox.warning(None, "Problem during uninstallation", "Problem uninstalling numpy")
        return False
    return True


def install_numpy():
    """
        install numpy using whl file inside numpy directory
    """
    import platform

    os_ver = platform.architecture()[0]
    #compiled wheels can be found here: https://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy
    if os_ver == '64bit':
        numpy_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'deps',
                                  'numpy-1.16.4+mkl-cp27-cp27m-win_amd64.whl')
    else:
        numpy_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'deps',
                                  'numpy-1.14.5+mkl-cp27-cp27m-win32.whl')

    if not command:
        open_ui()
    params = 'python -m pip install {} {}'.format(numpy_path, proxy)
    # params = 'python -m pip install numpy --upgrade'
    #  params = 'python -m pip uninstall numpy'
    rc = run_as_admin([command, params], wait=True)


def install_pandas():
    """
        install numpy using whl file inside numpy directory
    """
    # os_ver = platform.architecture()[0]
    #compiled wheels can be found here: https://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy
    # if os_ver == '64bit':
    #     pandas_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'deps',
    #                               'pandas-0.20.1-cp27-cp27m-win_amd64.whl')
    # else:
    #     pandas_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'deps',
    #                               'pandas-0.20.1-cp27-cp27m-win_amd64.whl')

    if not command:
        open_ui()
        
    # params = 'python -m pip install {} {}'.format(pandas_path, proxy)
    params = 'python -m pip install pandas'
    # params = 'python -m pip uninstall numpy'
    
    rc = run_as_admin([command, params], wait=True)

    if rc != 0:
        QMessageBox.warning(None, "Problem during installation", "Problem installing pandas")

        return False
    return True

'''
def install_netcdf4():
    """
        install numpy using whl file inside numpy directory
    """
    import platform
    if not command:
        open_ui()

    #params = 'python -m pip install {} {}'.format(numpy_path, proxy)
    #params = 'python -m pip install numpy --upgrade'
    params = 'python -m pip install netCDF4'
    
    rc = run_as_admin([command, params], wait=True)

    if rc != 0:
        QMessageBox.warning(None, "Problem during installation", "Problem installing netCDF4")
        return False
    return True    
'''    


def install_enum():
    """
        Install flopy without dependencies
    """
    # os_ver = platform.architecture()[0]
    # #compiled wheels can be found here: https://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy
    # if os_ver == '64bit':
    #     enum_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'deps',
    #                               'enum34-1.1.6-py2-none-any.whl')
    # else:
    #     enum_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'deps',
    #                               'enum34-1.1.6-py2-none-any.whl')
    if not command:
        open_ui()
    # params = 'python -m pip install {} {}'.format(enum_path, proxy)
    params = 'python -m pip install enum34'
    rc = run_as_admin([command, params], wait=True)

    if rc != 0:
        QMessageBox.warning(None, "Problem during installation", "Problem installing enum")
        return False
    return True

def install_flopy():
    """
        Install flopy without dependencies
    """
    if not command:  # not support by python 2.7 now
        open_ui()
    # params = 'python -m pip install {} {}'.format(flopy_path, proxy)
    params ='python -m pip install flopy==3.2.9'
    rc = run_as_admin([command, params], wait=True)

    if rc != 0:
        QMessageBox.warning(None, "Problem during installation", "Problem installing flopy")
        return False
    return True


    # import platform

    # os_ver = platform.architecture()[0]
    # if os_ver == '64bit':
    #     flopy_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'deps',
    #                               'flopy-3.2.9.zip')
    # else:
    #     flopy_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'deps',
    #                               'flopy-3.2.9.zip')

    # if not command:
    #     open_ui()
    # params = 'python -m pip install {} {}'.format(flopy_path, proxy)
    # rc = run_as_admin([command, params], wait=True)


def install_pyshp():
    """
        Install flopy without dependencies
    """
    # os_ver = platform.architecture()[0]
    # #compiled wheels can be found here: https://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy
    # if os_ver == '64bit':
    #     pyshp_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'deps',
    #                               'pyshp-1.2.12-py2.py3-none-any.whl')
    # else:
    #     flopy_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'deps',
    #                               'pyshp-1.2.12-py2.py3-none-any.whl')

    if not command:
        open_ui()

    # params = 'python -m pip install {} {}'.format(pyshp_path, proxy)
    params = 'python -m pip install pyshp'
    rc = run_as_admin([command, params], wait=True)

    if rc != 0:
        QMessageBox.warning(None, "Problem during installation", "Problem installing pyshp")
        return False
    return True


def install_cv2():
    """
        Install flopy without dependencies
    """
    # os_ver = platform.architecture()[0]
    # #compiled wheels can be found here: https://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy
    # if os_ver == '64bit':
    #     opencv_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'deps',
    #                               'opencv_python-3.4.1.15-cp27-cp27m-win_amd64.whl')
    # else:
    #     opencv_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'deps',
    #                               'opencv_python-3.4.1.15-cp27-cp27m-win_amd64.whl')

    if not command:
        open_ui()
    # params = 'python -m pip install {} {}'.format(opencv_path, proxy)
    params = 'python -m pip install opencv-python'
    rc = run_as_admin([command, params], wait=True)

    if rc != 0:
        QMessageBox.warning(None, "Problem during installation", "Problem installing opencv")
        return False
    return True


def install_all_deps():
    if not command:
        open_ui()
    pks = ['pandas', 'pyshp', 'opencv-python', 'flopy==3.2.9']
    params = 'python -m pip install {} {} {} {}'.format(pks[0], pks[1], pks[2], pks[3])
    # params = 'python -m pip install numpy --upgrade'
    #  params = 'python -m pip uninstall numpy'
    rc = run_as_admin([command, params], wait=True)

    if rc != 0:
        QMessageBox.warning(None, "Problem during installation", "Problem installing")
        return False
    return True


def install_missing_dep(packs):
    """
        Install missing QSWATMOD dependencies
    """
    if len(packs) == 5:
        # uninstall_numpy()
        install_numpy()
        install_enum()
        flag = install_all_deps()
        if not flag:
            return
        packages = ""
    else:
        packages = ""
        for dep in packs:
            if dep == 'pip':
                continue
            # if package[dep] or dep == 'pip':
            #     continue
            elif dep == "numpy":
                flag = install_numpy()
                if not flag:
                    return
            elif dep == "pandas":
                # packages += " pandas=={}".format(version.pandas)
                flag = install_pandas()
                if not flag:
                    return
            elif dep == "flopy":
                # install_setuptools()
                # install_enum()
                # packages += " flopy=={}".format(version.flopy)
                flag = install_flopy()
                if not flag:
                    return
            elif dep == "shapefile":
                # packages += " shapefile=={}".format(version.shapefile)
                flag = install_pyshp()
                if not flag:
                    return
            elif dep == "cv2":
                # packages += " cv2=={}".format(version.cv2)
                flag = install_cv2()
                if not flag:
                    return
            else:
                # install_numpy()
                packages += "{}".format(dep)
                QMessageBox.warning(None, "Restart!", "Please, click 'OK' to restart QGIS")

    if len(packages) == 0:
        write_file()
        QMessageBox.warning(None, "Installation completed!", "QSWATMOD plugin is ready to use!")
        return
    else:
        QMessageBox.warning(None, "Restart!", "Please, click 'OK' to restart QGIS")
    # if not command:
    #     open_ui()

    # params = 'python -m pip install{} {}'.format(packages, proxy)
    # rc = run_as_admin([command, params], wait=True)

    # if rc != 0:
    #     QMessageBox.warning(None, "Problem during installation", "Problem during installation, please try again")
    # else:
    #     rc = write_file()

    #     if rc == 0:
    #         QMessageBox.warning(None, "Installation done", "QSWATMOD plugin is ready to use!")


def write_file():
    """
        Write file to confirm that dependencies are installed
    """
    if not command:
        open_ui()

    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'writeFile.py')
    params = "python {}".format(path)
    rc = run_as_admin([command, params], wait=True)

    global proxy
    del proxy
    return rc
