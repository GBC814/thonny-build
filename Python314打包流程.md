# Thonny 3.14.2 (Python 3.14) 打包流程

## 1. 编译启动器 (必须手动执行一次)

由于 Python 解释器版本从 3.10 升级到 3.14，必须重新生成启动器执行文件：

1. 使用 **Visual Studio** 打开：`D:\thonny-4.1.8\packaging\windows\ThonnyRunner314\ThonnyRunner.sln`
2. 在上方工具栏（或者菜单栏下方）的下拉框中：
    *   左边的下拉框（配置）选择：**Release**
    *   右边的下拉框（平台）选择：**x64**
3. 点击顶部菜单：**生成** -> **重新生成解决方案**
4. 确认生成成功：`D:\thonny-4.1.8\packaging\windows\ThonnyRunner314\x64\Release\thonny.exe`

## 2. 卸载第三方库

在 D 盘下地址栏输入 `PowerShell`，执行以下命令：

```powershell
D:\Python314\python.exe D:\卸载python第三方库\xiezai-python3.14.2.py
```

## 3. 创建并激活虚拟环境

使用新的 Python 3.14 解释器创建环境：

```powershell
D:\Python314\python.exe -m venv .venv
.venv\Scripts\activate
```

## 4. 执行打包脚本

进入打包目录并运行：

```powershell
cd D:\thonny-4.1.8\packaging\windows
.\create_installer_314.bat
```

## 5. 说明

*   **Python 版本**：当前已配置为使用 `D:\Python314`。
*   **依赖优化**：为了兼容 Python 3.14，已在 `requirements-xxl-bundle.txt` 中移除了版本限制，并暂时注释了尚未支持 3.14 的库（pygame, odfpy 等）。
*   **故障排除**：如果打开 thonny.exe 提示找不到 `python310.dll`，说明第 1 步的编译没有成功或没有执行。
