import sys

from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"
    
buildOptions = dict(
        copy_dependent_files = True,
        path = sys.path + ["C:\Users\kundlj\Documents\GitHub\PythonDaysimeter12Client"],
        includes = ["atexit", "scipy.sparse.csgraph._validation", \
        "scipy.sparse.linalg.dsolve.umfpack", "scipy.integrate.vode", \
        "scipy.integrate.lsoda"])

setup(
        name = "Daysimeter Client",
        version = "0.1",
        description = "Client for interfacing with LRC's Daysimeter 12",
        options = dict(build_exe = buildOptions),
        executables = [Executable("daysimdlclient.py", base = base)])
