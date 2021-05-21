import os
from . import SCC_Logs as Logs

if (not os.path.exists(Logs.DEFAULT_TRUE_ADDRESS)) or (not os.listdir(Logs.DEFAULT_TRUE_ADDRESS)):
    Logs.Logs(run_first=True)

Logs.LOG_LEVEL = '0.1.0 pro-alpha'
