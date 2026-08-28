"""兼容层：`import lanzou` 已废弃，请改用 `import funlanzou`。

PyPI 发行名一直是 `funlanzou`，但包内导入名过去一直是 `lanzou`——这里把它们
统一成 `funlanzou`。已经 `pip install funlanzou` 的用户下次升级时，旧代码
里的 `import lanzou` 不应该直接 ModuleNotFoundError，所以保留这一层转发。
下一次破坏性版本会把这个目录整个删掉。
"""

import sys
import warnings

import funlanzou

warnings.warn(
    "`import lanzou` 已废弃，请改用 `import funlanzou`。"
    "这个兼容层会在未来某个版本被移除。",
    DeprecationWarning,
    stacklevel=2,
)

sys.modules[__name__] = funlanzou
