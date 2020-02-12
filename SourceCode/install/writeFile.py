# -*- coding: utf-8 -*-
import os
file_name = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'install.txt')

with open(file_name, 'w') as f:

    string = "installation done"
    f.write(string)
    f.close()