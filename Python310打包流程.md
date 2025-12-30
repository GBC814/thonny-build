# Thonny 3.10.11 (Python 3.10) 打包流程

## 1. 恢复启动器 (如果曾修改过)

确保使用的是原有的 ThonnyRunner310：
1. 确认 `D:\thonny-4.1.8\packaging\windows\ThonnyRunner310\x64\Release\thonny.exe` 文件存在。
2. 该文件应为 Python 3.10 版本。

## 2. 卸载第三方库

在 D 盘下地址栏输入 `PowerShell`，执行以下命令：

```powershell
D:\Python310\python.exe D:\卸载python第三方库\xiezai.py
```

## 3. 创建并激活虚拟环境

使用 Python 3.10 解释器创建环境：

```powershell
D:\Python310\python.exe -m venv .venv
.venv\Scripts\activate
```

## 4. 执行打包脚本

进入打包目录并运行：

```powershell
cd D:\thonny-4.1.8\packaging\windows
.\create_installer_310.bat
```

## 5. 说明

*   **Python 版本**：当前已配置为使用 `D:\Python310`。
*   **依赖恢复**：已将 `requirements-xxl-bundle.txt` 恢复为 Python 3.10 兼容的版本（带版本锁定）。
*   **启动器**：脚本已改回调用 `ThonnyRunner310` 编译出的执行文件。
