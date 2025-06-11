# core_logic.py (V3.2 - 智能日期引擎 & 智能预览)

import os
import shutil
import magic
import datetime
from collections import Counter
from PIL import Image
from PIL.ExifTags import TAGS


def get_image_taken_date(file_path):
    """
    尝试从图片的EXIF信息中获取拍摄日期。
    这是V3.0的核心技术之一。
    """
    try:
        with Image.open(file_path) as img:
            exif_data = img._getexif()
            if exif_data:
                # 36867 是 DateTimeOriginal (拍摄日期) 的标签ID
                if 36867 in exif_data:
                    date_str = exif_data[36867]
                    return datetime.datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
    except Exception:
        # 如果文件不是图片、格式损坏或没有EXIF信息，则会失败
        pass
    return None


def analyze_files(source_dir, rules, mode):
    """
    分析文件，用于生成预览报告。
    现在能根据不同的整理模式生成不同的、智能的报告。
    这是V3.2的核心升级。
    """
    analysis_result = Counter()

    try:
        # 过滤掉文件夹，只处理文件
        all_files = [os.path.join(r, f) for r, d, fs in os.walk(source_dir) for f in fs if
                     os.path.isfile(os.path.join(r, f))]

        if mode == 'type':
            # 按文件类型分析
            for file_path in all_files:
                try:
                    mime_type = magic.from_file(file_path, mime=True)
                    if mime_type in rules:
                        # 按目标文件夹的主类别来统计 (例如 '图片/JPG' -> '图片')
                        main_category = rules[mime_type].split('/')[0]
                        analysis_result[main_category] += 1
                    else:
                        analysis_result["未匹配规则的文件"] += 1
                except Exception:
                    analysis_result["无法识别的文件"] += 1

        elif mode == 'creation_date' or mode == 'taken_date':
            # 按日期分析
            target_folders = set()  # 使用集合来存储不重复的目标文件夹名
            for file_path in all_files:
                try:
                    folder_name = None
                    if mode == 'creation_date':
                        ctime = os.path.getctime(file_path)
                        folder_name = datetime.datetime.fromtimestamp(ctime).strftime(
                            '%Y/%m_%B')  # 格式: 2023/11_November
                    elif mode == 'taken_date':
                        taken_date = get_image_taken_date(file_path)
                        if taken_date:
                            folder_name = taken_date.strftime('%Y/%m_%B')
                        else:  # 备用方案
                            ctime = os.path.getctime(file_path)
                            folder_name = datetime.datetime.fromtimestamp(ctime).strftime('%Y/%m_%B')
                    if folder_name:
                        target_folders.add(folder_name)
                except Exception:
                    pass  # 忽略单个文件的日期读取错误
            # 最终的分析结果是目标文件夹的数量和总文件数
            analysis_result['个文件'] = len(all_files)
            analysis_result['个按日期命名的文件夹'] = len(target_folders)

        return analysis_result
    except Exception as e:
        print(f"分析文件夹时出错: {e}")
        return None


def sort_files_logic(params, callbacks):
    """
    文件整理的核心函数，包含了所有整理模式的实现。
    """
    source_dir = params['source_dir']
    dest_dir = params['dest_dir']
    is_copy_mode = params['is_copy_mode']
    rules = params['rules']
    mode = params['mode']

    pause_event = params['pause_event']
    cancel_flag = params['cancel_flag']
    update_status = callbacks['update_status']
    update_progress = callbacks['update_progress']
    on_complete = callbacks['on_complete']

    try:
        action_text = "已复制" if is_copy_mode else "已移动"
        all_files = [(os.path.join(r, f), f) for r, d, fs in os.walk(source_dir) for f in fs if
                     os.path.isfile(os.path.join(r, f))]
        total_files = len(all_files)
        if total_files == 0:
            update_status("源文件夹中没有文件。")
            on_complete()
            return

        processed_files = 0
        update_status("准备开始整理...")

        for file_path, filename in all_files:
            if cancel_flag[0]:
                update_status("操作已取消。")
                break
            pause_event.wait()
            processed_files += 1
            update_progress((processed_files / total_files) * 100)

            try:
                folder_name = None

                if mode == 'type':
                    mime_type = magic.from_file(file_path, mime=True)
                    folder_name = rules.get(mime_type)

                elif mode == 'creation_date':
                    ctime_timestamp = os.path.getctime(file_path)
                    ctime_dt = datetime.datetime.fromtimestamp(ctime_timestamp)
                    folder_name = ctime_dt.strftime('%Y/%m_%B')

                elif mode == 'taken_date':
                    taken_date = get_image_taken_date(file_path)
                    if taken_date:
                        folder_name = taken_date.strftime('%Y/%m_%B')
                    else:
                        ctime_timestamp = os.path.getctime(file_path)
                        ctime_dt = datetime.datetime.fromtimestamp(ctime_timestamp)
                        folder_name = ctime_dt.strftime('%Y/%m_%B') + "/(无拍摄信息)"

                if folder_name:
                    dest_folder_path = os.path.join(dest_dir, folder_name)
                    if not os.path.exists(dest_folder_path):
                        os.makedirs(dest_folder_path)

                    if is_copy_mode:
                        shutil.copy2(file_path, dest_folder_path)
                    else:
                        shutil.move(file_path, dest_folder_path)
                    update_status(f"[{processed_files}/{total_files}] {action_text} ({filename}) -> {folder_name}")
                else:
                    update_status(f"[{processed_files}/{total_files}] 跳过 (无匹配规则): {filename}")
            except Exception as e:
                update_status(f"处理 {filename} 时跳过: {e}")

        if not cancel_flag[0]:
            update_status(f"整理完成！共处理 {total_files} 个文件。")
        on_complete()
    except Exception as e:
        print(f"整理过程中发生严重错误: {e}")
        on_complete()