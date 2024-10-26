import _thread

class Queue:
    def __init__(self):
        self.queue = []
        self.lock = _thread.allocate_lock()

    def put(self, item):
        # Añadir un item a la cola de manera segura
        with self.lock:
            self.queue.append(item)

    def get(self):
        # Obtener un item de la cola de manera segura
        with self.lock:
            if len(self.queue) > 0:
                return self.queue.pop(0)
            else:
                return None

    def empty(self):
        # Verificar si la cola está vacía de manera segura
        with self.lock:
            return len(self.queue) == 0