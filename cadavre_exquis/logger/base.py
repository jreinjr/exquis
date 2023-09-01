import tkinter as tk
import asyncio
import random

class TextWidgetManager:
    """Manages dynamic creation and placement of Text widgets in the GUI."""
    
    def __init__(self, root, max_rows=6):
        self.root = root
        self.text_widgets = []
        self.max_rows = max_rows

    def create_text_widget(self):
        total_widgets = len(self.text_widgets)
        rows = total_widgets % self.max_rows + 1
        cols = total_widgets // self.max_rows

        if rows == 1:
            self.root.grid_columnconfigure(cols, weight=1)
        self.root.grid_rowconfigure(rows - 1, weight=1)

        text_widget = tk.Text(self.root)
        text_widget.grid(row=rows - 1, column=cols, sticky="nsew")
        self.text_widgets.append(text_widget)

        return text_widget

class CoroutineLogger:
    """Listens to an event queue and logs results from coroutines into Text widgets."""

    def __init__(self, root, event_queue, max_rows=6):
        self.root = root
        self.event_queue = event_queue
        self.text_manager = TextWidgetManager(root, max_rows)
        self.coroutine_queues = []

    async def _update_text_widget(self, text_widget, coroutine_queue):
        while True:
            line = await coroutine_queue.get()
            text_widget.insert(tk.END, line + "\n")
            text_widget.see(tk.END)

    async def process_events(self):
        while True:
            try:
                coroutine_func, args = self.event_queue.get_nowait()
                text_widget = self.text_manager.create_text_widget()
                coroutine_queue = asyncio.Queue()
                self.coroutine_queues.append(coroutine_queue)
                asyncio.create_task(self._update_text_widget(text_widget, coroutine_queue))
                asyncio.create_task(coroutine_func(*args, coroutine_queue))
            except asyncio.QueueEmpty:
                pass
            self.root.update_idletasks()
            self.root.update()
            await asyncio.sleep(0.01)

    async def start(self):
        await asyncio.gather(self.process_events())


async def sample_coroutine(ix, queue):
    """Sample coroutine that sends random integers to a queue."""
    while True:
        await asyncio.sleep(1)
        await queue.put(f"Sample Coroutine {ix}: {random.randint(1, 100)}")


async def endless_loop(event_queue):
    """Endlessly adds coroutines to an event queue."""
    ix = 0
    while True:
        event_queue.put_nowait((sample_coroutine, (ix,)))
        ix += 1
        await asyncio.sleep(1)


def setup_gui():
    root = tk.Tk()
    root.title("Coroutine Logs")
    return root


if __name__ == '__main__':
    root = setup_gui()
    event_queue = asyncio.Queue()
    logger = CoroutineLogger(root, event_queue)

    loop = asyncio.get_event_loop()
    loop.create_task(endless_loop(event_queue))
    loop.run_until_complete(logger.start())
