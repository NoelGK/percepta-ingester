import subprocess
from config.rtsp import RTSPSettings
from config.logging import appLogging as logging


class FFmpegWatcher:
    def __init__(
        self, 
        rtsp_settings: RTSPSettings,
        frame_width: int = 1920,
        frame_height: int = 1080
    ):
        self.rtsp = rtsp_settings
        self.frame_width = frame_width
        self.frame_height = frame_height

    def ingest(self) -> subprocess.Popen:
        ffmpeg_cmd = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", self.rtsp.connection_string,
            '-f', 'image2pipe',
            '-pix_fmt', 'bgr24',
            '-vcodec', 'rawvideo',
            '-'
        ]
        logging.info(f"FFmpeg ingesting from {self.rtsp.HOST}/{self.rtsp.STREAM}")
        return subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
