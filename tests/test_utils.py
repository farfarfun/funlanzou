"""funlanzou.api.utils 的公开函数测试：只测纯函数，不发网络请求。"""

from funlanzou.api.utils import (
    convert_file_size_to_int,
    convert_file_size_to_str,
    is_folder_url,
    is_name_valid,
    name_format,
    remove_notes,
    time_format,
)


def test_remove_notes_strips_html_and_js_comments():
    html = "<div>ok</div><!-- 注释 --><script>var a = 1; // 行内注释\n</script>"
    result = remove_notes(html)
    assert "注释" not in result
    assert "行内注释" not in result
    assert "<div>ok</div>" in result


def test_name_format_strips_illegal_chars_and_extra_spaces():
    assert name_format('a<b>c:d "e"  f') == "abcd e f"


def test_name_format_normalizes_unicode_whitespace():
    assert name_format("a\xa0b　c") == "a b c"


def test_is_name_valid_true_for_known_suffix():
    assert is_name_valid("archive.ZIP") is True


def test_is_name_valid_false_for_unknown_suffix():
    assert is_name_valid("binary.unknownext") is False


def test_convert_file_size_to_int_units():
    assert convert_file_size_to_int("1K") == 1 << 10
    assert convert_file_size_to_int("1M") == 1 << 20
    assert convert_file_size_to_int("1G") == 1 << 30
    assert convert_file_size_to_int("100B") == 100


def test_convert_file_size_to_int_unknown_unit_returns_zero():
    assert convert_file_size_to_int("100") == 0


def test_convert_file_size_to_str_round_trip_ranges():
    assert convert_file_size_to_str(500).endswith("B")
    assert convert_file_size_to_str(5 * (1 << 10)).endswith("K")
    assert convert_file_size_to_str(5 * (1 << 20)).endswith("M")
    assert convert_file_size_to_str(5 * (1 << 30)).endswith("G")


def test_time_format_relative_expressions_become_today():
    today = time_format("5 秒前")
    assert len(today) == len("2026-01-01")


def test_time_format_passthrough_for_absolute_date():
    assert time_format("2024-01-02") == "2024-01-02"


def test_is_folder_url_matches_normal_share_link_without_network():
    # 普通用户分享链接命中固定正则分支，不需要发网络请求
    assert is_folder_url("https://leon.lanzoub.com/b0d8h93hi") is True


def test_is_folder_url_false_for_unrelated_domain():
    assert is_folder_url("https://example.com/foo") is False
