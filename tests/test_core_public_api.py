"""`LanZouCloud` 公开 API 的正常路径/边界/失败路径回归测试。

对应 codex 审计 farfarfun/todo-list#562 的 finding 6：README 的最小示例之外，
`LanZouCloud` 的登录、Cookie 登录、文件查询等公开 API 原先没有不依赖真实网络的
测试覆盖。这里全部 mock `_get`/`_post`，不发起真实请求。
"""

import warnings
from unittest import mock

from funlanzou.api import core
from funlanzou.api.models import FolderList
from funlanzou.api.types import Folder


def _resp(text="", status_code=200, json_data=None):
    resp = mock.Mock(status_code=status_code)
    resp.text = text
    if json_data is not None:
        resp.json.return_value = json_data
    return resp


# ----------------------------------------------------------------------- login


def test_login_is_deprecated_and_warns():
    drive = core.LanZouCloud()
    with (
        mock.patch.object(drive, "_get", return_value=None),
        warnings.catch_warnings(record=True) as caught,
    ):
        warnings.simplefilter("always")
        code = drive.login("demo-user", "demo-pwd")

    assert code == core.LanZouCloud.NETWORK_ERROR
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)


def test_login_returns_network_error_when_account_page_unreachable():
    drive = core.LanZouCloud()
    with mock.patch.object(drive, "_get", return_value=None):
        assert drive.login("u", "p") == core.LanZouCloud.NETWORK_ERROR


def test_login_returns_failed_when_formhash_missing():
    drive = core.LanZouCloud()
    with mock.patch.object(drive, "_get", return_value=_resp(text="<html></html>")):
        assert drive.login("u", "p") == core.LanZouCloud.FAILED


def test_login_returns_success_when_server_confirms():
    drive = core.LanZouCloud()
    account_page = _resp(text='name="formhash" value="abc123"')
    login_resp = mock.Mock()
    login_resp.cookies.get_dict.return_value = {"phpdisk_info": "demo"}
    login_resp.json.return_value = {"info": "登录成功"}

    with (
        mock.patch.object(drive, "_get", return_value=account_page),
        mock.patch.object(drive, "_post", return_value=login_resp),
    ):
        assert drive.login("u", "p") == core.LanZouCloud.SUCCESS
    assert drive.get_cookie() == {"phpdisk_info": "demo"}


# ---------------------------------------------------------------- login_by_cookie


def test_login_by_cookie_success():
    drive = core.LanZouCloud()
    with mock.patch.object(drive, "_get", return_value=_resp(text="个人中心")):
        assert drive.login_by_cookie({"ylogin": "1"}) == core.LanZouCloud.SUCCESS


def test_login_by_cookie_failed_when_session_expired():
    drive = core.LanZouCloud()
    with mock.patch.object(drive, "_get", return_value=_resp(text="网盘用户登录")):
        assert drive.login_by_cookie({"ylogin": "1"}) == core.LanZouCloud.FAILED


def test_login_by_cookie_network_error():
    drive = core.LanZouCloud()
    with mock.patch.object(drive, "_get", return_value=None):
        assert drive.login_by_cookie({"ylogin": "1"}) == core.LanZouCloud.NETWORK_ERROR


# ------------------------------------------------------------- get_file_info_by_url


def test_get_file_info_by_url_rejects_folder_urls():
    drive = core.LanZouCloud()
    with mock.patch.object(core, "is_file_url", return_value=False):
        info = drive.get_file_info_by_url("https://demo.lanzoub.com/bxxxx")
    assert info.code == core.LanZouCloud.URL_INVALID


def test_get_file_info_by_url_network_error_when_first_page_missing():
    drive = core.LanZouCloud()
    with (
        mock.patch.object(core, "is_file_url", return_value=True),
        mock.patch.object(drive, "_get", return_value=None),
    ):
        info = drive.get_file_info_by_url("https://demo.lanzoub.com/ixxxx")
    assert info.code == core.LanZouCloud.NETWORK_ERROR


