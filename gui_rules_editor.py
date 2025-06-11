# gui_rules_editor.py (V2.5 "防弹"容错版)
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class RulesEditor(tk.Toplevel):
    def __init__(self, parent, rules_dict):
        super().__init__(parent)
        self.title("规则编辑器")
        self.geometry("600x400")

        self.rules = rules_dict
        self.parent = parent

        self.create_widgets()
        self.load_rules_to_tree()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # ... (这部分代码无变化) ...
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=("mime", "folder"), show="headings")
        self.tree.heading("mime", text="文件类型 (MIME Type)")
        self.tree.heading("folder", text="目标文件夹")
        self.tree.column("mime", width=250)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.edit_rule)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="添加规则", command=self.add_rule).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="修改规则", command=self.edit_rule).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除规则", command=self.delete_rule).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存并关闭", command=self.on_closing).pack(side=tk.RIGHT, padx=5)

    def load_rules_to_tree(self):
        # ... (无变化) ...
        for item in self.tree.get_children():
            self.tree.delete(item)
        for mime, folder in self.rules.items():
            self.tree.insert("", tk.END, values=(mime, folder))

    def add_rule(self):
        # ... (无变化) ...
        mime = simpledialog.askstring("添加规则", "请输入文件类型 (MIME Type):", parent=self)
        if mime:
            folder = simpledialog.askstring("添加规则", f"为 {mime} 设置目标文件夹:", parent=self)
            if folder:
                self.rules[mime] = folder
                self.load_rules_to_tree()

    # --- !!! 核心升级点：为edit_rule函数穿上“防弹衣” !!! ---
    def edit_rule(self, event=None):
        selected_item = self.tree.focus()
        if not selected_item:
            return

        try:
            # 我们将可能出错的代码块放进 try...except 中
            item_values = self.tree.item(selected_item, "values")

            # 如果item_values不是一个包含两个元素的元组，就会在这里出错
            # 比如双击了标题栏，item_values会是'' (空字符串)
            if not isinstance(item_values, tuple) or len(item_values) != 2:
                return  # 静默返回，不处理这种点击

            old_mime, old_folder = item_values

            new_folder = simpledialog.askstring("修改规则", f"为 {old_mime} 修改目标文件夹:", initialvalue=old_folder,
                                                parent=self)
            if new_folder and new_folder != old_folder:
                self.rules[old_mime] = new_folder
                self.load_rules_to_tree()

        except (ValueError, TypeError):
            # 捕获可能发生的 ValueError (解包失败) 或 TypeError
            # 这样即使发生意外，程序也不会崩溃，而是静默地忽略这个无效操作
            pass

    def delete_rule(self):
        # ... (为delete_rule也加上同样的保护) ...
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("操作无效", "请先选择一条要删除的规则。", parent=self)
            return

        try:
            item_values = self.tree.item(selected_item, "values")
            if not isinstance(item_values, tuple) or len(item_values) != 2:
                return

            mime_to_delete = item_values[0]
            if messagebox.askyesno("确认删除", f"确定要删除关于 {mime_to_delete} 的规则吗？", parent=self):
                del self.rules[mime_to_delete]
                self.load_rules_to_tree()
        except (ValueError, TypeError):
            pass

    def on_closing(self):
        # ... (无变化) ...
        self.parent.update_rules(self.rules)
        self.destroy()