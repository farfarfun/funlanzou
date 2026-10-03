# Changelog

## [未发布]

> 本节记录 issue #427、#562、#726 审计修复的改动，版本号与发布日期留给
> `funbuild` 走正式发布流程时填写，这里不手动递增版本号。

### 新增

- `pyproject.toml` 补齐运行时依赖声明（`farlog`、`funsecret`、`requests`、
  `requests-toolbelt`、`urllib3`），并新增 `gui` extra（`PyQt6`、
  `PyQt6-WebEngine`、`keyring`、`lz4`、`pycryptodomex`）隔离图形客户端依赖。
- 提交 `uv.lock`，保证可复现构建。
- README 补充安装/使用说明、第三方代码来源声明
  （`zaxtyson/LanZouCloud-API`、`borisbabic/browser_cookie3`，均为 MIT）及组织
  介绍区块。
- `pyproject.toml` 新增 `[project.scripts]`，注册 `funlanzou-gui` 命令行入口
  （`funlanzou.gui.gui:main`），对应 README 的 `uv tool install 'funlanzou[gui]'`
  安装方式；`gui.py` 补充 `main()`/`__main__` 启动入口。
- `LanZouCloud.login` 已弃用方法补充 `DeprecationWarning`，README/CHANGELOG
  同步说明替代方案为 `login_by_cookie()`。
- 新增 `tests/test_core_public_api.py`：覆盖 `login`/`login_by_cookie`/
  `get_file_info_by_url`/`delete`/`clean_ghost_folders` 等公开 API 的正常、
  边界与失败路径，网络一律 mock。

### 修复

- 源码布局迁移到标准 `src/funlanzou/`、`src/lanzou/`，同步更新
  `[tool.hatch.build.targets.wheel]` 打包配置。
- `funlanzou/debug.py` 不再在 import 时创建配置目录、配置全局 logging
  handler；改用 `farlog.getLogger`，目录创建延后到真正写配置文件时
  （`ensure_app_dir()`）。
- 移除 `LanZouCloud.login_by_cookie`、`down_file_by_url` 等处打印 cookie/
  下载进度等诊断信息的 `print()`；将会把提取码等敏感字段写入日志的
  `logger.error` 降级为 `logger.debug` 并脱敏（不再记录 `pwd` 字段本身）。
- `get_short_url` 中硬编码的第三方短链服务 API token 迁移到 `funsecret`
  读取，未配置时直接跳过该服务商，不再有硬编码凭据。
- 修复多处裸 `except:` 吞掉异常：改为捕获具体异常类型，并在
  `funlanzou/gui/config.py`、`funlanzou/gui/dialogs/login.py` 等处记录带上下文
  的错误日志。
- 修复 `funlanzou/login_assister.py` 仍在使用 `PyQt5`、与包内其余 GUI 模块
  （已是 `PyQt6`）不一致导致运行时无法同进程共存的问题，统一迁移到
  `PyQt6`/`PyQt6-WebEngine`。
- `LanZouCloud._get`/`_head`/`_post`/`login` 等方法补充类型标注与
  参数/返回值说明的 docstring。
- 移除 `core.py` import 期的网络副作用（原先 import 时就 `executors.submit`
  探测域名）；`check_domains()` 改为纯探测、不就地修改模块级
  `available_domains`，新增 `refresh_available_domains()` 显式刷新；修复
  `check_domains` 边遍历边删导致漏判域名的缺陷，探测超时从硬编码 0.1s 放宽为
  可配置的 5s。
- 修复两处无限重试热循环：`get_file_list`（网络异常 `continue` 不计数）、
  `get_folder_info_by_url`（服务端返回「请刷新，重试」时 `continue` 不计数），
  统一受 `_MAX_REFRESH_RETRY` 约束，连续失败达到上限后放弃并返回错误码。
- 修复两处 `None` 解引用：`get_file_info_by_url`/`get_share_info` 在
  `second_page` 为 `None` 时仍访问 `.text` 会抛 `AttributeError`。
