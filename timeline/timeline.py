"""
timeline.py

通用工具函数：
- 单位转换（秒与帧）
- 合并重叠区间（用于覆盖率计算）
"""


def seconds_to_frames(seconds):
    """
    将秒转换为帧（1秒 = 30帧）
    """
    return int(seconds * 30)


def frames_to_seconds(frames):
    """
    将帧数转换为秒（1秒 = 30帧）
    """
    return frames / 30.0


def merge_intervals(intervals):
    """
    合并重叠的时间区间。

    参数:
      intervals: 列表 [(start, end), ...]
    返回:
      合并后的区间列表
    """
    if not intervals:
        return []
    intervals = sorted(intervals, key=lambda x: x[0])
    merged = [intervals[0]]
    for current in intervals[1:]:
        prev = merged[-1]
        if current[0] <= prev[1]:
            merged[-1] = (prev[0], max(prev[1], current[1]))
        else:
            merged.append(current)
    return merged
