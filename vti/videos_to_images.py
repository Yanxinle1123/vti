import asyncio
import concurrent.futures
import os
import time

import cv2


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


class VideosToImages:
    def __init__(self, video_source, save_path, frame_interval_ms, suffix='.jpg'):
        self._video_source = video_source
        self._save_path = save_path
        self._suffix = suffix
        self._frame_interval_ms = frame_interval_ms

        # 确保保存路径存在
        os.makedirs(self._save_path, exist_ok=True)

        asyncio.run(self.convert())

    async def convert(self):
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

        tasks = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i, index in enumerate(frame_indices):
                # 设置视频捕获到指定帧
                video_capture.set(cv2.CAP_PROP_POS_FRAMES, index)
                success, frame = video_capture.read()
                if success:
                    loop = asyncio.get_running_loop()
                    # 使用 i + 1 作为图片名称
                    task = loop.run_in_executor(executor, _save_image, frame, self._save_path, i + 1, self._suffix)
                    tasks.append(task)

            # 等待所有任务完成
            await asyncio.gather(*tasks)

        video_capture.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    print('处理中')

    video_path = 'https://img.tukuppt.com/video_show/2475824/00/01/84/5b4b1d6d2b582.mp4'
    save_path = 'save_images/fallen_leaves2_images/'

    VideosToImages(video_source=video_path, save_path=save_path, frame_interval_ms=('auto', 5))

    print('处理完成')
