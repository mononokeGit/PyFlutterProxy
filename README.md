# PyFlutterProxy说明文档
一个用于自动配置 Flutter 项目代理的 Python 脚本

## 简介

`setup_flutter_proxy.py` 是一个用于自动配置 Flutter 项目代理的 Python 脚本，支持将 Android 构建依赖源切换为阿里云 Maven，并将 Gradle 分发包下载源切换为腾讯云镜像，提升国内开发环境下的依赖下载速度。

## 使用方法

### 1. 直接运行可执行文件（推荐）

无需安装 Python 环境，直接双击或命令行运行：

```shell
./setup_flutter_proxy.dist/setup_flutter_proxy.exe
```

### 2. 使用 Python 脚本运行

如需自定义或调试，可在已安装 `requests` 和 `tqdm` 的 Python 3.8+ 环境下运行：

```shell
python setup_flutter_proxy.py
```

## 功能说明
- 自动修改 `android/build.gradle.kts`，添加阿里云 Maven 仓库
- 自动修改 `android/settings.gradle.kts`，添加阿里云 Maven 仓库（如有）
- 自动修改 `android/gradle/wrapper/gradle-wrapper.properties`，将 Gradle 分发包下载源切换为腾讯云镜像，并将其本地缓存
- 下载 Gradle 分发包时显示进度条

## 注意事项
- 请在 Flutter 项目根目录下运行本工具
- 若需重新打包可执行文件，请确保已安装 Nuitka，并在 Anaconda/虚拟环境下执行：
  ```shell
  nuitka --standalone --show-progress --output-dir=setup_flutter_proxy.dist setup_flutter_proxy.py
  ```
- 若遇到权限或依赖问题，请以管理员身份运行或检查 Python 依赖

## 目录结构
```
pyflutter/
├── setup_flutter_proxy.py
├── setup_flutter_proxy.dist/
│   ├── setup_flutter_proxy.exe
│   └── ...（依赖文件）
└── nuitka-crash-report.xml（如有）
```

## 联系方式
如有问题或建议，欢迎提交 issue。
