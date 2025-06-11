# File-Sorter-GG
A smart file organizer application that sorts files by type or date, with a watcher service for automation.


---

### For macOS & Linux Users (Running from Source)

Since the executable file (.exe) is for Windows only, users on macOS and Linux can run this application directly from the source code.

**Prerequisites:**
*   You need to have Python 3.8+ installed on your system.

**Instructions:**

1.  **Download the Source Code:**
    *   Click the green `<> Code` button on the main repository page and select `Download ZIP`.
    *   Unzip the downloaded file (`File-Sorter-GG-main.zip`).

2.  **Open the Terminal:**
    *   Navigate into the unzipped project folder using the `cd` command. For example: `cd ~/Downloads/File-Sorter-GG-main`

3.  **Install Dependencies:**
    *   Run the following command in your terminal to install all the necessary libraries:
    ```bash
    pip install pillow watchdog pystray python-magic-bin
    ```

4.  **Run the Application:**
    *   Execute the main script with this command:
    ```bash
    python3 main_app.py
    ```
The application window should now appear on your screen.

---

### 致 macOS 与 Linux 用户 (从源代码运行)

由于 .exe 可执行文件仅适用于Windows，macOS和Linux用户可以从源代码直接运行本程序。

**先决条件:**
*   您的系统中需要安装 Python 3.8 或更高版本。

**操作指南:**

1.  **下载源代码:**
    *   在项目主页，点击绿色的 `<> Code` 按钮，然后选择 `Download ZIP`。
    *   解压缩下载的 `File-Sorter-GG-main.zip` 文件。

2.  **打开终端 (Terminal):**
    *   使用 `cd` 命令进入解压后的项目文件夹。例如: `cd ~/Downloads/File-Sorter-GG-main`

3.  **安装依赖库:**
    *   在您的终端中，运行以下命令以安装所有必需的库:
    ```bash
    pip install pillow watchdog pystray python-magic-bin
    ```

4.  **运行程序:**
    *   执行以下命令来启动主程序:
    ```bash
    python3 main_app.py
    ```
现在，应用程序的窗口应该会出现在您的屏幕上。
