import json

import requests
from funsecret import read_secret

from funlanzou.api.utils import USER_AGENT
from funlanzou.debug import logger

timeout = 2

# 调用第三方短链接口时可能遇到的失败类型：
# - requests.RequestException：网络层失败
# - json.JSONDecodeError（ValueError 子类）：响应不是合法 JSON
# - KeyError / TypeError：响应 JSON 结构与预期不符，取不到 `short` 字段
_SHORTEN_ERRORS = (requests.RequestException, ValueError, KeyError, TypeError)


def _post_shorten(api_url: str, url: str, token: str) -> str:
    """向需要 Token 鉴权的短链服务提交一次缩短请求。

    Args:
        api_url: 短链服务的 API 地址。
        url: 待缩短的长链接。
        token: 该服务的访问令牌；仅放入这次请求专属的请求头，不会被其他服务复用。

    Returns:
        缩短后的短链接；失败时返回空字符串。
    """
    # 每个服务使用独立的 headers，避免一个服务的 Token 被带去另一个服务（跨服务泄露）
    headers = {"User-Agent": USER_AGENT, "Authorization": f"Token {token}"}
    try:
        resp = requests.post(api_url, json={"url": url}, headers=headers, timeout=timeout)
        rsp = json.loads(resp.text)
        if rsp:
            return rsp["short"]
    except _SHORTEN_ERRORS as e:
        logger.warning(f"短链服务调用失败: api={api_url} reason={type(e).__name__}: {e}")
    return ""


def get_short_url(url: str) -> str:
    """把长链接转换成短链接。

    依次尝试：配置了 Token 的 dwz.lc、ecx.cx，然后是无需鉴权的 tinyurl、gg.gg。
    对应的 funsecret 配置项未设置时自动跳过该服务商，不在代码里硬编码凭据。

    Args:
        url: 待缩短的长链接。

    Returns:
        缩短后的短链接；所有服务都失败时返回空字符串。
    """
    short_url = ""

    dwz_token = read_secret("funlanzou", "api", "extra", "dwz_lc_token")
    if dwz_token:
        short_url = _post_shorten("https://www.dwz.lc/api/url/add", url, dwz_token)

    ecx_token = read_secret("funlanzou", "api", "extra", "ecx_cx_token")
    if not short_url and ecx_token:
        short_url = _post_shorten("https://www.ecx.cx/api/url/add", url, ecx_token)

    if not short_url:
        headers = {"User-Agent": USER_AGENT}
        try:
            # https, 国外,速度较慢
            resp = requests.get(f"https://tinyurl.com/api-create.php?url={url}", headers=headers, timeout=timeout)
            if resp.text and len(resp.text) < 32:
                short_url = resp.text
        except requests.RequestException as e:
            logger.warning(f"短链服务调用失败: api=tinyurl reason={type(e).__name__}: {e}")

    if not short_url:
        headers = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        try:
            # 支持https, 国外,速度较慢
            resp = requests.post(
                "http://gg.gg/create", data={"long_url": url}, headers=headers, timeout=timeout
            ).text
            if resp:
                short_url = resp
        except requests.RequestException as e:
            logger.warning(f"短链服务调用失败: api=gg.gg reason={type(e).__name__}: {e}")

    return short_url
