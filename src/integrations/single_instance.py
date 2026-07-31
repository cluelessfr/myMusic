import ctypes
from ctypes import wintypes


MUTEX_NAME = r"Local\myMusic.SingleInstance"
ERROR_ALREADY_EXISTS = 183
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.CreateMutexW.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL


class SingleInstanceMutex:
    def __init__(self):
        ctypes.set_last_error(0)
        mutex = kernel32.CreateMutexW(None, False, MUTEX_NAME)
        last_error = ctypes.get_last_error()

        if not mutex:
            raise ctypes.WinError(last_error)

        self._handle = mutex
        self.is_primary = last_error != ERROR_ALREADY_EXISTS

    def close(self):
        if self._handle is None:
            return

        close = kernel32.CloseHandle(self._handle)

        if not close:
            raise ctypes.WinError(ctypes.get_last_error())

        self._handle = None
