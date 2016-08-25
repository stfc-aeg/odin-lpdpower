import time
from functools import partial

class _DeferredCommand(object):

    def __init__(self, command, delay, *args, **kwargs):

        self.partial = partial(command, *args, **kwargs)
        self.delay = delay

    def execute(self):
        self.partial()

class DeferredExecutor(object):
    """Implements a deferred command executor."""

    def __init__(self):

        self.execution_queue = []
        self.last_executed = 0.0

    def enqueue(self, command, delay, *args, **kwargs):
        self.execution_queue.append(_DeferredCommand(command, delay, *args, **kwargs))

    def pending(self):
        return len(self.execution_queue)

    def process(self):

        if len(self.execution_queue) > 0:
            now = time.time()
            next_command = self.execution_queue[0]

            if now >= (self.last_executed + next_command.delay):
                next_command.execute()
                self.execution_queue.pop(0)
                self.last_executed = now


class Quad(object):

    def __init__(self, id):
        self.id = id

    def enable_channel(self, channel):

        now = time.time()
        print "Enable quad {} channel {} at {}".format(self.id, channel, now)

def callbackFunction(value):
    print "callback", value

def create_partial(command, ignored, *args, **kwargs):
    return partial(command, *args, **kwargs)

if __name__ == '__main__':

    quads = [Quad(i) for i in range(4)]
    de = DeferredExecutor()

    for quad in quads:
        for channel in range(4):
            de.enqueue(quad.enable_channel, 1.0, channel)

    print de.pending()
    while de.pending():
        de.process()
        time.sleep(0.01)
