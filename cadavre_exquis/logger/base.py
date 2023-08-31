import tkinter as tk
import asyncio
import random

class CoroutineLogger:
    def __init__(self, root, rows, cols):
        self.root = root
        self.rows = rows
        self.cols = cols
        self._configure_grid()
        self.text_widgets = self._create_text_widgets()
        self.queues = [asyncio.Queue() for _ in range(rows * cols)]

    def _configure_grid(self):
        for i in range(self.rows):
            self.root.grid_rowconfigure(i, weight=1)
        for j in range(self.cols):
            self.root.grid_columnconfigure(j, weight=1)

    def _create_text_widgets(self):
        widgets = []
        for i in range(self.rows):
            for j in range(self.cols):
                text_widget = tk.Text(self.root)
                text_widget.grid(row=i, column=j, sticky="nsew")  # Sticky to all sides
                widgets.append(text_widget)
        return widgets

    async def _coroutine(self, queue, idx):
        while True:
            await asyncio.sleep(1)
            await queue.put(f"Coroutine {idx}: {random.randint(1, 100)}")

    async def _update_text_widget(self, text_widget, queue):
        while True:
            line = await queue.get()
            text_widget.insert(tk.END, line + "\n")
            text_widget.see(tk.END)

    def start(self, loop):
        for idx, (text_widget, queue) in enumerate(zip(self.text_widgets, self.queues)):
            loop.create_task(self._update_text_widget(text_widget, queue))
            loop.create_task(self._coroutine(queue, idx + 1))
        
        while True:
            self.root.update_idletasks()
            self.root.update()
            loop.run_until_complete(asyncio.sleep(0.01))

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Coroutine Logs")

    logger = CoroutineLogger(root, rows=3, cols=2)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(logger.start(loop))
