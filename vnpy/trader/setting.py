"""
Global setting of the trading platform.
"""

from logging import CRITICAL
from typing import Dict, Any
from tzlocal import get_localzone_name

from .utility import load_json


SETTINGS: Dict[str, Any] = {
    "font.family": "微软雅黑",
    "font.size": 12,

    "log.active": True,
    "log.level": CRITICAL,
    "log.console": True,
    "log.file": True,

    "email.server": "smtp.qq.com",
    "email.port": 465,
    "email.username": "",
    "email.password": "",
    "email.sender": "",
    "email.receiver": "",

    "datafeed.name": "rqdata",
    "datafeed.username": "license",
    "datafeed.password": "gFwo3kKsr0GuKfaYTgnU83aSh8cZ6-e_mD5VbhzIfr1Cv1IvlxQYDn8_ld5FOM5nhb8Mj1cvWNYvwq_RRlp5QKudKLT-cUO-dzbwhuLda93lTSEBQcJqUiXB0xNjFvoeEH35rvwOmBaWtXIrAZOad8KGQtBq2jLVHKwW0yrx24M=HXEOyElfuo9kRGdy_W2etyoU8GTPtqJTTGj2Qs5IXNnAwaAiLip0cikfsL180wvoXvkbjTEbVrBVeRTyBEzMRml7m2e1UZ5NpjtBHZFT8PW02pQvu0VGGtC07qaabXBIr3VfR7knrPjf2r5BUIk4pZREthCIQH2ZgQF8bW9Y7QE=",

    "database.timezone": get_localzone_name(),
    "database.name": "sqlite",
    "database.database": "database.db",
    "database.host": "",
    "database.port": 0,
    "database.user": "",
    "database.password": ""
}


# Load global setting from json file.
SETTING_FILENAME: str = "vt_setting.json"
SETTINGS.update(load_json(SETTING_FILENAME))


def get_settings(prefix: str = "") -> Dict[str, Any]:
    prefix_length: int = len(prefix)
    settings = {k[prefix_length:]: v for k, v in SETTINGS.items() if k.startswith(prefix)}
    return settings
