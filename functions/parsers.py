def parse_ms(milliseconds):
    seconds = int((milliseconds / 1000) % 60)
    minutes = int((milliseconds / (1000 * 60)) % 60)
    hours = int((milliseconds / (1000 * 60 * 60)) % 24)
    days = int((milliseconds / (1000 * 60 * 60 * 24)) % 365)

    result = ""
    if days > 0:
        result += f"{days}d "
    if hours > 0:
        result += f"{hours}h "
    if minutes > 0:
        result += f"{minutes}m "
    if seconds > 0:
        result += f"{seconds}s"

    return result.strip()


def format_file_size(file_size):
    units = ["B", "KB", "MB", "GB", "TB"]
    index = 0

    while file_size >= 1024 and index < len(units) - 1:
        file_size /= 1024
        index += 1

    return f"{file_size:.2f} {units[index]}"
