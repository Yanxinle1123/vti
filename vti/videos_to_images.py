import asyncio
import concurrent.futures
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
    address = addr + str(name) + suffix
    cv2.imwrite(address, image)


class VideosToImages:
    def __init__(self, video_source, save_path, suffix='.jpg', frame_interval_ms=1000):
        self._video_source = video_source
        self._save_path = save_path
        self._suffix = suffix
        self._frame_interval_ms = frame_interval_ms
        asyncio.run(self.convert())

    async def convert(self):
        video_capture = cv2.VideoCapture(self._video_source)
        is_cam = is_camera(self._video_source)
        if is_cam:
            time.sleep(2)

        # 获取视频的帧率
        fps = int(video_capture.get(cv2.CAP_PROP_FPS))

        # 计算每隔 frame_interval_ms 毫秒应该跳过的帧数
        skip_frames = fps * self._frame_interval_ms // 1000

        # 截图
        i = 0
        j = 1
        tasks = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            while video_capture.isOpened():
                success, frame = video_capture.read()
                if not success:
                    break

                if i % skip_frames == 0:
                    loop = asyncio.get_running_loop()
                    task = loop.run_in_executor(executor, _save_image, frame, self._save_path, j, self._suffix)
                    tasks.append(task)
                    j += 1
                i += 1

            # 等待所有任务完成
            await asyncio.gather(*tasks)

        video_capture.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    start_time = time.time()

    video_path = 'https://img.tukuppt.com/video_show/2475824/00/01/84/5b4b1d6d2b582.mp4'
    save_path = 'save_images/fallen_leaves2_images/'

    VideosToImages(video_source=video_path, save_path=save_path, suffix='.jpg', frame_interval_ms=1000)

    end_time = time.time()

    print('运行时长:', end_time - start_time)
