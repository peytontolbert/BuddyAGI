import os
import psycopg2
import subprocess
from dotenv import load_dotenv
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
load_dotenv()
class BrowserAgentTools:
    def __init__(self):
        self.driver = None  # Selenium WebDriver
        # Get the absolute path of the directory where main.py is located
        main_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the path to the workingspace folder
        self.working_dir = os.path.join(main_dir, 'workingspace')
        
    def launch_browser(self):
        try:
            self.driver = webdriver.Chrome()  # Use Chrome; ensure driver is installed
            self.driver.maximize_window()
            return "Browser launched successfully."
        except Exception as e:
            return f"An error occurred while launching the browser: {e}"

    def find_and_click_link(self, link_text):
        try:
            links = self.driver.find_elements(By.XPATH, "//a[@href]")
            for link in links:
                if link_text in link.get_attribute("innerHTML"):
                    link.click()
                    return f"Clicked on link containing '{link_text}'."
            return f"No link containing '{link_text}' found."
        except NoSuchElementException:
            return "Element not found."
        except Exception as e:
            return f"An error occurred: {e}"
        
    def navigate_to_url(self, url):
        try:
            self.driver.get(url)
            return f"Navigated to {url} successfully."
        except Exception as e:
            return f"An error occurred while navigating to {url}: {e}"

    def click_at_coordinates(self, x, y):
        try:
            action = ActionChains(self.driver)
            action.move_by_offset(x, y).click().perform()
            return f"Clicked at coordinates ({x}, {y}) successfully."
        except Exception as e:
            return f"An error occurred while clicking: {e}"

    def type_text(self, text):
        try:
            action = ActionChains(self.driver)
            action.send_keys(text).perform()
            return f"Typed text '{text}' successfully."
        except Exception as e:
            return f"An error occurred while typing text: {e}"

    def take_screenshot(self, filename):
        filepath = os.path.join(os.getcwd(), filename)
        try:
            self.driver.save_screenshot(filepath)
            return f"Screenshot saved as '{filename}'."
        except Exception as e:
            return f"An error occurred while taking screenshot: {e}"

    def close_browser(self):
        try:
            self.driver.quit()
            return "Browser closed successfully."
        except Exception as e:
            return f"An error occurred while closing the browser: {e}"

    