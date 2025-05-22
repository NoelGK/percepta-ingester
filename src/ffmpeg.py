import cv2
import redis
import base64
import threading
import subprocess
import numpy as np
from config.logging import appLogging as logging
from schemas.stream_schema import StreamSchema


class FFmpegReaderThread(threading.Thread):
    def __init__(
        self, 
        camera_settings: StreamSchema,
        redis_client: redis.Redis,
        stream_name: str
    ):
        super().__init__()
        self.rtsp = camera_settings
        self.redis_client = redis_client
        self.stream_name = stream_name
        self.frame_size = self.rtsp.frame_width * self.rtsp.frame_height * 3
        self.running = True
        self.ffmpeg_process = None
    
    def run(self):
        self.__start_ffmpeg()
        logging.info(f"Reading {self.frame_size} bytes from ffmpeg")
        while self.running:
            raw_frame = self.ffmpeg_process.stdout.read(self.frame_size)
            if len(raw_frame) != self.frame_size:
                logging.warning("Incomplete frame read from FFmpeg")
                continue

            try:
                encoded_frame = self.__encode_frame(raw_frame)
                self.__send_to_stream(encoded_frame)

            except Exception as e:
                logging.error(f"Failed to process frame from camera {self.rtsp.device_id}:\n {e}")

    def stop(self):
        logging.info(f"Stopping image acquisition from camera {self.rtsp.device_id}...")
        self.running = False
        try:
            self.ffmpeg_process.terminate()
            self.ffmpeg_process.wait(timeout=10)
            logging.info(f"Gracefully stopped process")
        except subprocess.TimeoutExpired:
            logging.warning(f"Camera {self.rtsp.device_id} did not shut down gracefully, force killing...")
            self.ffmpeg_process.kill()

    def __start_ffmpeg(self) -> None:
        ffmpeg_cmd = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", self.rtsp.connection_string,
            '-f', 'image2pipe',
            '-pix_fmt', 'bgr24',
            '-vcodec', 'rawvideo',
            '-'
        ]
        logging.info(f"FFmpeg ingesting from {self.rtsp.host}/{self.rtsp.stream}")
        self.ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    def __encode_frame(self, raw_frame):
        frame = np.frombuffer(raw_frame, np.uint8)
        frame = frame.reshape((self.rtsp.frame_height, self.rtsp.frame_width, 3))
        _, buffer = cv2.imencode(".jpg", frame)
        return base64.b64encode(buffer).decode("utf-8")
    
    def __send_to_stream(self, encoded_frame):
        body = {
            "device_id": self.rtsp.device_id,
            "frame": encoded_frame
        }
        self.redis_client.xadd(self.stream_name, body, maxlen=1000)
