# Changelog

## [0.2.0] - 2026-08-28

### Changed（破坏性变更）

- 包内导入路径从 `lanzou` 统一改为 `funlanzou`，与仓库名、PyPI 发布名（一直都是
  `funlanzou`）保持一致。
- 保留了 `lanzou` 兼容层（`lanzou/__init__.py`，仅一个文件）：`import lanzou`
  仍然可用，会转发到 `funlanzou` 并抛出 `DeprecationWarning`。计划在下一次破坏性
  版本中删除这个兼容层，请尽快把代码里的 `import lanzou` / `from lanzou...`
  换成 `import funlanzou` / `from funlanzou...`。

### Known issues（本次未处理，超出改名范围）

- `pyproject.toml` 的 `dependencies` 一直是空列表，但代码实际依赖 `requests`、
  `requests_toolbelt`、`PyQt5` 等——这是改名之前就存在的问题，不在本次范围内，
  留给仓库所有者后续补齐。
