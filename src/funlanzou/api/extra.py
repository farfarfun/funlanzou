import json

import requests
from funsecret import read_secret

from funlanzou.api.utils import USER_AGENT
from funlanzou.debug import logger

timeout = 2


def get_short_url(url: str) -> str:
    """短链接生成器"""
    headers = {'User-Agent': USER_AGENT}
    short_url = ""

    # token 通过 funsecret 配置，未配置则跳过该服务商，不在代码里硬编码凭据
    dwz_token = read_secret("funlanzou", "api", "extra", "dwz_lc_token")
    if dwz_token:
        try:
            post_data = {"url": url}
            headers["Authorization"] = f"Token {dwz_token}"
            resp = requests.post("https://www.dwz.lc/api/url/add", json=post_data, headers=headers, timeout=timeout)
            rsp = json.loads(resp.text)
            if rsp:
                short_url = rsp["short"]
        except Exception as e:
            logger.error(f"get_short_url error: e={e}")

    ecx_token = read_secret("funlanzou", "api", "extra", "ecx_cx_token")
    if not short_url and ecx_token:
        try:
            post_data = {"url": url}
            headers["Authorization"] = f"Token {ecx_token}"
            resp = requests.post("https://www.ecx.cx/api/url/add", json=post_data, headers=headers, timeout=timeout)
            rsp = json.loads(resp.text)
            if rsp:
                short_url = rsp["short"]
        except Exception as e:
            logger.error(f"get_short_url error: e={e}")

    if not short_url:
        try:
            # https, 国外,速度较慢
            resp = requests.get(f"https://tinyurl.com/api-create.php?url={url}", headers=headers, timeout=timeout)
            if resp.text and len(resp.text) < 32:
                short_url = resp.text
        except Exception as e:
            logger.error(f"get_short_url error: e={e}")

    if not short_url:
        headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        post_data = {"long_url": url}
        try:
            # 支持https, 国外,速度较慢
            resp = requests.post("http://gg.gg/create", data=post_data, headers=headers, timeout=timeout).text
            if resp:
                short_url = resp
        except Exception as e:
            logger.error(f"get_short_url2 error: e={e}")

    return short_url
