import os
import sys
import subprocess

reqs = ["selenium", "webdriver-manager", "colorama", "pyfiglet"]

def install_missing():
    for pkg in reqs:
        try:
            __import__(pkg.replace("-", "_"))
        except:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

install_missing()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import Fore, init
from pyfiglet import Figlet
import time

init(autoreset=True)

path = "C:/temp/chrome-profile"
os.makedirs(path, exist_ok=True)

def banner():
    f = Figlet(font='slant')
    print(Fore.CYAN + f.renderText("DISCORD CLEANER"))
    print(Fore.LIGHTMAGENTA_EX + "        >> AUTO FRIEND REMOVER <<\n")

def spinner(text="Waiting"):
    for c in "|/-\\":
        sys.stdout.write(Fore.YELLOW + f"\r{text} {c}")
        sys.stdout.flush()
        time.sleep(0.08)

class DiscordCleaner:

    def __init__(self):
        os.system("cls")
        banner()

        os.environ['WDM_LOG_LEVEL'] = '0'

        options = Options()
        options.add_argument(f"--user-data-dir={path}")
        options.add_argument("--start-maximized")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 30)

        self.removed = 0
        self.errors = 0

    def log(self, msg, color=Fore.WHITE):
        print(color + "[+] " + msg)

    def success(self, msg):
        print(Fore.GREEN + "[✔] " + msg)

    def warn(self, msg):
        print(Fore.YELLOW + "[!] " + msg)

    def error(self, msg):
        print(Fore.RED + "[X] " + msg)

    def stats(self):
        print(Fore.CYAN + f"[STATS] Removed: {self.removed} | Errors: {self.errors}")

    def open_discord(self):
        self.log("Opening Discord...", Fore.CYAN)
        self.driver.get("https://discord.com/app")

    def wait_login_auto(self):
        self.log("Waiting for login (auto-detect)...", Fore.MAGENTA)

        while True:
            spinner("Login pending")
            try:
                self.driver.find_element(By.XPATH, "//div[contains(@class,'peopleColumn')]")
                break
            except:
                pass

            if "/channels/@me" in self.driver.current_url:
                break

        print()
        self.success("Login detected")

    def go_to_friends(self):
        self.log("Navigating to Friends...", Fore.CYAN)
        self.driver.get("https://discord.com/channels/@me")

        self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'peopleColumn')]")))

    def switch_all(self):
        try:
            all_tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='All']")))
            self.driver.execute_script("arguments[0].click();", all_tab)
            self.success("Switched to ALL tab")
        except:
            self.warn("ALL tab not found")

    def load_all_friends(self):
        self.log("Scanning friends list...", Fore.CYAN)

        last_count = 0

        while True:
            users = self.driver.find_elements(By.XPATH, "//div[contains(@class,'peopleListItem')]")
            current_count = len(users)

            sys.stdout.write(Fore.LIGHTBLUE_EX + f"\rLoaded: {current_count}")
            sys.stdout.flush()

            if current_count == last_count:
                break

            last_count = current_count

            try:
                container = self.driver.find_element(By.XPATH, "//div[contains(@class,'peopleList')]")
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            except:
                self.driver.execute_script("window.scrollBy(0,1000)")

        print()
        self.success(f"Total friends: {current_count}")

    def auto_wait_popup(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']")))
        except:
            pass

        try:
            self.wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[@role='dialog']")))
            return True
        except:
            return False

    def semi_auto_remove(self):
        print(Fore.CYAN + "\n" + "="*60)
        print(Fore.LIGHTMAGENTA_EX + "        >> CONTROL MODE ACTIVE <<")
        print(Fore.CYAN + "="*60)
        print(Fore.WHITE + "Click REMOVE / CANCEL → script continues instantly\n")

        users = self.driver.find_elements(By.XPATH, "//div[contains(@class,'peopleListItem')]")

        for i in range(len(users)):
            try:
                users = self.driver.find_elements(By.XPATH, "//div[contains(@class,'peopleListItem')]")
                user = users[i]

                print(Fore.YELLOW + f"\n[USER {i+1}]")

                menu = user.find_element(By.XPATH, ".//div[@aria-label='More']")
                self.driver.execute_script("arguments[0].click();", menu)

                remove = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@role='menuitem']//div[text()='Remove Friend']"))
                )
                remove.click()

                if self.auto_wait_popup():
                    self.removed += 1
                    self.success("Done")
                else:
                    self.errors += 1
                    self.warn("Popup issue")

                self.stats()

            except Exception as e:
                self.errors += 1
                self.error(str(e))
                continue

        self.success("Completed all users")

    def close(self):
        print(Fore.CYAN + "\nSession finished.")
        input(Fore.WHITE + "[>] Press ENTER to exit...")
        self.driver.quit()

if __name__ == "__main__":
    app = DiscordCleaner()
    app.open_discord()
    app.wait_login_auto()
    app.go_to_friends()
    app.switch_all()
    app.load_all_friends()
    app.semi_auto_remove()
    app.close()