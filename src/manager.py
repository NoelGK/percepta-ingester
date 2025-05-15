import redis
from ffmpeg import FFmpegReaderThread
from config.logging import appLogging as logging
from schemas.new_stream_schema import NewStreamSchema


class IngestionManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.processes = {}

    def add_stream(self, new_stream: NewStreamSchema) -> str:
        stream_name = f"frame_stream:{new_stream.device_id}"
        ffmpeg_reader = FFmpegReaderThread(new_stream, self.redis_client, stream_name)
        self.processes[stream_name] = ffmpeg_reader
        ffmpeg_reader.start()
        return stream_name

    def remove_stream(self, stream_name: str):
        try:
            self.processes[stream_name].stop()
            self.processes.pop(stream_name)
            return True
        except KeyError:
            logging.error(f"Tried to stop stream {stream_name}, which is not in the active processes")
            return False

    def get_active_streams(self) -> dict:
        return [device_id for device_id in self.processes]
