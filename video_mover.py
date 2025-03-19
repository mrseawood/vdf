import os
import sys
import shutil
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import logging
from datetime import datetime

try:
    from moviepy.editor import VideoFileClip
    video_lib = 'moviepy'
except ImportError:
    try:
        import cv2
        video_lib = 'cv2'
    except ImportError:
        video_lib = None

# 配置日志
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'video_mover_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class VideoMoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("视频时长筛选器")
        self.root.geometry("600x620")
        self.root.resizable(True, True)
        
        self.source_folder = ""
        self.target_folder = ""
        self.max_duration = 0
        self.is_running = False
        self.total_files = 0
        self.processed_files = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加程序说明
        desc_frame = ttk.LabelFrame(main_frame, text="程序说明")
        desc_frame.pack(fill=tk.X, pady=5)
        
        desc_text = """这是一个视频时长筛选工具，可以将小于或等于指定时长的视频文件从源文件夹移动到目标文件夹。

使用方法：
1. 选择包含视频的"导入文件夹"（将递归扫描所有子文件夹）
2. 选择要移动视频的"导出文件夹"
3. 设置视频的"最大时长(秒)"
4. 点击"开始处理"按钮开始筛选和移动视频

注意：程序会移动（而非复制）符合条件的视频文件，并保持原有的文件夹结构。"""
        
        desc_label = ttk.Label(desc_frame, text=desc_text, wraplength=550, justify="left")
        desc_label.pack(padx=10, pady=10)
        
        # 源文件夹选择
        source_frame = ttk.Frame(main_frame)
        source_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(source_frame, text="导入文件夹:").pack(side=tk.LEFT, padx=5)
        self.source_entry = ttk.Entry(source_frame)
        self.source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(source_frame, text="浏览", command=self.browse_source).pack(side=tk.LEFT, padx=5)
        
        # 目标文件夹选择
        target_frame = ttk.Frame(main_frame)
        target_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(target_frame, text="导出文件夹:").pack(side=tk.LEFT, padx=5)
        self.target_entry = ttk.Entry(target_frame)
        self.target_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(target_frame, text="浏览", command=self.browse_target).pack(side=tk.LEFT, padx=5)
        
        # 时长设置
        duration_frame = ttk.Frame(main_frame)
        duration_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(duration_frame, text="最大时长(秒):").pack(side=tk.LEFT, padx=5)
        self.duration_var = tk.DoubleVar(value=60)
        self.duration_entry = ttk.Entry(duration_frame, width=10, textvariable=self.duration_var)
        self.duration_entry.pack(side=tk.LEFT, padx=5)
        
        # 添加验证功能，确保输入为数字
        def validate_number(P):
            if P == "" or P == ".":
                return True
            try:
                float(P)
                return True
            except ValueError:
                return False
        
        vcmd = (self.root.register(validate_number), '%P')
        self.duration_entry.config(validate="key", validatecommand=vcmd)
        self.duration_label = ttk.Label(duration_frame, text="60")
        self.duration_label.pack(side=tk.LEFT, padx=5)
        
        # 添加时长值更新回调
        def update_duration_label(*args):
            self.duration_label.config(text=f"{int(self.duration_var.get())}")
        self.duration_var.trace_add("write", update_duration_label)
        
        # 进度条
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5)
        
        self.status_label = ttk.Label(progress_frame, text="就绪")
        self.status_label.pack(pady=5)
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="日志")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="开始处理", command=self.start_process)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_process, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        
        # 添加版权信息
        copyright_frame = ttk.Frame(main_frame)
        copyright_frame.pack(fill=tk.X, pady=5)
        copyright_text = "© 2025 一模型Ai (https://jmlovestore.com) - 不会开发软件吗 🙂 Ai会哦"
        copyright_label = ttk.Label(copyright_frame, text=copyright_text, anchor="center")
        copyright_label.pack(fill=tk.X)
    
    def browse_source(self):
        folder = filedialog.askdirectory(title="选择导入文件夹")
        if folder:
            self.source_folder = folder
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, folder)
            self.log_message(f"已选择导入文件夹: {folder}")
    
    def browse_target(self):
        folder = filedialog.askdirectory(title="选择导出文件夹")
        if folder:
            self.target_folder = folder
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, folder)
            self.log_message(f"已选择导出文件夹: {folder}")
    
    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        logging.info(message)
    
    def update_status(self, message):
        self.status_label.config(text=message)
    
    def update_progress(self, value=None):
        if value is not None:
            self.progress_var.set(value)
        else:
            if self.total_files > 0:
                progress = (self.processed_files / self.total_files) * 100
                self.progress_var.set(progress)
    
    def get_video_duration(self, video_path):
        try:
            if video_lib == 'moviepy':
                clip = VideoFileClip(video_path)
                duration = clip.duration
                clip.close()
                return duration
            elif video_lib == 'cv2':
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    return None
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = frame_count / fps if fps > 0 else 0
                cap.release()
                return duration
            else:
                self.log_message("错误: 未找到支持的视频处理库 (moviepy 或 cv2)")
                return None
        except Exception as e:
            self.log_message(f"获取视频时长时出错: {str(e)}")
            return None
    
    def is_video_file(self, file_path):
        video_extensions = [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"]
        return os.path.splitext(file_path)[1].lower() in video_extensions
    
    def process_videos(self):
        if not self.source_folder or not self.target_folder:
            messagebox.showerror("错误", "请选择导入和导出文件夹")
            return
        
        try:
            self.max_duration = float(self.duration_var.get())
        except ValueError:
            messagebox.showerror("错误", "无效的时长数值")
            return
        
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # 在新线程中运行处理过程
        threading.Thread(target=self._process_videos_thread, daemon=True).start()
    
    def _process_videos_thread(self):
        try:
            self.update_status("正在扫描文件...")
            self.log_message(f"开始处理: 最大时长 {self.max_duration} 秒")
            
            # 扫描所有视频文件
            all_videos = []
            for root, dirs, files in os.walk(self.source_folder):
                for file in files:
                    if self.is_video_file(file):
                        all_videos.append(os.path.join(root, file))
            
            self.total_files = len(all_videos)
            self.processed_files = 0
            
            if self.total_files == 0:
                self.log_message("未找到视频文件")
                self.update_status("未找到视频文件")
                self.process_completed()
                return
            
            self.log_message(f"找到 {self.total_files} 个视频文件")
            
            # 处理每个视频
            moved_count = 0
            for video_path in all_videos:
                if not self.is_running:
                    self.log_message("处理已停止")
                    break
                
                rel_path = os.path.relpath(video_path, self.source_folder)
                self.update_status(f"正在处理: {rel_path}")
                
                duration = self.get_video_duration(video_path)
                if duration is None:
                    self.log_message(f"无法获取视频时长: {rel_path}")
                else:
                    self.log_message(f"视频: {rel_path}, 时长: {duration:.2f} 秒")
                    
                    if duration <= self.max_duration:
                        # 创建目标路径，保持相同的目录结构
                        target_path = os.path.join(self.target_folder, rel_path)
                        target_dir = os.path.dirname(target_path)
                        
                        try:
                            os.makedirs(target_dir, exist_ok=True)
                            shutil.move(video_path, target_path)
                            self.log_message(f"已移动: {rel_path}")
                            moved_count += 1
                        except Exception as e:
                            self.log_message(f"移动文件时出错: {str(e)}")
                
                self.processed_files += 1
                self.update_progress()
            
            self.log_message(f"处理完成: 共移动 {moved_count} 个视频文件")
            self.update_status(f"完成: 已移动 {moved_count}/{self.total_files} 个文件")
            
        except Exception as e:
            self.log_message(f"处理过程中出错: {str(e)}")
            logging.exception("处理过程异常")
        finally:
            self.process_completed()
    
    def process_completed(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def start_process(self):
        self.source_folder = self.source_entry.get()
        self.target_folder = self.target_entry.get()
        self.process_videos()
    
    def stop_process(self):
        if self.is_running:
            self.is_running = False
            self.update_status("正在停止...")
            self.log_message("正在停止处理...")

def main():
    # 检查是否有必要的视频处理库
    if video_lib is None:
        print("错误: 未找到支持的视频处理库。请安装 moviepy 或 opencv-python")
        print("可以使用以下命令安装:")
        print("pip install moviepy")
        print("或")
        print("pip install opencv-python")
        sys.exit(1)
    
    root = tk.Tk()
    app = VideoMoverApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()