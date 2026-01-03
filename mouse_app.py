import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import pyautogui
import json
import os

class MouseTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("鼠标操作工具")
        
        # 运行状态
        self.running = False
        self.count = 0
        
        # 默认设置
        self.settings = {
            "start_hotkey": "F1",
            "stop_hotkey": "F2",
            "operation_type": "left",  # left, right, middle, scroll
            "scroll_direction": "up",  # up, down
            "scroll_speed": 100,
            "click_interval": 2,
            "scroll_interval": 2
        }
        
        # 加载保存的设置
        self.load_settings()
        
        # 创建带滚动条的界面
        self.setup_scrollable_ui()
        
        # 绑定快捷键
        self.bind_hotkeys()
        
    def load_settings(self):
        """加载保存的设置"""
        if os.path.exists("mouse_settings.json"):
            try:
                with open("mouse_settings.json", "r", encoding="utf-8") as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
            except:
                pass
    
    def save_settings(self):
        """保存设置到文件"""
        try:
            with open("mouse_settings.json", "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def setup_scrollable_ui(self):
        # 创建主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)
        
        # 创建画布和滚动条
        self.canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        
        # 滚动区域框架
        self.scrollable_frame = tk.Frame(self.canvas)
        
        # 配置滚动区域
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # 将滚动区域框架添加到画布
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # 打包画布和滚动条
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮滚动
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # 创建UI内容
        self.create_ui_content()
        
        # 设置窗口最小大小
        self.root.minsize(500, 600)
    
    def _on_mousewheel(self, event):
        """处理鼠标滚轮滚动"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def create_ui_content(self):
        # 标题
        title_label = tk.Label(self.scrollable_frame, text="鼠标操作工具", 
                              font=("微软雅黑", 18, "bold"))
        title_label.pack(pady=20)
        
        # === 鼠标操作类型设置 ===
        type_frame = tk.LabelFrame(self.scrollable_frame, text="鼠标操作类型", 
                                  font=("微软雅黑", 11, "bold"),
                                  padx=15, pady=10)
        type_frame.pack(fill="x", pady=(0, 15), padx=10)
        
        # 操作类型变量
        self.operation_type = tk.StringVar(value=self.settings["operation_type"])
        
        # 点击操作类型选择
        tk.Label(type_frame, text="点击操作:", font=("微软雅黑", 10)).pack(anchor="w", pady=5)
        
        click_frame = tk.Frame(type_frame)
        click_frame.pack(anchor="w", padx=20)
        
        tk.Radiobutton(click_frame, text="左键点击", 
                      variable=self.operation_type, value="left",
                      font=("微软雅黑", 10), command=self.update_settings_display).pack(side="left", padx=5)
        
        tk.Radiobutton(click_frame, text="右键点击", 
                      variable=self.operation_type, value="right",
                      font=("微软雅黑", 10), command=self.update_settings_display).pack(side="left", padx=5)
        
        tk.Radiobutton(click_frame, text="中键点击", 
                      variable=self.operation_type, value="middle",
                      font=("微软雅黑", 10), command=self.update_settings_display).pack(side="left", padx=5)
        
        # 滚动操作类型选择
        tk.Label(type_frame, text="滚动操作:", font=("微软雅黑", 10)).pack(anchor="w", pady=(10, 5))
        
        scroll_frame = tk.Frame(type_frame)
        scroll_frame.pack(anchor="w", padx=20)
        
        tk.Radiobutton(scroll_frame, text="滚轮滚动", 
                      variable=self.operation_type, value="scroll",
                      font=("微软雅黑", 10), command=self.update_settings_display).pack(side="left", padx=5)
        
        # === 动态设置区域 ===
        self.settings_frame = tk.LabelFrame(self.scrollable_frame, text="操作设置", 
                                          font=("微软雅黑", 11, "bold"),
                                          padx=15, pady=10)
        self.settings_frame.pack(fill="x", pady=(0, 15), padx=10)
        
        # === 点击频率设置 ===
        self.click_settings_frame = tk.Frame(self.settings_frame)
        
        tk.Label(self.click_settings_frame, text="点击频率:", 
                font=("微软雅黑", 10)).pack(side="left")
        
        self.click_interval = tk.StringVar(value=str(self.settings["click_interval"]))
        self.click_interval_entry = tk.Entry(self.click_settings_frame, 
                                           textvariable=self.click_interval,
                                           width=8, font=("微软雅黑", 10), justify="center")
        self.click_interval_entry.pack(side="left", padx=5)
        
        tk.Label(self.click_settings_frame, text="秒/次", 
                font=("微软雅黑", 10)).pack(side="left")
        
        # === 滚动设置 ===
        self.scroll_settings_frame = tk.Frame(self.settings_frame)
        
        # 滚动方向
        scroll_dir_frame = tk.Frame(self.scroll_settings_frame)
        scroll_dir_frame.pack(anchor="w", pady=(0, 10))
        
        tk.Label(scroll_dir_frame, text="滚动方向:", 
                font=("微软雅黑", 10)).pack(side="left")
        
        self.scroll_direction = tk.StringVar(value=self.settings["scroll_direction"])
        
        tk.Radiobutton(scroll_dir_frame, text="向上", 
                      variable=self.scroll_direction, value="up",
                      font=("微软雅黑", 10)).pack(side="left", padx=5)
        
        tk.Radiobutton(scroll_dir_frame, text="向下", 
                      variable=self.scroll_direction, value="down",
                      font=("微软雅黑", 10)).pack(side="left", padx=5)
        
        # 滚动速率
        scroll_speed_frame = tk.Frame(self.scroll_settings_frame)
        scroll_speed_frame.pack(anchor="w", pady=(0, 10))
        
        tk.Label(scroll_speed_frame, text="滚动速率:", 
                font=("微软雅黑", 10)).pack(side="left")
        
        self.scroll_speed = tk.IntVar(value=self.settings["scroll_speed"])
        self.scroll_speed_entry = tk.Entry(scroll_speed_frame, 
                                         textvariable=self.scroll_speed,
                                         width=8, font=("微软雅黑", 10), justify="center")
        self.scroll_speed_entry.pack(side="left", padx=5)
        
        tk.Label(scroll_speed_frame, text="(数值越大滚动越快)", 
                font=("微软雅黑", 9), fg="#666").pack(side="left")
        
        # 滚动频率
        scroll_interval_frame = tk.Frame(self.scroll_settings_frame)
        scroll_interval_frame.pack(anchor="w")
        
        tk.Label(scroll_interval_frame, text="滚动频率:", 
                font=("微软雅黑", 10)).pack(side="left")
        
        self.scroll_interval = tk.StringVar(value=str(self.settings["scroll_interval"]))
        self.scroll_interval_entry = tk.Entry(scroll_interval_frame, 
                                            textvariable=self.scroll_interval,
                                            width=8, font=("微软雅黑", 10), justify="center")
        self.scroll_interval_entry.pack(side="left", padx=5)
        
        tk.Label(scroll_interval_frame, text="秒/次", 
                font=("微软雅黑", 10)).pack(side="left")
        
        # 初始显示正确的设置
        self.update_settings_display()
        
        # === 快捷键设置 ===
        hotkey_frame = tk.LabelFrame(self.scrollable_frame, text="快捷键设置", 
                                    font=("微软雅黑", 11, "bold"),
                                    padx=15, pady=10)
        hotkey_frame.pack(fill="x", pady=(0, 15), padx=10)
        
        # 开始快捷键
        tk.Label(hotkey_frame, text="开始快捷键:", 
                font=("微软雅黑", 10)).grid(row=0, column=0, sticky="w", pady=5)
        
        self.start_key = tk.StringVar(value=self.settings["start_hotkey"])
        start_entry = tk.Entry(hotkey_frame, textvariable=self.start_key,
                              width=10, font=("微软雅黑", 10), justify="center")
        start_entry.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # 停止快捷键
        tk.Label(hotkey_frame, text="停止快捷键:", 
                font=("微软雅黑", 10)).grid(row=1, column=0, sticky="w", pady=5)
        
        self.stop_key = tk.StringVar(value=self.settings["stop_hotkey"])
        stop_entry = tk.Entry(hotkey_frame, textvariable=self.stop_key,
                             width=10, font=("微软雅黑", 10), justify="center")
        stop_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # 应用设置按钮
        apply_btn = tk.Button(hotkey_frame, text="应用快捷键设置", 
                            command=self.apply_hotkeys,
                            font=("微软雅黑", 9))
        apply_btn.grid(row=0, column=2, rowspan=2, padx=(20, 0), pady=5)
        
        # === 控制按钮 ===
        control_frame = tk.Frame(self.scrollable_frame)
        control_frame.pack(pady=20)
        
        # 开始按钮
        self.start_btn = tk.Button(control_frame, text=f"开始 ({self.settings['start_hotkey']})", 
                                 command=self.start_action,
                                 font=("微软雅黑", 12, "bold"),
                                 width=12, height=2)
        self.start_btn.pack(side="left", padx=15)
        
        # 停止按钮
        self.stop_btn = tk.Button(control_frame, text=f"停止 ({self.settings['stop_hotkey']})", 
                                command=self.stop_action,
                                font=("微软雅黑", 12, "bold"),
                                width=12, height=2,
                                state="disabled")
        self.stop_btn.pack(side="left", padx=15)
        
        # === 状态显示 ===
        status_frame = tk.LabelFrame(self.scrollable_frame, text="状态信息", 
                                   font=("微软雅黑", 11, "bold"),
                                   padx=15, pady=10)
        status_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # 当前状态
        tk.Label(status_frame, text="当前状态:", 
                font=("微软雅黑", 10)).grid(row=0, column=0, sticky="w", pady=5)
        
        self.status_label = tk.Label(status_frame, text="准备就绪", 
                                   font=("微软雅黑", 10, "bold"), fg="#2980b9")
        self.status_label.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # 操作次数
        tk.Label(status_frame, text="操作次数:", 
                font=("微软雅黑", 10)).grid(row=1, column=0, sticky="w", pady=5)
        
        self.count_label = tk.Label(status_frame, text="0", 
                                  font=("微软雅黑", 10, "bold"), fg="#e67e22")
        self.count_label.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # 提示信息
        tk.Label(self.scrollable_frame, text="💡 提示：设置完成后点击'应用快捷键设置'，然后按相应快捷键控制", 
                font=("微软雅黑", 9), fg="#7f8c8d").pack(pady=10)
        
        # 保存设置按钮
        save_btn = tk.Button(self.scrollable_frame, text="保存所有设置", 
                           command=self.save_all_settings,
                           font=("微软雅黑", 10),
                           width=15, height=1)
        save_btn.pack(pady=10)
        
        # 退出按钮
        exit_btn = tk.Button(self.scrollable_frame, text="退出程序", 
                           command=self.on_closing,
                           font=("微软雅黑", 10),
                           width=15, height=1)
        exit_btn.pack(pady=(0, 20))
    
    def update_settings_display(self):
        """根据选择的鼠标操作类型更新设置显示"""
        # 清空当前设置区域
        for widget in self.settings_frame.winfo_children():
            widget.pack_forget()
        
        # 获取当前选择的鼠标操作类型
        operation = self.operation_type.get()
        
        # 更新设置显示
        if operation == "scroll":
            # 显示滚动设置
            self.scroll_settings_frame.pack(fill="x", anchor="w", pady=5)
            self.settings_frame.config(text="滚动设置")
        else:
            # 显示点击频率设置
            self.click_settings_frame.pack(fill="x", anchor="w", pady=5)
            
            # 根据点击类型更新标签
            if operation == "left":
                click_text = "左键点击设置"
            elif operation == "right":
                click_text = "右键点击设置"
            else:  # middle
                click_text = "中键点击设置"
            
            self.settings_frame.config(text=click_text)
    
    def bind_hotkeys(self):
        """绑定快捷键"""
        try:
            # 解绑之前的快捷键
            for key in ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"]:
                self.root.unbind(f"<{key}>")
            
            # 绑定新的快捷键
            self.root.bind(f"<{self.settings['start_hotkey']}>", lambda e: self.start_action())
            self.root.bind(f"<{self.settings['stop_hotkey']}>", lambda e: self.stop_action())
        except:
            pass
    
    def apply_hotkeys(self):
        """应用快捷键设置"""
        start_key = self.start_key.get().strip().upper()
        stop_key = self.stop_key.get().strip().upper()
        
        # 验证输入
        if not start_key or not stop_key:
            messagebox.showerror("错误", "快捷键不能为空！")
            return
        
        if start_key == stop_key:
            messagebox.showerror("错误", "开始和停止快捷键不能相同！")
            return
        
        # 验证是否为有效的功能键
        valid_keys = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"]
        if start_key not in valid_keys or stop_key not in valid_keys:
            messagebox.showerror("错误", "快捷键必须是F1-F12之间的功能键！")
            return
        
        # 更新设置
        self.settings["start_hotkey"] = start_key
        self.settings["stop_hotkey"] = stop_key
        
        # 重新绑定快捷键
        self.bind_hotkeys()
        
        # 更新按钮文本
        self.start_btn.config(text=f"开始 ({start_key})")
        self.stop_btn.config(text=f"停止 ({stop_key})")
        
        messagebox.showinfo("成功", f"快捷键设置已应用！\n开始：{start_key}\n停止：{stop_key}")
    
    def save_all_settings(self):
        """保存所有设置"""
        try:
            # 获取当前设置值
            operation = self.operation_type.get()
            
            # 保存操作类型
            self.settings["operation_type"] = operation
            
            if operation == "scroll":
                # 滚动设置
                self.settings["scroll_direction"] = self.scroll_direction.get()
                self.settings["scroll_speed"] = self.scroll_speed.get()
                interval = float(self.scroll_interval.get())
                if interval <= 0:
                    messagebox.showerror("错误", "滚动频率必须大于0秒！")
                    return
                self.settings["scroll_interval"] = interval
            else:
                # 点击设置
                interval = float(self.click_interval.get())
                if interval <= 0:
                    messagebox.showerror("错误", "点击频率必须大于0秒！")
                    return
                self.settings["click_interval"] = interval
            
            # 快捷键设置
            self.settings["start_hotkey"] = self.start_key.get().strip().upper()
            self.settings["stop_hotkey"] = self.stop_key.get().strip().upper()
            
            # 验证快捷键
            valid_keys = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"]
            if (self.settings["start_hotkey"] not in valid_keys or 
                self.settings["stop_hotkey"] not in valid_keys):
                messagebox.showerror("错误", "快捷键必须是F1-F12之间的功能键！")
                return
            
            # 保存到文件
            self.save_settings()
            
            # 更新按钮文本
            self.start_btn.config(text=f"开始 ({self.settings['start_hotkey']})")
            self.stop_btn.config(text=f"停止 ({self.settings['stop_hotkey']})")
            
            # 重新绑定快捷键
            self.bind_hotkeys()
            
            messagebox.showinfo("成功", "所有设置已保存！")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字！")
        except Exception as e:
            messagebox.showerror("错误", f"保存设置时出错：{e}")
    
    def start_action(self):
        """开始执行鼠标操作"""
        try:
            # 获取当前操作类型
            operation = self.operation_type.get()
            
            if operation == "scroll":
                # 滚动操作
                interval = float(self.scroll_interval.get())
                scroll_speed = self.scroll_speed.get()
                scroll_direction = self.scroll_direction.get()
                action_text = f"滚轮滚动 ({scroll_direction})"
            else:
                # 点击操作
                interval = float(self.click_interval.get())
                if operation == "left":
                    action_text = "左键点击"
                elif operation == "right":
                    action_text = "右键点击"
                else:  # middle
                    action_text = "中键点击"
            
            if interval <= 0:
                messagebox.showerror("错误", "频率必须大于0秒！")
                return
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的频率数字！")
            return
        
        # 更新UI状态
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        # 显示操作类型
        self.status_label.config(text=f"正在运行：{action_text}", fg="#27ae60")
        
        # 在新线程中执行操作
        thread = threading.Thread(target=self.run_mouse_action, 
                                 args=(operation, interval))
        thread.daemon = True
        thread.start()
    
    def run_mouse_action(self, operation, interval):
        """执行鼠标操作的线程函数"""
        while self.running:
            try:
                # 执行鼠标操作
                if operation == "scroll":
                    # 滚轮滚动
                    scroll_amount = self.scroll_speed.get()
                    if self.scroll_direction.get() == "down":
                        scroll_amount = -scroll_amount
                    pyautogui.scroll(scroll_amount)
                else:
                    # 鼠标点击
                    if operation == "left":
                        pyautogui.click()
                    elif operation == "right":
                        pyautogui.rightClick()
                    elif operation == "middle":
                        pyautogui.middleClick()
                
                # 更新计数
                self.count += 1
                
                # 更新界面（需要在主线程中执行）
                self.root.after(0, self.update_count_display)
                
                # 等待指定时间
                for i in range(int(interval * 10)):
                    if not self.running:
                        break
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"操作出错：{e}")
                break
    
    def update_count_display(self):
        """更新计数显示"""
        self.count_label.config(text=str(self.count))
    
    def stop_action(self):
        """停止执行鼠标操作"""
        self.running = False
        
        # 更新UI状态
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="已停止", fg="#e74c3c")
    
    def on_closing(self):
        """关闭窗口时的处理"""
        if self.running:
            self.stop_action()
            time.sleep(0.5)
        
        self.root.destroy()

# 运行程序
if __name__ == "__main__":
    app = MouseTool()
    app.root.mainloop()