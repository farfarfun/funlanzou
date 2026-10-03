import re

from funlanzou.debug import logger

"""html页面参数解析"""


def parse_file_name(html: str) -> str:
    """从文件分享页 HTML 中解析文件名。

    Args:
        html: 文件分享页面的 HTML 文本。

    Returns:
        解析出的文件名（`*` 会被替换为 `_`）；未匹配到时返回 `"未匹配到文件名"`。
    """
    name = re.search(r"<title>(.+?) - 蓝奏云</title>", html) or \
           re.search(r'<div class="filethetext".+?>([^<>]+?)</div>', html) or \
           re.search(r'<div style="font-size.+?>([^<>].+?)</div>', html) or \
           re.search(r"var filename = '(.+?)';", html) or \
           re.search(r'id="filenajax">(.+?)</div>', html) or \
           re.search(r'<div class="b"><span>([^<>]+?)</span></div>', html)

    return name.group(1).replace("*", "_") if name else "未匹配到文件名"


def parse_file_size(html: str) -> str:
    """从文件分享页 HTML 中解析文件大小描述。

    Args:
        html: 文件分享页面的 HTML 文本。

    Returns:
        形如 `"12.3 M"` 的大小描述；未匹配到时返回空字符串。
    """
    size = re.search(r'大小.+?(\d[\d.,]+\s?[BKM]?)<', html) or \
           re.search(r'class="n_filesize">[^<0-9]*([.0-9 MKBmkbGg]+)<', html) or \
           re.search(r'大小：(.+?)</div>', html)  # VIP 分享页面
    return size.group(1) if size else ""


def parse_time(html: str) -> str:
    """从分享页 HTML 中解析上传时间描述（可能是相对时间，如“5 天前”）。

    Args:
        html: 分享页面的 HTML 文本。

    Returns:
        原始时间描述字符串；未匹配到时返回空字符串。
    """
    time = re.search(r'class="n_file_infos">(.+?)</span>', html) or \
           re.search(r'>(\d+\s?[秒天分小][钟时]?前|[昨前]天\s?[\d:]+?|\d+\s?天前|\d{4}-\d\d-\d\d)<', html)
    return time.group(1) if time else ''


def parse_desc(html: str) -> str:
    """从文件分享页 HTML 中解析文件描述。

    Args:
        html: 文件分享页面的 HTML 文本。

    Returns:
        文件描述文本；未匹配到时返回空字符串。
    """
    desc = re.search(r'class="n_box_des">(.*?)</div>', html) or \
           re.search(r'文件描述.+?</span><br>\n?\s*(.*?)\s*</td>', html)
    return desc.group(1) if desc else ''


def parse_sign(html: str) -> str:
    """从分享页 HTML 中解析下载请求所需的 `sign` 参数。

    Args:
        html: 分享页面或下载页面的 HTML 文本。

    Returns:
        `sign` 参数值（已去除包裹的单引号）。

    Raises:
        AttributeError: 页面结构变化导致三种候选正则均未命中。
    """
    # 一般情况 sign 的值就在 data 里，有时放在变量后面
    sign = (re.search(r"'sign':(.+?),", html) or
            re.search(r"'sign'\s*:\s*'(.+?)'", html) or
            re.search(r"sign=(\w+?)&", html)).group(1)
    if len(sign) < 20:  # 此时 sign 保存在变量里面, 变量名是 sign 匹配的字符
        sign = re.findall(r"var sasign\s*=\s*'(.{10,}?)';", html)[-1]
    return sign.replace("'", "")


def parse_form_hash(html: str) -> str:
    """从登录/控制台页面 HTML 中解析表单的 `formhash` 隐藏字段。

    Args:
        html: 页面 HTML 文本。

    Returns:
        `formhash` 字段值。

    Raises:
        IndexError: 页面中不存在 `formhash` 字段。
    """
    return re.findall(r'name="formhash" value="(.+?)"', html)[0]


def parse_folder_name(html: str) -> str:
    """从文件夹分享页 HTML 中解析文件夹名称。

    Args:
        html: 文件夹分享页面的 HTML 文本。

    Returns:
        文件夹名称；未匹配到时返回空字符串。
    """
    folder_name = re.search(r"var.+?='(.+?)';\n.+document.title", html) or \
                  re.search(r'user-title">(.+?)</div>', html) or \
                  re.search(r'<div class="b">(.+?)<div', html)  # 会员自定义
    return folder_name.group(1) if folder_name else ''


def parse_folder_id(html: str) -> str:
    """从文件夹分享页 HTML 中解析文件夹 id（`fid`）。

    Args:
        html: 文件夹分享页面的 HTML 文本。

    Returns:
        文件夹 id 字符串。

    Raises:
        IndexError: 页面中不存在 `fid` 字段。
    """
    return re.findall(r"'fid':'?(\d+)'?,", html)[0]


def parse_folder_time(html: str) -> str:
    """从文件夹分享页 HTML 中解析创建日期（通常只有月、日，不含年份）。

    Args:
        html: 文件夹分享页面的 HTML 文本。

    Returns:
        形如 `"MM-DD"` 的日期片段；未匹配到时返回空字符串。
    """
    folder_time = re.search(r'class="rets">([\d\-]+?)<a', html)  # 日期不全 %m-%d
    return folder_time.group(1) if folder_time else ''


def parse_folder_desc(html: str) -> str:
    """从文件夹分享页 HTML 中解析文件夹描述。

    Args:
        html: 文件夹分享页面的 HTML 文本。

    Returns:
        文件夹描述文本；未匹配到时返回空字符串。
    """
    folder_desc = re.search(r'id="filename">(.+?)</span>', html, re.DOTALL) or \
                  re.search(r'<div class="user-radio-\d"></div>(.+?)</div>', html) or \
                  re.search(r'class="teta tetb">说</span>(.+?)</div><div class="d2">', html, re.DOTALL)
    return folder_desc.group(1) if folder_desc else ''
