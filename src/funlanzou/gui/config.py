import hashlib
import json
import pickle
from pickle import load, dump

from funsecret import read_secret, write_secret

from funlanzou.debug import CONFIG_FILE, DL_DIR, ensure_app_dir, logger

__all__ = ['config']

# 仅用于读取并迁移旧版本配置；新凭据统一由 funsecret 管理。
KEY = 152  # config 混淆 key

default_settings = {
    "download_threads": 3,  # 同时三个下载任务
    "timeout": 5,  # 每个请求的超时 s(不包含下载响应体的用时)
    "max_size": 100,  # 单个文件大小上限 MB
    "dl_path": DL_DIR,
    "time_fmt": False,  # 是否使用年月日时间格式
    "to_tray": False,  # 关闭到系统托盘
    "watch_clipboard": False,  # 监听系统剪切板
    "debug": False,  # 调试
    "set_pwd": False,
    "pwd": "",
    "set_desc": False,
    "desc": "",
    "upload_delay": 20,  # 上传大文件延时 0 - 20s
    "allow_big_file": False,
    "upgrade": True
}


def _decrypt_legacy(s):
    c = bytearray(str(s).encode("utf-8"))
    n = len(c)
    if n % 2 != 0:
        return ""
    n = n // 2
    b = bytearray(n)
    j = 0
    for i in range(0, n):
        c1 = c[j]
        c2 = c[j + 1]
        j = j + 2
        c1 = c1 - 46
        c2 = c2 - 46
        b2 = c2 * 19 + c1
        b1 = b2 ^ KEY
        b[i] = b1
    return b.decode("utf-8")


def save_config(cf):
    ensure_app_dir()
    with open(CONFIG_FILE, 'wb') as f:
        dump(cf, f)


def _secret_user_id(name: str) -> str:
    return hashlib.sha256(name.encode("utf-8")).hexdigest()


def _read_credential(name: str, kind: str):
    if not name:
        return None
    value = read_secret("funlanzou", "gui", _secret_user_id(name), kind)
    if kind == "cookie" and value:
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            logger.error("funsecret 中保存的 Cookie 格式无效")
            return None
    return value


def _write_credential(name: str, kind: str, value) -> None:
    if not name:
        return
    if kind == "cookie" and value:
        value = json.dumps(value, ensure_ascii=True)
    write_secret(value or "", "funlanzou", "gui", _secret_user_id(name), kind)


class Config:
    """存储登录用户信息"""

    def __init__(self):
        self._users = {}
        self._cookie = ''
        self._name = ''
        self._pwd = ''
        self._work_id = -1
        self._settings = default_settings
        self._credentials_migrated = True

    def update_user(self):
        if self._name:
            self._users[self._name] = ('', self._name, '',
                                       self._work_id, self._settings)
            save_config(self)

    def del_user(self, name) -> bool:
        if name in self._users:
            _write_credential(name, "password", "")
            _write_credential(name, "cookie", "")
            del self._users[name]
            return True
        return False

    def change_user(self, name) -> bool:
        if name in self._users:
            self.update_user()  # 切换用户前保持目前用户信息
            user = self._users[name]
            self._cookie = ''
            self._name = user[1]
            self._pwd = ''
            self._work_id = user[3]
            self._settings = user[4]
            save_config(self)
            return True
        return False

    @property
    def users_name(self) -> list:
        return list(self._users)

    def get_user_info(self, name):
        """返回用户名、pwd、cookie"""
        if name in self._users:
            return name, _read_credential(name, "password"), _read_credential(name, "cookie")

    def default_path(self):
        path = default_settings['dl_path']
        self._settings.update({'dl_path': path})
        save_config(self)

    @property
    def default_settings(self):
        return default_settings

    @property
    def name(self):
        return self._name

    @property
    def pwd(self):
        return _read_credential(self.name, "password")

    @property
    def cookie(self):
        return _read_credential(self.name, "cookie")

    @cookie.setter
    def cookie(self, cookie):
        _write_credential(self.name, "cookie", cookie)
        self._cookie = ''
        save_config(self)

    @property
    def work_id(self):
        return self._work_id

    @work_id.setter
    def work_id(self, work_id):
        self._work_id = work_id
        save_config(self)

    def set_cookie(self, cookie):
        _write_credential(self.name, "cookie", cookie)
        self._cookie = ''
        save_config(self)

    def set_username(self, username):
        self._name = username
        save_config(self)

    @property
    def path(self):
        return self._settings['dl_path']

    @path.setter
    def path(self, path):
        self._settings.update({'dl_path': path})
        save_config(self)

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, settings):
        self._settings = settings
        save_config(self)

    def set_infos(self, infos: dict):
        self.update_user()  # 切换用户前保持目前用户信息
        if "name" in infos:
            self._name = infos["name"]
        if "pwd" in infos:
            _write_credential(self.name, "password", infos["pwd"])
            self._pwd = ''
        if "cookie" in infos:
            _write_credential(self.name, "cookie", infos["cookie"])
            self._cookie = ''
        if "path" in infos:
            self._settings.update({'dl_path': infos["path"]})
        if "work_id" in infos:
            self._work_id = infos["work_id"]
        if "settings" in infos:
            self._settings = infos["settings"]
        save_config(self)

    def migrate_credentials(self) -> bool:
        """将旧 pickle 中的凭据迁移到 funsecret。"""
        if getattr(self, "_credentials_migrated", False):
            return False

        changed = True
        migrated_users = {}
        for encoded_name, user in list(self._users.items()):
            try:
                name = _decrypt_legacy(encoded_name)
                cookie = {key: _decrypt_legacy(value) for key, value in user[0].items()} if user[0] else None
                password = _decrypt_legacy(user[2]) if user[2] else None
            except (AttributeError, TypeError, UnicodeDecodeError, ValueError):
                logger.error("旧版凭据配置格式无效，已跳过")
                continue
            if password:
                _write_credential(name, "password", password)
            if cookie:
                _write_credential(name, "cookie", cookie)
            migrated_users[name] = ('', name, '', user[3], user[4])

        try:
            name = _decrypt_legacy(self._name) if self._name else ''
            password = _decrypt_legacy(self._pwd) if self._pwd else None
            cookie = {key: _decrypt_legacy(value) for key, value in self._cookie.items()} if self._cookie else None
        except (AttributeError, TypeError, UnicodeDecodeError, ValueError):
            logger.error("旧版当前用户凭据格式无效，已跳过")
            name = password = cookie = None
        if password:
            _write_credential(name, "password", password)
        if cookie:
            _write_credential(name, "cookie", cookie)
        self._users = migrated_users
        self._name = name or ''
        self._pwd = self._cookie = ''
        self._credentials_migrated = True
        return changed


# 全局配置对象
try:
    with open(CONFIG_FILE, 'rb') as c:
        config = load(c)
    if config.migrate_credentials():
        save_config(config)
except FileNotFoundError:
    config = Config()
except (OSError, EOFError, pickle.UnpicklingError) as e:
    logger.error(f"Load config file {CONFIG_FILE} failed, fall back to default: {e}")
    config = Config()
