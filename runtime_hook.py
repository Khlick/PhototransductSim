# runtime_hook.py
import ctypes
import sys

if sys.platform == "win32":
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)  # 6 is for minimizing the console window
