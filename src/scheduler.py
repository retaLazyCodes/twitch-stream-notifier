import schedule
import time


class TaskScheduler:
    def __init__(self, interval_minutes=1):
        self.interval = interval_minutes

    def schedule_task(self, task_function):
        """Programa una función para que se ejecute a un intervalo fijo."""
        schedule.every(self.interval).minutes.do(task_function)

    def run_pending_tasks(self):
        """Ejecuta las tareas pendientes en un bucle."""
        while True:
            schedule.run_pending()
            time.sleep(1)
