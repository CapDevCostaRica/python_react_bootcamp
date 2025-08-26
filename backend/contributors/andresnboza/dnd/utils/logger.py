def log_message(message):
    """
    Appends a message to logs.txt in the current directory.
    Usage: log_message('your message')
    """
    with open('logs.txt', 'a') as f:
        f.write(str(message) + '\n')
