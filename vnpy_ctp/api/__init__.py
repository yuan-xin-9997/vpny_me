import os
from pathlib import Path


if hasattr(os, "add_dll_directory"):
    os.add_dll_directory(str(Path(__file__).resolve().parent))

from .vnctp.vnctpmd import MdApi      # noqa
from .vnctp.vnctptd import TdApi      # noqa
from .ctp_constant import *     # noqa
