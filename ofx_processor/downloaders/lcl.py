import time
from pathlib import Path

import click
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from ofx_processor.utils.config import (
    get_config,
    get_config_file_name,
    handle_config_file_error,
)


class LclDownloader:
    def __init__(self, download_folder: Path = None):
        self.config = get_config("lcl")
        if not self.config.bank_identifier or not self.config.bank_password:
            handle_config_file_error(
                get_config_file_name(), "Missing credentials in config file"
            )

        if not download_folder:
            download_folder = Path.home() / "Downloads"
        self.download_folder = download_folder.resolve()
        options = webdriver.FirefoxOptions()
        options.headless = True
        options.set_preference("browser.download.dir", str(self.download_folder))
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk", "application/x-ofx"
        )
        self.selenium = webdriver.Firefox(options=options)
        self.selenium.implicitly_wait(30)

    def download(self) -> str:
        selenium = self.selenium

        click.secho("Logging in to LCL...", fg="blue")
        selenium.get("https://monespace.lcl.fr/connexion")
        try:
            self._click(By.ID, "popin_tc_privacy_button_2")
        except:
            # If the user has already accepted the privacy policy,
            # the button is not present
            pass
        login_input = selenium.find_element(By.ID, "identifier")
        login_input.send_keys(self.config.bank_identifier)
        self._click(By.CLASS_NAME, "app-cta-button")
        for char in self.config.bank_password:
            self._click(By.CSS_SELECTOR, f".pad-button[value='{char}']")
        self._click(By.CLASS_NAME, "app-cta-button")
        click.secho("Logged in!", fg="green")

        click.secho("Navigating through archives...", fg="blue")
        self._click(By.ID, "linkSynthese")
        self._click(By.CLASS_NAME, "picDl")
        self._select(By.ID, "change", index=1)
        self._select(By.ID, "DS", index=20)
        self._click(By.ID, "MON04")
        self._click(By.ID, "Valider")
        click.secho("Found it!", fg="green")
        selenium.get("about:downloads")
        return self._get_last_download_file_name()

    def _click(self, by: By, value: str):
        self.selenium.find_element(by, value).click()

    def _select(self, by: By, value: str, index: int):
        Select(self.selenium.find_element(by, value)).select_by_index(index)

    def _get_last_download_file_name(self, wait_seconds: int = 30):
        end_time = time.time() + wait_seconds
        while time.time() < end_time:
            try:
                file_name = self.selenium.execute_script(
                    "return document.querySelector('#contentAreaDownloadsView .downloadMainArea .downloadContainer description:nth-of-type(1)').value"
                )
                if file_name:
                    return self.download_folder / file_name
            except:
                pass
            time.sleep(1)


if __name__ == "__main__":
    filename = LclDownloader().download()
    print(filename)
