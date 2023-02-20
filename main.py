from ui import VideoManager
import sys
output = open("output.txt", "wt")
sys.stdout = output
sys.stderr = output
if __name__ == "__main__":
    app = VideoManager()
output.close()