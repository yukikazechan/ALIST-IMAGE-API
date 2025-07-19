# Alist 图片 API

这是一个包含前端和后端的图片管理服务。

## 功能

- 用户认证
- 图片上传和管理
- 图片标签和搜索
- 用于访问图片的 API 密钥管理

## 系统要求

- Python 3
- Node.js 和 npm

## 安装与启动

直接运行安装脚本即可。脚本会自动安装所有依赖项，并启动应用程序。
-   **Windows 用户**: 运行 `install.bat`。
-   **Linux 和 macOS 用户**: 首先运行 `chmod +x install.sh` 赋予脚本执行权限，然后运行 `./install.sh`。

安装完成后，应用程序将在默认端口 `5235` 上运行。请在浏览器中打开 `http://localhost:5235` 来访问它。

## API 使用说明

您可以通过以下格式的 API 地址来获取一张随机图片。该 API 会作为代理直接返回图片，可用于 `<img>` 标签。

**API 地址:**
`http://localhost:5235/api/v1/random/YOUR_API_KEY`

请将 `YOUR_API_KEY` 替换为您在“API 密钥管理”页面生成的密钥。

## 如何修改端口

如果您需要修改应用程序的端口，请按照以下步骤操作：

1.  **复制配置文件**: 在项目根目录下，找到名为 `.env.example` 的文件，复制并重命名为 `.env`。
2.  **修改后端端口**: 打开 `.env` 文件，您会看到 `BACKEND_PORT=5235`。将 `5235` 修改为您想要的任何端口号。
3.  **修改前端 API 地址**:
    -   打开文件: `frontend/src/services/api.js`。
    -   找到这一行: `baseURL: 'http://localhost:5235/api',`
    -   将 `5235` 修改为您在第 2 步中设置的新端口号。
4.  **重新启动**: 修改完毕后，重新运行安装脚本或直接运行 `python3 -m backend.app.main` 来启动应用。

## 默认管理员凭据

-   **用户名:** admin
-   **密码:** admin

---

## Linux 环境故障排除

如果您在运行 `install.sh` 时遇到关于 Python 或虚拟环境 (venv) 的错误，特别是提示 "Failed to create Python virtual environment"，这通常意味着您系统中的 Python 安装不完整或存在问题。

以下是在 Debian/Ubuntu 系统上进行修复的推荐步骤：

**1. 清理旧的/损坏的 Python 版本 (可选，但推荐)**

如果您不确定当前的 Python 安装状态，最好先清理它。请谨慎操作，确保不会移除系统关键的 Python 版本。

```bash
# 查找所有已安装的 python3 版本
dpkg -l | grep python3

# 卸载特定的版本，例如 python3.10
sudo apt-get purge python3.10
sudo apt-get autoremove
```

**2. 安装一个干净、完整的 Python 环境**

我们推荐安装 Python 3.10，这是一个稳定且兼容性好的版本。

```bash
sudo apt-get update
# 安装 python3.10 本体, venv 支持, pip, 以及 C 语言编译所需的 dev 包
sudo apt-get install -y python3.10 python3.10-venv python3-pip python3.10-dev
```

**3. 配置默认 Python 版本 (重要)**

使用 `update-alternatives` 来管理系统中的多个 Python 版本，并设置 `python3` 命令的默认指向。

```bash
# 将 python3.10 添加到 alternatives 系统
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# (可选) 如果您有其他版本，可以用此命令在它们之间切换
sudo update-alternatives --config python3
```

**4. 验证安装**

检查 Python 和 pip 的版本，确保它们都指向新安装的版本。

```bash
python3 --version
# 应该输出: Python 3.10.x

pip3 --version
# 应该指向 python 3.10 的 site-packages
```

完成以上步骤后，您的 Linux 系统应该有了一个干净、完整的 Python 环境。现在，您可以回到项目根目录，重新运行 `bash install.sh`，安装过程应该可以顺利完成了。

#### Git 拉取失败 (dubious ownership)

当您以 `root` 用户身份在属于其他用户（例如 `myuser`）的目录中执行 `git pull` 时，可能会遇到 `fatal: detected dubious ownership in repository` 错误。这是 Git 的一项安全措施。

**解决方案：**

*   **(推荐)** 切换到目录的所有者用户再执行 `git pull`：
    ```bash
    # 将 myuser 替换为实际的用户名
    sudo -iu myuser
    cd /path/to/your/project
    git pull
    ```
*   **(快速修复)** 或者，将该目录对 `root` 用户标记为安全：
    ```bash
    # 将 /path/to/your/project 替换为实际的项目路径
    git config --global --add safe.directory /path/to/your/project
    # 然后再以 root 身份执行 git pull
    ```

---

## 设置开机自启动 (Linux with systemd)

在您成功运行 `install.sh` 并确保应用可以启动后，如果您希望应用在服务器开机时自动在后台运行，可以运行 `setup_service.sh` 脚本。

**重要**: 请确保您是在项目的主目录 (即 `ALIST-IMAGE-API` 目录) 中运行此脚本。

```bash
sudo bash setup_service.sh
```

该脚本会自动：
1.  根据当前路径和用户，生成一个 `systemd` 服务文件。
2.  将服务文件安装到系统中。
3.  启动服务，并设置其为开机自启动。

**服务管理命令:**
-   检查服务状态: `sudo systemctl status alist-image-api.service`
-   停止服务: `sudo systemctl stop alist-image-api.service`
-   启动服务: `sudo systemctl start alist-image-api.service`
-   查看实时日志: `sudo journalctl -u alist-image-api.service -f`