# funlanzou

蓝奏云网盘的 API 封装与 PyQt 桌面客户端。

## 安装

```bash
pip install funlanzou
```

图形客户端额外依赖 PyQt6 等，需要安装 `gui` extra：

```bash
pip install funlanzou[gui]
```

## 使用

```python
from funlanzou.api.core import LanZouCloud
```

图形客户端入口在 `src/funlanzou/gui/gui.py`。

## 致谢

- API 封装基于 [zaxtyson/LanZouCloud-API](https://github.com/zaxtyson/LanZouCloud-API)（MIT 协议）。
- 浏览器 Cookie 读取功能内置了
  [borisbabic/browser_cookie3](https://github.com/borisbabic/browser_cookie3)
  （MIT 协议）。

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
