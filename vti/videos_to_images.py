import os
import time
from multiprocessing import Pool
from typing import Union

import cv2
import psutil


# 判断是否连接到摄像头
def is_camera(video_source):
    video_capture = cv2.VideoCapture(video_source)
    frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    video_capture.release()
    return frame_count <= 0


# 保存图片
def _save_image(image, addr, name, suffix='.jpg'):
    address = os.path.join(addr, f"{name}{suffix}")
    cv2.imwrite(address, image)


def process_frame(video_source, index, save_path, suffix):
    video_capture = cv2.VideoCapture(video_source)
    video_capture.set(cv2.CAP_PROP_POS_FRAMES, index)
    success, frame = video_capture.read()
    video_capture.release()

    if success:
        _save_image(frame, save_path, index + 1, suffix)


class VideosToImages:
    def __init__(self, video_source, save_path, frame_interval_ms: Union[tuple, int], suffix='.jpg',
                 max_workers: Union[str, int] = 'auto'):
        self._video_source = video_source
        self._save_path = save_path
        self._suffix = suffix
        self._frame_interval_ms = frame_interval_ms
        self._max_workers = max_workers

        # 确保保存路径存在
        os.makedirs(self._save_path, exist_ok=True)

        self.convert()

    def convert(self):
        try:
            video_capture = cv2.VideoCapture(self._video_source)
            is_cam = is_camera(self._video_source)
            if is_cam:
                time.sleep(2)

            # 获取视频的总帧数
            total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

            # 处理 frame_interval_ms 参数
            if isinstance(self._frame_interval_ms, tuple) and self._frame_interval_ms[0] == 'auto':
                num_images = self._frame_interval_ms[1]

                # 计算每张图应该截取的帧索引
                frame_indices = [int(i * (total_frames - 1) / (num_images - 1)) for i in range(num_images)]
            else:
                fps = int(video_capture.get(cv2.CAP_PROP_FPS))
                skip_frames = fps * self._frame_interval_ms // 1000
                frame_indices = [i * skip_frames for i in range(total_frames // skip_frames)]

            video_capture.release()

            if self._max_workers == 'auto':
                # 获取当前系统的CPU使用率
                cpu_usage = psutil.cpu_percent(interval=1)

                # 根据CPU使用率动态调整进程池大小
                max_workers = psutil.cpu_count(logical=False)  # 获取物理核心数
                if cpu_usage > 70:
                    max_workers = max(1, max_workers // 2)
            else:
                max_workers = self._max_workers

            # 使用多进程处理
            with Pool(processes=max_workers) as pool:
                pool.starmap(
                    process_frame,
                    [(self._video_source, index, self._save_path, self._suffix) for index in frame_indices]
                )

            cv2.destroyAllWindows()
        except ZeroDivisionError:
            print("\033[31mError: The value of parameter 'frame_interval_ms' cannot be too small\033[0m")
            return 'Error'


if __name__ == '__main__':
    print('处理中')

    start_time = time.time()

    video_path = 'https://img.tukuppt.com/video_show/2475824/00/01/84/5b4b1d6d2b582.mp4'
    save_path = 'save_images/fallen_leaves2_images/'

    VideosToImages(video_source=video_path, save_path=save_path, frame_interval_ms=('auto', 10), max_workers='auto')

    print(f'处理完成, 处理时间: {time.time() - start_time}')
