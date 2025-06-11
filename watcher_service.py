# watcher_service.py (V4.0 新模块 - 自动化哨兵)
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading


class WatcherEventHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        # 使用一个集合来处理短时间内可能出现的重复事件
        self.processed = set()
        self.lock = threading.Lock()

    def on_created(self, event):
        # 当有新文件被创建时触发
        if not event.is_directory:
            # 短时间内（2秒）同一个文件只处理一次
            current_time = time.time()
            with self.lock:
                if (event.src_path, current_time // 2) not in self.processed:
                    print(f"检测到新文件: {event.src_path}")
                    self.callback()  # 调用主程序的回调函数，通知它该整理了
                    self.processed.add((event.src_path, current_time // 2))


class WatcherService:
    def __init__(self, path, callback):
        self.path = path
        self.callback = callback
        self.observer = Observer()
        self.thread = None

    def start(self):
        event_handler = WatcherEventHandler(self.callback)
        self.observer.schedule(event_handler, self.path, recursive=True)

        # 将监视器放在一个单独的线程中运行，不阻塞主程序
        self.thread = threading.Thread(target=self.observer.start, daemon=True)
        self.thread.start()
        print(f"开始监视文件夹: {self.path}")

    def stop(self):
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()  # 等待线程完全结束
            print(f"已停止监视文件夹: {self.path}")