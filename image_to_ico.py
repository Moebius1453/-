import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import threading
import sys
import traceback
import subprocess

class ImageToICOConverter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("图片转ICO图标转换器")
        self.root.geometry("700x600")
        self.root.minsize(600, 500)
        
        # 设置默认字体
        self.set_default_fonts()
        
        # 存储选择的文件路径
        self.selected_file_path = ""
        
        # 让窗口居中显示
        self.center_window()
        
        # 转换状态
        self.converting = False
        
        # 支持的图标尺寸
        self.sizes = [16, 24, 32, 48, 64, 128, 256]
        
        # 默认选择常用尺寸
        self.selected_sizes = {16: tk.BooleanVar(value=True),
                              32: tk.BooleanVar(value=True),
                              48: tk.BooleanVar(value=True),
                              64: tk.BooleanVar(value=True),
                              128: tk.BooleanVar(value=False),
                              256: tk.BooleanVar(value=False),
                              24: tk.BooleanVar(value=False)}
        
        # 支持的图片格式
        self.supported_formats = [('PNG图片', '*.png'), 
                                 ('JPEG图片', '*.jpg *.jpeg'), 
                                 ('所有图片', '*.png *.jpg *.jpeg'),
                                 ('所有文件', '*.*')]
        
        # 存储预览图片引用
        self.preview_image = None
        
        self.setup_ui()
        
    def set_default_fonts(self):
        """设置默认字体，提高兼容性"""
        # 尝试使用系统字体
        try:
            # 尝试中文字体
            fonts = ["Microsoft YaHei", "SimHei", "SimSun", "Arial Unicode MS", "Arial"]
            for font in fonts:
                try:
                    # 测试字体是否存在
                    tk.Label(self.root, text="测试", font=(font, 12)).destroy()
                    self.default_font = font
                    break
                except:
                    continue
            else:
                self.default_font = "TkDefaultFont"
        except:
            self.default_font = "TkDefaultFont"
    
    def center_window(self):
        """使窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2) - 20
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        # 创建主容器 - 使用Canvas和滚动条
        main_container = tk.Frame(self.root)
        main_container.pack(fill="both", expand=True)
        
        # 创建Canvas和滚动条
        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 创建滚动框架
        self.scrollable_frame = tk.Frame(canvas)
        
        # 绑定配置事件
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # 将可滚动框架放入Canvas
        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # 配置Canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 绑定鼠标滚轮
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 布局Canvas和滚动条
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 设置Canvas窗口的宽度调整
        def configure_canvas_width(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", configure_canvas_width)
        
        # === 内容区域 ===
        content_frame = tk.Frame(self.scrollable_frame, padx=20, pady=10)
        content_frame.pack(fill="both", expand=True)
        
        # 标题
        title_frame = tk.Frame(content_frame)
        title_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(title_frame, text="图片转ICO图标转换器", 
                font=(self.default_font, 18, "bold")).pack(pady=5)
        
        tk.Label(title_frame, text="支持PNG/JPG/JPEG格式，转换为Windows图标(.ico)", 
                font=(self.default_font, 10), fg="gray").pack()
        
        # 分隔线
        ttk.Separator(content_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # === 图片选择区域 ===
        image_frame = tk.LabelFrame(content_frame, text="选择图片", 
                                   font=(self.default_font, 11, "bold"),
                                   padx=15, pady=10)
        image_frame.pack(fill="x", pady=(0, 15))
        
        # 图片预览
        preview_frame = tk.Frame(image_frame)
        preview_frame.pack(fill="x", pady=5)
        
        # 预览区域
        preview_container = tk.Frame(preview_frame, bg="#f0f0f0", relief="solid", width=150, height=150)
        preview_container.pack(side="left", padx=(0, 15))
        preview_container.pack_propagate(False)  # 保持固定大小
        
        self.preview_label = tk.Label(preview_container, text="选择图片后显示预览", 
                                     bg="#f0f0f0", font=(self.default_font, 9), 
                                     anchor="center", justify="center", wraplength=140)
        self.preview_label.pack(expand=True, fill="both")
        
        # 文件信息和选择按钮
        info_frame = tk.Frame(preview_frame)
        info_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(info_frame, text="支持的格式:", 
                font=(self.default_font, 10)).pack(anchor="w", pady=(0, 5))
        
        format_frame = tk.Frame(info_frame, bg="#f9f9f9", relief="solid", bd=1)
        format_frame.pack(anchor="w", pady=(0, 15), fill="x")
        
        tk.Label(format_frame, text="• PNG (.png)\n• JPEG (.jpg, .jpeg)", 
                bg="#f9f9f9", font=(self.default_font, 9), 
                justify="left").pack(padx=5, pady=5, anchor="w")
        
        self.file_path_display = tk.StringVar()
        tk.Label(info_frame, text="当前文件:", 
                font=(self.default_font, 10)).pack(anchor="w", pady=(5, 0))
        
        file_label = tk.Label(info_frame, textvariable=self.file_path_display, 
                             font=(self.default_font, 9), fg="blue", 
                             wraplength=300, justify="left", anchor="w", 
                             bg="#f9f9f9", relief="solid", bd=1, height=2)
        file_label.pack(anchor="w", pady=(0, 15), fill="x")
        
        tk.Button(info_frame, text="选择图片文件", 
                 command=self.select_image_file,
                 font=(self.default_font, 10), width=20, height=2).pack(anchor="w")
        
        # === 尺寸选择区域 ===
        size_frame = tk.LabelFrame(content_frame, text="选择图标尺寸", 
                                  font=(self.default_font, 11, "bold"),
                                  padx=15, pady=10)
        size_frame.pack(fill="x", pady=(0, 15))
        
        # 尺寸复选框
        tk.Label(size_frame, text="选择需要的图标尺寸:", 
                font=(self.default_font, 10)).pack(anchor="w", pady=(0, 10))
        
        size_grid = tk.Frame(size_frame)
        size_grid.pack(fill="x", pady=5)
        
        # 创建两行复选框
        row1_frame = tk.Frame(size_grid)
        row1_frame.pack(fill="x", pady=2)
        
        sizes_row1 = [16, 32, 48, 64]
        for i, size in enumerate(sizes_row1):
            cb = tk.Checkbutton(row1_frame, text=f"{size}x{size}", 
                               variable=self.selected_sizes[size],
                               font=(self.default_font, 10))
            cb.pack(side="left", padx=20 if i < len(sizes_row1)-1 else 0)
        
        row2_frame = tk.Frame(size_grid)
        row2_frame.pack(fill="x", pady=2)
        
        sizes_row2 = [128, 256, 24]
        for i, size in enumerate(sizes_row2):
            cb = tk.Checkbutton(row2_frame, text=f"{size}x{size}", 
                               variable=self.selected_sizes[size],
                               font=(self.default_font, 10))
            cb.pack(side="left", padx=20 if i < len(sizes_row2)-1 else 0)
        
        # 选择按钮
        button_frame = tk.Frame(size_frame)
        button_frame.pack(pady=10)
        
        buttons = [
            ("全选", self.select_all_sizes),
            ("清除", self.clear_all_sizes),
            ("常用尺寸", self.select_common_sizes),
            ("推荐尺寸", self.select_recommended_sizes)
        ]
        
        for text, command in buttons:
            tk.Button(button_frame, text=text, 
                     command=command,
                     font=(self.default_font, 9)).pack(side="left", padx=5)
        
        # === 输出设置 ===
        output_frame = tk.LabelFrame(content_frame, text="输出设置", 
                                    font=(self.default_font, 11, "bold"),
                                    padx=15, pady=10)
        output_frame.pack(fill="x", pady=(0, 15))
        
        # 输出文件名
        tk.Label(output_frame, text="输出文件名:", 
                font=(self.default_font, 10)).grid(row=0, column=0, sticky="w", pady=5)
        
        self.output_name = tk.StringVar(value="icon")
        name_entry = tk.Entry(output_frame, textvariable=self.output_name,
                            font=(self.default_font, 10), width=30)
        name_entry.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        tk.Label(output_frame, text=".ico", 
                font=(self.default_font, 10)).grid(row=0, column=2, sticky="w", padx=(5, 0))
        
        # 输出目录
        tk.Label(output_frame, text="输出目录:", 
                font=(self.default_font, 10)).grid(row=1, column=0, sticky="w", pady=5)
        
        self.output_dir = tk.StringVar(value=os.path.expanduser("~/Desktop"))
        dir_entry = tk.Entry(output_frame, textvariable=self.output_dir,
                           font=(self.default_font, 10), width=30)
        dir_entry.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        tk.Button(output_frame, text="浏览...", 
                 command=self.select_output_dir,
                 font=(self.default_font, 9)).grid(row=1, column=2, sticky="w", padx=(5, 0))
        
        # === 控制按钮 ===
        control_frame = tk.Frame(content_frame)
        control_frame.pack(pady=20)
        
        self.convert_button = tk.Button(control_frame, text="开始转换", 
                                       command=self.start_conversion,
                                       font=(self.default_font, 12, "bold"),
                                       width=20, height=2, bg="#4CAF50", fg="white")
        self.convert_button.pack(side="left", padx=10)
        
        self.open_button = tk.Button(control_frame, text="打开输出目录", 
                                    command=self.open_output_dir,
                                    font=(self.default_font, 12),
                                    width=20, height=2, state="disabled")
        self.open_button.pack(side="left", padx=10)
        
        # === 进度条 ===
        self.progress = ttk.Progressbar(content_frame, mode='indeterminate')
        self.progress.pack(fill="x", pady=(0, 10))
        
        # === 状态栏 ===
        self.status_label = tk.Label(self.root, text="准备就绪", 
                                    font=(self.default_font, 10),
                                    bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=10)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 强制更新界面
        self.root.update_idletasks()
    
    def select_image_file(self):
        """选择图片文件"""
        file_path = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=self.supported_formats
        )
        if file_path:
            # 存储完整路径到实例变量
            self.selected_file_path = file_path
            # 只显示文件名
            self.file_path_display.set(os.path.basename(file_path))
            # 更新预览
            self.update_preview(file_path)
            # 自动设置输出文件名
            name = os.path.splitext(os.path.basename(file_path))[0]
            self.output_name.set(name)
            
            # 更新状态
            file_size = os.path.getsize(file_path) / 1024  # KB
            file_ext = os.path.splitext(file_path)[1].upper()
            self.update_status(f"已选择: {os.path.basename(file_path)} ({file_ext}, {file_size:.1f}KB)")
    
    def update_preview(self, file_path):
        """更新图片预览"""
        try:
            # 使用PIL加载图片并调整大小以适合预览区域
            img = Image.open(file_path)
            
            # 获取图片尺寸
            width, height = img.size
            
            # 调整大小以适应预览区域
            max_size = 140
            if width > max_size or height > max_size:
                if width > height:
                    new_width = max_size
                    new_height = int(height * (max_size / width))
                else:
                    new_height = max_size
                    new_width = int(width * (max_size / height))
            else:
                new_width, new_height = width, height
            
            # 调整图片大小
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为Tkinter PhotoImage
            self.preview_image = ImageTk.PhotoImage(img_resized)
            
            # 更新标签
            self.preview_label.config(image=self.preview_image, 
                                      text=f"{width}×{height}",
                                      compound="top")
            
        except Exception as e:
            self.preview_label.config(image=None, 
                                      text=f"预览加载失败\n{str(e)[:20]}...",
                                      compound="center")
    
    def select_all_sizes(self):
        """全选所有尺寸"""
        for var in self.selected_sizes.values():
            var.set(True)
    
    def clear_all_sizes(self):
        """清除所有尺寸选择"""
        for var in self.selected_sizes.values():
            var.set(False)
    
    def select_common_sizes(self):
        """选择常用尺寸"""
        self.clear_all_sizes()
        common_sizes = [16, 32, 48, 64]
        for size in common_sizes:
            self.selected_sizes[size].set(True)
    
    def select_recommended_sizes(self):
        """选择推荐尺寸（适合Windows应用）"""
        self.clear_all_sizes()
        recommended_sizes = [16, 32, 48, 64, 128, 256]
        for size in recommended_sizes:
            self.selected_sizes[size].set(True)
    
    def select_output_dir(self):
        """选择输出目录"""
        dir_path = filedialog.askdirectory(
            title="选择输出目录",
            initialdir=self.output_dir.get()
        )
        if dir_path:
            self.output_dir.set(dir_path)
    
    def update_status(self, message):
        """更新状态"""
        self.status_label.config(text=message)
        self.root.update()
    
    def start_conversion(self):
        """开始转换"""
        # 使用存储的完整文件路径
        image_file = self.selected_file_path
        
        if not image_file or not os.path.exists(image_file):
            messagebox.showerror("错误", "请先选择图片文件！")
            return
        
        # 检查是否至少选择了一个尺寸
        selected = [size for size, var in self.selected_sizes.items() if var.get()]
        if not selected:
            messagebox.showerror("错误", "请至少选择一个图标尺寸！")
            return
        
        if self.converting:
            return
        
        self.converting = True
        self.convert_button.config(state="disabled")
        self.open_button.config(state="disabled")
        self.progress.start()
        
        # 在新线程中转换
        thread = threading.Thread(target=self.convert_in_thread, args=(selected,), daemon=True)
        thread.start()
    
    def convert_in_thread(self, sizes):
        """在后台线程中执行转换"""
        try:
            image_file = self.selected_file_path
            output_name = self.output_name.get()
            output_dir = self.output_dir.get()
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            self.update_status("正在加载图片...")
            
            # 加载原始图片
            img = Image.open(image_file)
            
            # 记录原始模式
            original_mode = img.mode
            
            # 转换RGBA模式为RGB模式（如果包含透明通道）
            if img.mode in ('RGBA', 'LA'):
                # 创建一个白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                # 合并图片
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[3])
                else:
                    background.paste(img, mask=img.split()[1])
                img = background
                mode_change = f"（已从{original_mode}转换为RGB）"
            else:
                mode_change = ""
            
            self.update_status(f"正在生成 {len(sizes)} 种尺寸{mode_change}...")
            
            # 创建不同尺寸的图片
            icons = []
            for size in sizes:
                # 调整图片大小
                resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
                icons.append(resized_img)
            
            # 保存为ICO文件
            output_path = os.path.join(output_dir, f"{output_name}.ico")
            
            self.update_status("正在保存ICO文件...")
            
            # 保存所有尺寸到一个ICO文件
            icons[0].save(output_path, format='ICO', sizes=[(size, size) for size in sizes])
            
            # 完成
            file_size = os.path.getsize(output_path) / 1024  # KB
            self.update_status(f"转换完成！文件已保存到: {output_path} ({file_size:.1f}KB)")
            
            # 启用打开按钮
            self.open_button.config(state="normal")
            
            # 显示成功消息
            self.root.after(0, lambda: messagebox.showinfo(
                "成功", 
                f"ICO文件已生成！\n\n"
                f"位置: {output_path}\n"
                f"大小: {file_size:.1f}KB\n"
                f"包含尺寸: {', '.join(map(str, sizes))}"
            ))
            
        except Exception as e:
            error_msg = f"转换过程中出错: {str(e)}"
            print(traceback.format_exc())
            self.update_status(error_msg)
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
        
        finally:
            self.converting = False
            self.convert_button.config(state="normal")
            self.progress.stop()
    
    def open_output_dir(self):
        """打开输出目录"""
        dir_path = self.output_dir.get()
        
        if os.path.exists(dir_path):
            try:
                # 根据不同操作系统打开目录
                if os.name == 'nt':  # Windows
                    os.startfile(dir_path)
                elif os.name == 'posix':  # Linux or macOS
                    subprocess.Popen(['xdg-open' if sys.platform == 'linux' else 'open', dir_path])
            except Exception as e:
                messagebox.showinfo("提示", f"输出目录: {dir_path}\n\n打开文件夹时出错: {str(e)}")
        else:
            messagebox.showerror("错误", "输出目录不存在！")
    
    def run(self):
        self.root.mainloop()

def main():
    # 检查PIL库是否安装
    try:
        from PIL import Image
    except ImportError:
        print("错误: 需要Pillow库")
        print("请安装: pip install Pillow")
        input("按Enter键退出...")
        sys.exit(1)
    
    app = ImageToICOConverter()
    app.run()

if __name__ == "__main__":
    main()