- 修复短链 Token 跨服务泄露：`get_short_url` 原先 4 个短链服务共用同一个
  `headers` dict，dwz.lc 的 Token 会被带去 ecx.cx 等其他服务；改为每次请求
  使用独立 headers。
- 修复 `LanZouCloud.login` 两处缺陷：账号页解析不到 `formhash` 时原先的
  `if not formhash` 判断是死代码（`parse_form_hash` 找不到时直接抛
  `IndexError`，未被捕获会导致调用方崩溃），现在显式捕获并返回 `FAILED`；
  `login_data['formhash'] = formhash[0]` 原先把 `formhash` 误当列表切片，
  实际只取到了返回字符串的第一个字符，导致登录请求永远带着错误的
  formhash，现在直接使用完整值。
- 修复 `clean_ghost_folders` 内部 `_clean` 递归 bug：`get_dir_list` 返回
  `(folder_list, path_list)` 二元组，原代码直接遍历该元组，把两个
  `FolderList` 当成单个 `Folder` 处理，访问 `.id` 必然抛
  `AttributeError`；改为只递归 `folder_list`。
- `clean_ghost_folders` 返回值类型标注从 `-> None` 改为 `-> int`，与实际
  返回 `LanZouCloud.SUCCESS`/`FAILED` 状态码的行为一致。
- `browser_cookie3.py` 修复 `logger.info("Loaded %d cookies", ...)` 的
  `%d` 占位符问题：该文件用的是 `farlog.getLogger`（loguru 封装），
  `%`/`%s` 风格不会被插值，位置参数会被静默丢弃；改为 loguru 的 `{}`
  占位符写法。
- `api/utils.py`、`api/extra.py`、`login_assister.py` 中若干 `except
  Exception` 收窄为具体异常类型（`requests.RequestException`、
  `pickle.UnpicklingError` 等 pickle 相关异常、`RuntimeError`/`TypeError`/
  `ValueError`、`OSError`/`UnicodeEncodeError`），避免掩盖非预期错误。
- `api/utils.py` 的 typing 写法从 `Tuple`/`Union` 迁移到 Python 3.10
  原生的 `tuple[...]`/`X | Y`。
- `api/parser.py`、`api/utils.py`（`convert_file_size_to_str`、
  `calc_acw_sc__v2`、`un_serialize`）补充中文 docstring。
- `pyproject.toml` 新增 `[project.scripts]` 后，README 安装命令从
  `uv tool install funlanzou`（库场景无法提供可执行命令）改为库安装
  `uv pip install funlanzou`/`pip install funlanzou`，GUI 场景改为
  `uv tool install 'funlanzou[gui]'` + `funlanzou-gui` 命令。

### 变更

- `funlanzou/api/core.py`、`funlanzou/api/parser.py` 中若干仅用于调试、且被
  错误标为 `ERROR` 级别的状态日志（域名可用性检测、`sign` 解析结果等）降级为
  `DEBUG`。

### 废弃

- `LanZouCloud.login`（账号密码登录）：官方登录页改版后对多数新账号已失效，
  调用时现在会发出 `DeprecationWarning`，请改用 `login_by_cookie()`
  （配合 `funlanzou.login_assister` 或浏览器 Cookie 导出获取 Cookie）。计划
  在下一次破坏性版本中移除。
- `lanzou` 兼容层的废弃状态延续自 0.2.0，见下。

## [0.2.0] - 2026-08-28

### 新增

- 无。

### 修复

- 无。

### 变更

- 包内导入路径从 `lanzou` 统一改为 `funlanzou`，与仓库名、PyPI 发布名（一直都是
  `funlanzou`）保持一致。**破坏性变更**：请把代码里的 `import lanzou` /
  `from lanzou...` 换成 `import funlanzou` / `from funlanzou...`。

### 废弃

- 保留了 `lanzou` 兼容层（`lanzou/__init__.py`，仅一个文件）：`import lanzou`
  仍然可用，会转发到 `funlanzou` 并抛出 `DeprecationWarning`。计划在下一次破坏性
  版本中删除这个兼容层。
