import time, os
from swibots import DownloadProgress, Message, UploadProgress
from functions.parsers import format_file_size

def get_progress_bar(pct):
    p = min(max(pct, 0), 100)
    cFull = int(p // 8)
    p_str = "█" * cFull
    p_str += "░" * (12 - cFull)
    return f"[{p_str}]"


async def download_progress(
    prog: DownloadProgress, message: Message, text: str = "Downloading..."
):
    perc = (prog.downloaded / prog.total) * 100
    await message.edit_text(
        f"""{text} {prog.file_name}
[{format_file_size(prog.downloaded)} of {format_file_size(prog.total)}]

{get_progress_bar(perc)} {perc:.2f}%
"""
    )


async def upload_progress(
    prog: UploadProgress, message: Message, can_send
):
    if can_send and not can_send():
        return
    perc = (prog.readed / prog.total) * 100
    await message.edit_text(
        f"""⬆️ *Uploading* <copy>{os.path.basename(prog.path)}</copy>

[{format_file_size(prog.readed)} of {format_file_size(prog.total)}]
{get_progress_bar(perc)} {perc:.2f}%"""
    )


class Timer:
    def __init__(self, time_between=2):
        self.start_time = time.time()
        self.time_between = time_between

    def can_send(self):
        if time.time() > (self.start_time + self.time_between):
            self.start_time = time.time()
            return True
        return False