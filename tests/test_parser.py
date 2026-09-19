"""funlanzou.api.parser 的 html 解析函数测试，覆盖正常路径与匹配不到的边界。"""

import pytest

from funlanzou.api.parser import (
    parse_desc,
    parse_file_name,
    parse_file_size,
    parse_folder_id,
    parse_form_hash,
    parse_sign,
    parse_time,
)


def test_parse_file_name_from_title():
    html = "<title>my-file.zip - 蓝奏云</title>"
    assert parse_file_name(html) == "my-file.zip"


def test_parse_file_name_strips_asterisk():
    html = "<title>my*file.zip - 蓝奏云</title>"
    assert parse_file_name(html) == "my_file.zip"


def test_parse_file_name_not_found_returns_placeholder():
    assert parse_file_name("<html></html>") == "未匹配到文件名"


def test_parse_file_size_found():
    html = "大小：12.3 M<"
    assert parse_file_size(html) == "12.3 M"


def test_parse_file_size_not_found_returns_empty_string():
    assert parse_file_size("<html></html>") == ""


def test_parse_time_not_found_returns_empty_string():
    assert parse_time("<html></html>") == ""


def test_parse_desc_not_found_returns_empty_string():
    assert parse_desc("<html></html>") == ""


def test_parse_sign_from_dict_literal():
    html = "var data = {'sign':'abcdefghijklmnopqrstuvwxyz',};"
    assert parse_sign(html) == "abcdefghijklmnopqrstuvwxyz"


def test_parse_sign_short_value_falls_back_to_sasign_variable():
    html = "'sign':'short',\nvar sasign = 'thisislongenoughvalue12345';"
    assert parse_sign(html) == "thisislongenoughvalue12345"


def test_parse_sign_raises_when_not_present():
    with pytest.raises(AttributeError):
        parse_sign("<html>no sign here</html>")


def test_parse_form_hash_found():
    html = '<input type="hidden" name="formhash" value="abc123">'
    assert parse_form_hash(html) == "abc123"


def test_parse_form_hash_raises_index_error_when_missing():
    with pytest.raises(IndexError):
        parse_form_hash("<html></html>")


def test_parse_folder_id_found():
    html = "var x = {'fid':'12345',};"
    assert parse_folder_id(html) == "12345"


def test_parse_folder_id_raises_index_error_when_missing():
    with pytest.raises(IndexError):
        parse_folder_id("<html></html>")
