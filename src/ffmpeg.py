import cv2
import time
import redis
import base64
import threading
import subprocess
import numpy as np
from config.logging import appLogging as logging
from schemas.stream_schema import StreamSchema
from schemas.connection_status_schema import ConnectionStatus
from config.config import settings


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
        self.ffmpeg_process: subprocess.Popen = None
        self.ill_frames = 0

    def test_connection(self) -> ConnectionStatus:
        """
            FFmpeg doesn't throw an error if the connection string is well formatted.
            It just stays there waiting for a stream to appear, so the approach to check 
            if the connection is OK is to read some frames and determine the status 
            from the numbers of frames read. If there is at least one frame correctly 
            acquired, the connection can be considered valid.
        """
        # Start FFmpeg process and wait for connection
        self.__start_ffmpeg()
        time.sleep(settings.RTSP_TIMEOUT + 1)  # give 1 second margin

        # Check if it has ended
        if self.ffmpeg_process.poll() is None:
            status = ConnectionStatus.CONNECTED
        else:
            status = ConnectionStatus.FAILED
            _, stderr = self.ffmpeg_process.communicate()
            logging.error(f"FFmpeg exited with code {self.ffmpeg_process.returncode}")
        
        self.stop()
        return status


    def run(self):
        self.__start_ffmpeg()
        logging.info(f"Reading {self.frame_size} bytes from ffmpeg")
        while self.running:
            # Read frame from ffmpeg process
            raw_frame = self.ffmpeg_process.stdout.read(self.frame_size)

            # If frame cannot be read, skip it and increment number of ill frames
            if len(raw_frame) != self.frame_size:
                self.ill_frames += 1
                continue

            # Try to encode the frame and send it to Redis.
            try:
                encoded_frame = self.__encode_frame(raw_frame)
                self.__send_to_stream(encoded_frame)
            except Exception as e:
                logging.error(f"Failed to process frame from camera {self.rtsp.device_id}:\n {e}")

            # If number of ill frames is too high, stop ingestion pipeline
            if self.ill_frames > settings.MAX_ILL_FRAMES:
                self.stop()

    def stop(self):
        logging.info(f"Stopping image acquisition from camera {self.rtsp.device_id}...")
        self.running = False
        try:
            self.ffmpeg_process.terminate()
            self.ffmpeg_process.wait(timeout=settings.CAMERA_SHUTDOWN_MAX_TIME)
            logging.info(f"Gracefully stopped process")
        except subprocess.TimeoutExpired:
            logging.warning(f"Camera {self.rtsp.device_id} did not shut down gracefully, force killing...")
            self.ffmpeg_process.kill()

    def __start_ffmpeg(self) -> None:
        ffmpeg_cmd = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-timeout", str(settings.RTSP_TIMEOUT * 1e6),  # timeout is in ms
            "-i", self.rtsp.connection_string,
            '-f', 'image2pipe',
            '-pix_fmt', 'bgr24',
            '-vcodec', 'rawvideo',
            '-'
        ]
        logging.info(f"FFmpeg reading from {self.rtsp.host}/{self.rtsp.stream}")
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
