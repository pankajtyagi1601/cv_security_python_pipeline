# events/event_queue.py
from queue import Queue

# Shared queue between camera threads (producers)
# and event_worker thread (consumer)
event_queue = Queue()