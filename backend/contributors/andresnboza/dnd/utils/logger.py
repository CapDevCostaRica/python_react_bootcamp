import os

def log_message(message):
    # Get the absolute path to the dnd folder
    dnd_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(dnd_dir, '..', 'logs.txt')
    with open(log_path, 'a') as f:
        f.write(str(message) + '\n')