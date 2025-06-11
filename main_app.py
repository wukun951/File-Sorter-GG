# main_app.py (V4.0 - 智能管家 终极完整版)

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys
from PIL import Image, ImageDraw
from pystray import MenuItem as item, Icon

# 导入我们的自定义模块
from config_manager import load_config, save_config
from core_logic import sort_files_logic, analyze_files
from custom_widgets import Toast
from gui_rules_editor import RulesEditor
from watcher_service import WatcherService


class Application(tk.Tk):
    # 在 main_app.py 中，替换 __init__ 和 create_widgets 这两个函数

    def __init__(self):
        super().__init__()
        self.title("文件‘归归’整理器 V4.2 - 完美布局")  # 版本号升级！

        # --- 初始化所有变量 (无变化) ---
        self.config = load_config()
        self.rules = self.config.get('rules', {})
        self.watcher_service = None
        self.tray_icon = None
        self.sorting_thread = None
        self.is_paused = False
        self.cancel_flag = [False]
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.source_path = tk.StringVar(value=self.config['settings'].get('last_source_dir', ''))
        self.dest_path = tk.StringVar(value=self.config['settings'].get('last_dest_dir', ''))
        self.copy_mode_var = tk.BooleanVar(value=False)
        self.sort_mode_var = tk.StringVar(value='type')

        # --- 创建并打包所有组件 ---
        self.main_frame = self.create_widgets()  # create_widgets现在会返回主框架

        # --- !!! 核心升级点：强制自适应高度 !!! ---
        # 1. 强制Tkinter完成所有内部布局的计算
        self.update_idletasks()

        # 2. 获取能容纳所有内容的最小需要高度
        #    我们加上一点额外的padding（比如30像素）让它更宽松
        required_height = self.main_frame.winfo_reqheight() + 30

        # 3. 根据计算出的高度，重新设置窗口的几何尺寸
        self.geometry(f"600x{required_height}")
        self.minsize(600, required_height)  # 设置最小尺寸，防止用户拖拽得太小

        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ... (以下所有UI组件的创建和打包代码，与我们V4.1版本完全一致) ...
        # (为了简洁，这里省略，请保留您V4.1中的这部分代码，它不需要任何修改)
        source_frame = ttk.LabelFrame(main_frame, text=" 1. 源文件夹")
        source_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Entry(source_frame, textvariable=self.source_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5,
                                                                    pady=5)
        ttk.Button(source_frame, text="浏览...", command=self.select_source_folder).pack(side=tk.RIGHT, padx=5)
        dest_frame = ttk.LabelFrame(main_frame, text=" 2. 目标文件夹")
        dest_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Entry(dest_frame, textvariable=self.dest_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        ttk.Button(dest_frame, text="浏览...", command=self.select_dest_folder).pack(side=tk.RIGHT, padx=5)
        mode_frame = ttk.LabelFrame(main_frame, text=" 3. 整理模式")
        mode_frame.pack(fill=tk.X, padx=5, pady=10)
        ttk.Radiobutton(mode_frame, text="按文件类型整理 (使用规则编辑器)", variable=self.sort_mode_var,
                        value='type').pack(anchor=tk.W, padx=5)
        ttk.Radiobutton(mode_frame, text="按文件创建日期整理 (格式: 年/月)", variable=self.sort_mode_var,
                        value='creation_date').pack(anchor=tk.W, padx=5)
        ttk.Radiobutton(mode_frame, text="按照片拍摄日期整理 (格式: 年/月, 非照片则按创建日期)",
                        variable=self.sort_mode_var, value='taken_date').pack(anchor=tk.W, padx=5)
        options_frame = ttk.LabelFrame(main_frame, text=" 4. 其它选项")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Checkbutton(options_frame, text="使用“复制”模式 (保留源文件)", variable=self.copy_mode_var).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(options_frame, text="规则管理...", command=self.open_rules_editor).pack(side=tk.RIGHT, padx=5)
        watcher_frame = ttk.LabelFrame(main_frame, text=" 5. 自动化监视模式 (Beta)")
        watcher_frame.pack(fill=tk.X, padx=5, pady=10)
        self.watcher_toggle_button = ttk.Button(watcher_frame, text="启动后台监视", command=self.toggle_watcher)
        self.watcher_toggle_button.pack(fill=tk.X, padx=5, pady=5)
        watcher_info = "说明：启动后，将持续监视“源文件夹”，一旦有新文件被创建，将自动按当前设置进行整理。程序可最小化到托盘。"
        ttk.Label(watcher_frame, text=watcher_info, wraplength=550, justify=tk.LEFT).pack(padx=5, pady=5)
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        self.start_button = ttk.Button(action_frame, text="仅手动整理一次", command=self.start_sorting_with_preview)
        self.start_button.pack(fill=tk.X, pady=2)
        self.pause_button = ttk.Button(action_frame, text="暂停", state="disabled", command=self.toggle_pause)
        self.pause_button.pack(fill=tk.X, pady=2)
        self.cancel_button = ttk.Button(action_frame, text="取消", state="disabled", command=self.cancel_sorting)
        self.cancel_button.pack(fill=tk.X, pady=2)
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X)
        self.status_label = ttk.Label(progress_frame, text="准备就绪。", anchor="w")
        self.status_label.pack(fill=tk.X, pady=(5, 0))

        return main_frame  # 将主框架返回

    def start_sorting_with_preview(self):
        source_dir = self.source_path.get()
        if not source_dir or not self.dest_path.get():
            messagebox.showwarning("操作无效", "请务必选择源文件夹和目标文件夹！")
            return
        if source_dir == self.dest_path.get():
            messagebox.showwarning("操作无效", "源文件夹和目标文件夹不能是同一个！")
            return

        self.update_status("正在分析文件夹，请稍候...")
        threading.Thread(target=self.run_analysis, daemon=True).start()

    def run_analysis(self):
        source_dir = self.source_path.get()
        sort_mode = self.sort_mode_var.get()
        analysis_result = analyze_files(source_dir, self.rules, sort_mode)
        self.after(0, self.show_preview_results, analysis_result)

    def show_preview_results(self, analysis_result):
        if not analysis_result:
            messagebox.showerror("错误", "分析文件夹失败，请检查路径或文件权限。")
            self.update_status("准备就绪。")
            return
        if sum(analysis_result.values()) == 0:
            messagebox.showinfo("提示", "源文件夹中没有可供整理的文件。")
            self.update_status("准备就绪。")
            return

        action_name = "复制" if self.copy_mode_var.get() else "移动"
        sort_mode = self.sort_mode_var.get()
        preview_message = f"即将执行【{action_name}】操作：\n\n"
        if sort_mode == 'type':
            preview_message += "文件将被整理为以下类别：\n"
            for category, count in sorted(analysis_result.items()):
                preview_message += f"- {count} 个 {category}\n"
        else:
            file_count = analysis_result.get('个文件', 0)
            folder_count = analysis_result.get('个按日期命名的文件夹', 0)
            preview_message += f"共 {file_count} 个文件，将被整理到约 {folder_count} 个按日期命名的文件夹中。\n"
            preview_message += "（例如：2023/11_November）\n"
        preview_message += "\n是否继续？"

        if messagebox.askyesno("操作预览", preview_message):
            self.start_actual_sorting()
        else:
            self.update_status("操作已取消。")

    def start_actual_sorting(self, is_auto=False):
        self.cancel_flag[0] = False
        self.is_paused = False
        self.pause_event.set()

        params = {
            'source_dir': self.source_path.get(), 'dest_dir': self.dest_path.get(),
            'is_copy_mode': self.copy_mode_var.get(), 'rules': self.rules,
            'mode': self.sort_mode_var.get(), 'pause_event': self.pause_event,
            'cancel_flag': self.cancel_flag
        }
        callbacks = {
            'update_status': self.update_status, 'update_progress': self.update_progress,
            'on_complete': self.on_sorting_complete if not is_auto else self.on_auto_sorting_complete
        }

        if not is_auto:
            self.start_button.config(state="disabled");
            self.pause_button.config(state="normal");
            self.cancel_button.config(state="normal")
            self.progress['value'] = 0

        self.sorting_thread = threading.Thread(target=sort_files_logic, args=(params, callbacks), daemon=True)
        self.sorting_thread.start()

    def on_sorting_complete(self):
        self.start_button.config(state="normal");
        self.pause_button.config(state="disabled");
        self.cancel_button.config(state="disabled")

    def on_auto_sorting_complete(self):
        Toast(self, "后台自动整理完成！")

    def toggle_watcher(self):
        if self.watcher_service and self.watcher_service.observer.is_alive():
            self.watcher_service.stop()
            self.watcher_service = None
            self.watcher_toggle_button.config(text="启动后台监视")
            Toast(self, "后台监视已停止。")
        else:
            source_dir = self.source_path.get()
            if not source_dir or not os.path.isdir(source_dir):
                messagebox.showerror("错误", "请先选择一个有效的源文件夹以进行监视！")
                return
            self.watcher_service = WatcherService(source_dir, self.on_file_created)
            self.watcher_service.start()
            self.watcher_toggle_button.config(text="停止后台监视")
            Toast(self, f"已开始后台监视:\n{source_dir}")

    def on_file_created(self):
        self.after(2000, lambda: self.start_actual_sorting(is_auto=True))

    def create_tray_icon(self):
        width, height = 64, 64
        image = Image.new('RGB', (width, height), 'black')
        dc = ImageDraw.Draw(image)
        dc.text((10, 20), "GG", fill="white", font_size=24)  # '归归'

        menu = (item('显示主界面', self.show_window, default=True), item.SEPARATOR, item('退出程序', self.quit_app))
        self.tray_icon = Icon("文件归归整理器", image, "文件‘归归’整理器", menu)
        self.tray_icon.run_detached()

    def hide_to_tray(self):
        self.withdraw()
        if not self.tray_icon or not self.tray_icon.visible:
            self.create_tray_icon()
        Toast(self, "我还在后台默默工作哦！")

    def show_window(self):
        self.deiconify()
        self.focus_force()

    def quit_app(self):
        if self.watcher_service:
            self.watcher_service.stop()
        if self.tray_icon:
            self.tray_icon.stop()
        self.on_closing(force_quit=True)

    def on_closing(self, force_quit=False):
        self.config['settings']['last_source_dir'] = self.source_path.get()
        self.config['settings']['last_dest_dir'] = self.dest_path.get()
        save_config(self.config)
        if force_quit:
            self.destroy()

    def select_source_folder(self):
        folder_path = filedialog.askdirectory(initialdir=self.source_path.get())
        if folder_path: self.source_path.set(folder_path)

    def select_dest_folder(self):
        folder_path = filedialog.askdirectory(initialdir=self.dest_path.get())
        if folder_path: self.dest_path.set(folder_path)

    def open_rules_editor(self):
        if hasattr(self,
                   'rules_editor_window') and self.rules_editor_window and self.rules_editor_window.winfo_exists():
            self.rules_editor_window.focus()
        else:
            self.rules_editor_window = RulesEditor(self, self.rules.copy())

    def update_rules(self, new_rules):
        self.rules = new_rules
        self.config['rules'] = new_rules
        save_config(self.config)
        Toast(self, "分类规则已成功更新并保存！")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_event.clear();
            self.pause_button.config(text="继续");
            self.update_status("已暂停。")
        else:
            self.pause_event.set();
            self.pause_button.config(text="暂停")

    def cancel_sorting(self):
        if messagebox.askyesno("确认取消", "您确定要中途取消整理吗？"):
            self.cancel_flag[0] = True
            if self.is_paused: self.pause_event.set()

    def on_sorting_complete(self):
        self.start_button.config(state="normal");
        self.pause_button.config(state="disabled");
        self.cancel_button.config(state="disabled")

    def update_status(self, message):
        self.status_label.config(text=message)

    def update_progress(self, value):
        self.progress['value'] = value


if __name__ == "__main__":
    app = Application()
    app.mainloop()