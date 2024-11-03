import subprocess
import os
import sys
import shutil
import tempfile  # 导入 tempfile 模块，用于创建临时目录

def detect_resolution_changes(input_video):
    # 使用 ffprobe 检测视频中的分辨率变化，返回每一帧的时间戳、宽度和高度
    command = f"ffprobe -v error -select_streams v:0 -show_entries frame=best_effort_timestamp_time,width,height -of csv=p=0 \"{input_video}\""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.splitlines()  # 返回结果的每一行

def process_resolution_changes(input_video, resolution_changes):
    previous_resolution = None  # 初始化前一个分辨率
    start_time = None  # 初始化起始时间
    segments = []  # 初始化分段信息列表

    for line in resolution_changes:  # 遍历每一行分辨率变化数据
        if not line.strip():  # 跳过空行
            continue

        parts = line.split(',')  # 拆分行内容
        if len(parts) != 3:  # 检查是否有3个部分（时间戳、宽度、高度）
            continue  # 不输出跳过信息，直接继续下一行

        time, width, height = parts  # 解包时间戳、宽度、高度
        resolution = f"{width}x{height}"  # 拼接分辨率字符串

        if resolution != previous_resolution:  # 如果分辨率发生变化
            if previous_resolution is not None:  # 如果前一个分辨率存在
                end_time = time  # 当前时间戳为上一个分辨率段的结束时间
                segments.append((previous_resolution, start_time, end_time))  # 添加分段信息
                print(f"Resolution {previous_resolution} from time {start_time} to time {end_time}")
            start_time = time  # 更新起始时间
            previous_resolution = resolution  # 更新前一个分辨率

    if previous_resolution is not None:  # 处理最后一个分辨率段
        end_time = time
        segments.append((previous_resolution, start_time, end_time))
        print(f"Resolution {previous_resolution} from time {start_time} to time {end_time}")
    
    return segments  # 返回所有分段信息

def split_and_adjust_resolution(input_video, output_video, segments):
    video_name = os.path.splitext(os.path.basename(input_video))[0]  # 获取视频名
    output_dir = tempfile.mkdtemp(prefix=f"{video_name}.segments_", dir=tempfile.gettempdir())  # 定义系统临时文件夹中的输出目录
    os.makedirs(output_dir, exist_ok=True)  # 创建输出目录（如果不存在）

    output_file = os.path.abspath(output_video)  # 转成绝对路径

    segment_files = []  # 初始化分段文件列表
    for resolution, start_time, end_time in segments:  # 遍历每个分段
        width, height = resolution.split('x')  # 获取分辨率宽度和高度
        output_file_path = os.path.join(output_dir, f"segment_{resolution.replace('x', '_')}_{start_time}_{end_time}.mp4")  # 定义输出文件路径
        segment_files.append(f"segment_{resolution.replace('x', '_')}_{start_time}_{end_time}.mp4")  # 添加到分段文件列表
        # 构建 ffmpeg 命令，选择时间范围并调整分辨率进行转码
        command = f"ffmpeg -y -i \"{input_video}\" -ss {start_time} -to {end_time} -vf \"scale={width}:{height}\" -c:v hevc_amf -qp_i 28 -qp_p 28 -c:a aac -b:a 64k \"{output_file_path}\""
        #command = f"ffmpeg -y -i \"{input_video}\" -ss {start_time} -to {end_time} -vf \"scale={width}:{height}\" -c:v libsvtav1 -crf 28 -preset 8 -threads 16 -c:a aac -b:a 64k \"{output_file_path}\""
        print(f"Executing: {command}")  # 打印调试信息
        subprocess.run(command, shell=True, check=True)  # 执行 ffmpeg 命令

    os.chdir(output_dir)  # 切换到输出目录

    merge_list_file = "merge_list.txt"  # 定义合并列表文件路径
    with open(merge_list_file, 'w') as f:  # 创建并写入合并列表文件
        for segment_file in segment_files:  # 遍历每个分段文件
            f.write(f"file {segment_file}\n")  # 使用相对路径写入合并列表

    # 构建 ffmpeg 命令，合并所有分段视频
    command = f"ffmpeg -y -f concat -safe 0 -i {merge_list_file} -c copy \"{output_file}\""
    print(f"Executing: {command}")  # 打印调试信息
    subprocess.run(command, shell=True, check=True)  # 执行 ffmpeg 合并命令

    for segment_file in segment_files:  # 遍历每个分段文件
        os.remove(segment_file)  # 删除临时分割视频

    os.chdir('..')  # 切换回原目录
    shutil.rmtree(output_dir)  # 删除输出目录

if __name__ == "__main__":
    if len(sys.argv) != 3:  # 检查命令行参数
        print("Usage: python trancode-dynamic-resolution.py <input_video> <output_video>")  # 提示正确用法
        sys.exit(1)  # 退出程序

    input_video = sys.argv[1]  # 获取输入视频文件路径
    output_video = sys.argv[2]  # 获取输出视频文件路径
    resolution_changes = detect_resolution_changes(input_video)  # 检测分辨率变化
    segments = process_resolution_changes(input_video, resolution_changes)  # 处理分辨率变化
    split_and_adjust_resolution(input_video, output_video, segments)  # 分割并调整分辨率
