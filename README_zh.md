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

## 如何修改端口

如果您需要修改应用程序的端口，请按照以下步骤操作：

1.  **复制配置文件**: 在 `dist_package` 目录下，找到名为 `.env.example` 的文件，复制并重命名为 `.env`。
2.  **修改后端端口**: 打开 `.env` 文件，您会看到 `BACKEND_PORT=5235`。将 `5235` 修改为您想要的任何端口号。
3.  **修改前端 API 地址**:
    -   打开文件: `frontend/src/services/api.js`。
    -   找到这一行: `baseURL: 'http://localhost:5235/api',`
    -   将 `5235` 修改为您在第 2 步中设置的新端口号。
4.  **重新启动**: 修改完毕后，重新运行安装脚本或直接运行 `python backend/app/main.py` 来启动应用。

## 默认管理员凭据

-   **用户名:** admin
-   **密码:** admin