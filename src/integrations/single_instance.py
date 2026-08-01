import sys
from pathlib import Path


MUTEX_NAME = r"Local\myMusic.SingleInstance"
ERROR_ALREADY_EXISTS = 183


if sys.platform.startswith('win'):
    import ctypes
    from ctypes import wintypes
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
elif sys.platform.startswith('linux'):
    import fcntl
else:
    raise OSError("Unsupported platform")


class SingleInstanceMutex:
    def __init__(self):
        self._handle = None
        self.linux_lock = None

        if sys.platform.startswith('win'):
            ctypes.set_last_error(0)
            mutex = kernel32.CreateMutexW(None, False, MUTEX_NAME)
            last_error = ctypes.get_last_error()

            if not mutex:
                raise ctypes.WinError(last_error)

            self._handle = mutex
            self.is_primary = last_error != ERROR_ALREADY_EXISTS

        elif sys.platform.startswith('linux'):
            cache_dir = Path.home() / ".cache" / "myMusic"
            cache_dir.mkdir(parents=True, exist_ok=True)
            lock_path = cache_dir / "single_instance.lock"

            lock_file = open(lock_path, "a+")

            try:
                fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.linux_lock = lock_file
                self.is_primary = True
            except BlockingIOError:
                lock_file.close()
                self.is_primary = False

    def close(self):
        if sys.platform.startswith('win'):
            if self._handle is None:
                return

            close = kernel32.CloseHandle(self._handle)

            if not close:
                raise ctypes.WinError(ctypes.get_last_error())

            self._handle = None

        elif sys.platform.startswith('linux'):
            if self.linux_lock is not None:
                try:
                    fcntl.flock(self.linux_lock, fcntl.LOCK_UN)
                finally:
                    self.linux_lock.close()
                    self.linux_lock = None