def test_get_file_info_by_url_requires_password_when_page_asks_for_one():
    drive = core.LanZouCloud()
    page = _resp(text='<div id="pwdload"></div>')
    with (
        mock.patch.object(core, "is_file_url", return_value=True),
        mock.patch.object(drive, "_get", return_value=page),
    ):
        info = drive.get_file_info_by_url("https://demo.lanzoub.com/ixxxx", pwd="")
    assert info.code == core.LanZouCloud.LACK_PASSWORD


def test_get_file_info_by_url_reports_cancelled_file():
    drive = core.LanZouCloud()
    page = _resp(text="文件取消分享了")
    with (
        mock.patch.object(core, "is_file_url", return_value=True),
        mock.patch.object(drive, "_get", return_value=page),
    ):
        info = drive.get_file_info_by_url("https://demo.lanzoub.com/ixxxx")
    assert info.code == core.LanZouCloud.FILE_CANCELLED


# -------------------------------------------------------------------------- delete


def test_delete_file_success():
    drive = core.LanZouCloud()
    with mock.patch.object(
        drive, "_post", return_value=_resp(json_data={"zt": 1})
    ) as post:
        assert drive.delete(1, is_file=True) == core.LanZouCloud.SUCCESS
    assert post.call_args.args[1] == {"task": 6, "file_id": 1}


def test_delete_folder_failed_when_server_rejects():
    drive = core.LanZouCloud()
    with mock.patch.object(drive, "_post", return_value=_resp(json_data={"zt": 0})):
        assert drive.delete(2, is_file=False) == core.LanZouCloud.FAILED


def test_delete_network_error_when_post_fails():
    drive = core.LanZouCloud()
    with mock.patch.object(drive, "_post", return_value=None):
        assert drive.delete(1) == core.LanZouCloud.NETWORK_ERROR


# ----------------------------------------------------------------- clean_ghost_folders


def test_clean_ghost_folders_returns_int_and_handles_no_ghosts():
    """回归测试：`get_dir_list` 返回 (folder_list, path_list) 二元组，
    `_clean` 必须只递归 folder_list，否则会把 FolderList 当 Folder 用，
    访问 `.id` 时抛 AttributeError。"""
    drive = core.LanZouCloud()
    root = Folder(name="root-child", id=1, has_pwd=False, desc="")
    child_list = FolderList()
    child_list.append(root)
    empty_list = FolderList()

    def fake_get_dir_list(folder_id):
        if folder_id == -1:
            return child_list, empty_list
        return empty_list, empty_list

    move_folders = FolderList()
    move_folders.append(Folder(name="root", id=-1, has_pwd=False, desc=""))
    move_folders.append(root)

    with (
        mock.patch.object(drive, "get_dir_list", side_effect=fake_get_dir_list),
        mock.patch.object(drive, "get_move_folders", return_value=move_folders),
    ):
        code = drive.clean_ghost_folders()

    assert code == core.LanZouCloud.SUCCESS
    assert isinstance(code, int)


def test_clean_ghost_folders_deletes_folder_not_reachable_from_root():
    drive = core.LanZouCloud()
    ghost = Folder(name="ghost", id=99, has_pwd=False, desc="")
    empty_list = FolderList()

    move_folders = FolderList()
    move_folders.append(Folder(name="root", id=-1, has_pwd=False, desc=""))
    move_folders.append(ghost)

    with (
        mock.patch.object(drive, "get_dir_list", return_value=(empty_list, empty_list)),
        mock.patch.object(drive, "get_move_folders", return_value=move_folders),
        mock.patch.object(
            drive, "delete", return_value=core.LanZouCloud.SUCCESS
        ) as mocked_delete,
        mock.patch.object(
            drive, "delete_rec", return_value=core.LanZouCloud.SUCCESS
        ) as mocked_delete_rec,
    ):
        code = drive.clean_ghost_folders()

    assert code == core.LanZouCloud.SUCCESS
    mocked_delete.assert_called_once_with(99, False)
    mocked_delete_rec.assert_called_once_with(99, False)
