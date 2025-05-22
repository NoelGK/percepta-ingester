import redis
from ffmpeg import FFmpegReaderThread
from config.logging import appLogging as logging
from schemas.stream_schema import StreamSchema


class IngestionManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.processes = {}

    def start_stream(self, stream: StreamSchema) -> str:
        stream_name = f"frame_stream:{stream.device_id}"
        ffmpeg_reader = FFmpegReaderThread(stream, self.redis_client, stream_name)
        self.processes[stream.id] = ffmpeg_reader
        ffmpeg_reader.start()
        return stream_name

    def stop_stream(self, stream_id: int):
        try:
            ffmpeg_process = self.processes.pop(stream_id)
            ffmpeg_process.stop()
            return True
        except KeyError:
            logging.error(f"Tried to stop stream {stream_id}, which is not in the active processes")
            return False

    def get_active_streams(self) -> dict:
        return [device_id for device_id in self.processes]
