import os
from . import SCC_Logs as Logs

if (not os.path.exists(Logs.DEFAULT_TRUE_ADDRESS)) or (not os.listdir(Logs.DEFAULT_TRUE_ADDRESS)):
    Logs.Logs(first_run=True)

# SCC项目版本号
Logs.SOFTWARE_VERSION = '0.1.0 pro-alpha'
