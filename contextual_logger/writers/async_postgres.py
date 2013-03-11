from Queue import Queue
import threading
import psycopg2
from contextual_logger.writers.norm import INSERT

LOG_QUEUE = Queue()


def write(row):
    LOG_QUEUE.put_nowait(row)


def writer_thread(database_config):
    conn = psycopg2.connect(**database_config)
    conn.autocommit = True
    cur = conn.cursor()

    while True:
        row = LOG_QUEUE.get()
        for k, v in row.items():
            row[k] = str(v)
        q = INSERT('logs', data=row)
        cur.execute(q.query, q.binds)


def init_writer_threads(db_config, threads=5):
    for i in range(threads):
        t = threading.Thread(target=writer_thread, args=(db_config,))
        t.start()