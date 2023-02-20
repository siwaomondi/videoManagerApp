from ui import VideoManager
import sys
import os
basedir = os.path.dirname(__file__)
log_text = os.path.join(basedir, "vidman_logs/log.txt")
output = open(log_text, "wt")
sys.stdout = output
sys.stderr = output
if __name__ == "__main__":
    app = VideoManager()
output.close()