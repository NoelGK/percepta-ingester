import cv2
import redis
import base64
import numpy as np
from config.config import settings
from ffmpeg import FFmpegWatcher
from config.logging import appLogging as logging


def main():
    logging.info("Initializing video capture service...")

    redis_client = redis.Redis(
        host=settings.REDIS.HOST, 
        port=settings.REDIS.PORT,
        password=settings.REDIS.PASSWORD
    )
    logging.info(f"Connected to Redis stream at {settings.REDIS.HOST}")

    ffmpeg_watcher = FFmpegWatcher(settings.RTSP)
    ffmpeg_process = ffmpeg_watcher.ingest()
    frame_byte_size = ffmpeg_watcher.frame_width * ffmpeg_watcher.frame_height * 3

    while True:
        raw_frame = ffmpeg_process.stdout.read(frame_byte_size)
        if len(raw_frame) != frame_byte_size:
            logging.warning("Incomplete frame read from FFmpeg")

        try:
            frame = np.frombuffer(raw_frame, np.uint8).reshape(
                (ffmpeg_watcher.frame_height, ffmpeg_watcher.frame_width, 3)
            )
            _, buffer = cv2.imencode(".jpg", frame)
            encoded_frame = base64.b64encode(buffer).decode("utf-8")
            redis_client.xadd("frame_stream", {"frame": encoded_frame}, maxlen=100)
        except Exception as e:
            logging.error(f"Failed to process frame:\n {e}")


if __name__ == "__main__":
    main()
