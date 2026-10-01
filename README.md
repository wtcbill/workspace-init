# workspace-init

用一句“初始化一下工作区”，为当前项目建立规则文件，并读取已有工作状态。

## 工作流程

1. 确认当前工作区根目录，尝试读取已有 `AGENTS.md`。
2. 规则文件缺失时，从内置模板生成 `AGENTS.md` 和 `工作须知.md`，自动填入当前根目录。
3. 完整读取最终规则；存在 `交接文档.md` 时一并读取，接续当前状态。

已有文件保留原样。重复执行不会覆盖用户修改，也不会自动创建空白交接文档或项目日志。

模板随 skill 保存，初始化过程无需联网。辅助脚本只依赖 Python 标准库；没有 Python 时，Codex 可使用现有文件工具完成同样操作。

## 安装

在支持个人本地 skill 的 Codex 环境中，可以提出：

```text
使用 $skill-installer 安装 https://github.com/wtcbill/workspace-init。
skill 位于仓库根目录，请命名为 workspace-init。
```

也可以将本仓库复制到个人技能目录下的 `workspace-init` 文件夹，确保 `SKILL.md` 位于该文件夹的根目录。

如果安装后未出现在技能列表中，重启宿主后再检查。

## 使用

在目标工作区打开对话，然后说：

```text
初始化一下工作区
```

也可显式调用：

```text
用 $workspace-init 初始化当前工作区
```

自然语言选用由宿主根据 skill 描述匹配。此 skill 不注册会话启动钩子，不修改全局配置。

## 单独运行脚本

脚本负责创建缺失文件。运行后仍需让 Codex 读取规则和已有交接文档，才完成会话初始化。

Windows PowerShell 示例：

```powershell
python -B -X utf8 .\scripts\init_workspace.py --root 'D:\Projects\My Project'
```

仅预览将创建或保留的文件：

```powershell
python -B -X utf8 .\scripts\init_workspace.py --root 'D:\Projects\My Project' --dry-run
```

目标目录必须已存在，并使用绝对路径。脚本兼容已有 `agents.md` 等大小写变体；遇到冲突、同名目录或模板问题时返回错误。

## 文件结构

```text
SKILL.md
agents/openai.yaml
assets/AGENTS.md
assets/工作须知.md
scripts/init_workspace.py
```

调整标准规则时，修改 `assets` 中的模板，并保留 `{{WORKSPACE_ROOT}}` 占位符。修改模板只影响今后生成的文件，已有工作区文档需另行维护。
