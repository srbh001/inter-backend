GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"


GIN = f"{GREEN}[INFO]:  {RESET} "
ERR = f"{RED}[ERROR]:   {RESET} "
TST = f"{GREEN}[TEST]:  {RESET} "
WARN = f"{YELLOW}[WARNING]:  {RESET} "


def sprint(msg, type="i"):
    if type == "w":
        print(WARN, msg)
    elif type == "e":
        print(ERR, msg)
    else:
        print(GIN, msg)
