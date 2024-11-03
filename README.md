# transcode-dynamic-resolution
```transcode-dynamic-resolution``` 是一个用于具有动态分辨率视频转码能力的简单 Python 脚本

# 使用场景:

直播录屏视频,主播在连麦前后视频的分辨率会发生动态变化，使用ffmpeg直接转码会导致分辨率发生变化的部分被拉伸压缩，该脚本旨在解决这个痛点。

# 原理:

检测动态分辨率变化：使用 ffprobe 分析视频发生分辨率变化的时间戳。

分段转码：基于检测到分辨率变化的时间戳，使用正确的分辨率调用 ffmpeg 对视频进行分段转码。

合并：将转码后的文件合并并删除分段视频。

# 环境准备:

确保已安装 Python 及相关依赖库：

```pip install ffmpeg-python```

# 使用方法:

```python transcode-dynamic-resolution.py <input_video> <output_video>```

将 <input_video> 转码并输出到 <output_video>。<input_video> <output_video>两者均为文件而不是文件夹，可以使用相对路径

# 注意:

脚本内调用的编码器是```hevc_amf```，请结合你自己的硬件设备和需求进行更改

# 许可证:

本项目采用 MIT 许可证。
