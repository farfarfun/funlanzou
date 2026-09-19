# Changelog

## [未发布]

> 本节记录 issue #427 审计修复的改动，版本号与发布日期留给 `funbuild` 走正式
> 发布流程时填写，这里不手动递增版本号。

### 新增

- `pyproject.toml` 补齐运行时依赖声明（`farlog`、`funsecret`、`requests`、
  `requests-toolbelt`、`urllib3`），并新增 `gui` extra（`PyQt6`、
  `PyQt6-WebEngine`、`keyring`、`lz4`、`pycryptodomex`）隔离图形客户端依赖。
- 提交 `uv.lock`，保证可复现构建。
- README 补充安装/使用说明、第三方代码来源声明
  （`zaxtyson/LanZouCloud-API`、`borisbabic/browser_cookie3`，均为 MIT）及组织
  介绍区块。

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

### 变更

- `funlanzou/api/core.py`、`funlanzou/api/parser.py` 中若干仅用于调试、且被
  错误标为 `ERROR` 级别的状态日志（域名可用性检测、`sign` 解析结果等）降级为
  `DEBUG`。

### 废弃

- 无新增废弃项（`lanzou` 兼容层的废弃状态延续自 0.2.0，见下）。

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
