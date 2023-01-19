import codecs
from multiprocessing import Queue, Process
from typing import Dict


class LoggerStream(Process):

    def __init__(self, path: str):
        super().__init__()

        self.path: str = path

        self.queue: Queue = Queue()
        self.streams: Dict[str, codecs.StreamReaderWriter] = {}

    def run(self):
        for (stream, text) in iter(self.queue.get, None):
            if stream not in self.streams:
                stream_file = codecs.open('{}/{}.txt'.format(self.path, stream), 'w', encoding='utf8', buffering=512)
                self.streams[stream] = stream_file
            else:
                stream_file = self.streams[stream]

            stream_file.write(text)

        for stream in self.streams.values():
            stream.flush()

    def stop(self):
        self.queue.put(None)
