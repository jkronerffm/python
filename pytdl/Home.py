from pathlib import Path

class Home:
    def __call__(self):
        return str(Path.home())

if __name__ == "__main__":
    home = Home()
    print(home())
