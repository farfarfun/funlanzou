"""
全局常量与 logger。

注意：本模块会被纯 API 用法间接导入（`funlanzou.api.core` 等模块从这里取
`logger`），因此这里只计算路径常量，不在 import 时创建目录或写文件——
真正需要落盘的地方（GUI 配置读写）自己在写入前调用 `ensure_app_dir()`。
"""

import os

from farlog import getLogger

__all__ = ['logger', 'SRC_DIR', 'CONFIG_FILE', 'DL_DIR', 'BG_IMG', 'USER_HOME', 'ensure_app_dir']

# 全局常量: USER_HOME, DL_DIR, SRC_DIR, BG_IMG, CONFIG_FILE
USER_HOME = os.path.expanduser('~')
if os.name == 'nt':  # Windows
    root_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(root_dir)
    import winreg

    sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
    downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
        DL_DIR = winreg.QueryValueEx(key, downloads_guid)[0]
else:  # Linux and MacOS ...
    root_dir = USER_HOME + os.sep + '.config' + os.sep + 'lanzou-gui'
    DL_DIR = USER_HOME + os.sep + 'Downloads'

SRC_DIR = root_dir + os.sep + "resources" + os.sep
BG_IMG = (SRC_DIR + "default_background_img.jpg").replace('\\', '/')
CONFIG_FILE = root_dir + os.sep + 'config.pkl'

logger = getLogger("funlanzou")


def ensure_app_dir() -> None:
    """确保 GUI 本地配置目录存在，仅在真正需要写入配置时调用。"""
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
