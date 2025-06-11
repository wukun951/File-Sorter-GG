# custom_widgets.py (V2.6.1 - 稳定版)
import tkinter as tk


class Toast(tk.Toplevel):
    """
    更稳定、更简洁的Toast提示框。
    放弃了复杂的淡入效果，确保显示成功。
    """

    def __init__(self, parent, message, duration=2500, bg="#333333", fg="white", alpha=0.9):
        super().__init__(parent)

        # 移除窗口边框
        self.overrideredirect(True)

        # 直接设置最终的透明度
        self.attributes("-alpha", alpha)

        # 设置窗口在最顶层，确保不被其他窗口遮挡
        self.attributes("-topmost", True)

        # 创建显示消息的Label
        label = tk.Label(self, text=message, bg=bg, fg=fg, padx=20, pady=10, font=("微软雅黑", 10))
        label.pack()

        # --- 重新计算位置 ---
        # 我们需要在主事件循环中安排位置计算，以确保父窗口信息是最终的
        self.parent = parent
        self.parent.update_idletasks()

        # 使用 after(0, ...) 确保在下一个事件循环中执行，此时所有窗口尺寸都是准确的
        self.after(0, self.center_on_parent)

        # 安排自动销毁任务
        self.after(duration, self.fade_out)

    def center_on_parent(self):
        """将Toast窗口在父窗口中居中"""
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        self.update_idletasks()  # 确保Toast自身尺寸已更新
        toast_width = self.winfo_width()
        toast_height = self.winfo_height()

        x = parent_x + (parent_width // 2) - (toast_width // 2)
        y = parent_y + (parent_height // 2) - (toast_height // 2)

        self.geometry(f"+{x}+{y}")

    def fade_out(self):
        """淡出效果"""
        current_alpha = self.attributes('-alpha')
        if current_alpha > 0.0:
            new_alpha = max(current_alpha - 0.1, 0.0)  # 确保alpha不会小于0
            self.attributes('-alpha', new_alpha)
            self.after(50, self.fade_out)  # 淡出速度可以慢一点
        else:
            self.destroy()