from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import re

path = input("Input link txt path: ")
firefox_services = Service(executable_path='./firefoxdriver/geckodriver.exe',
                           port=3000,
                           service_args=['--marionette-port', '2828', '--connect-existing'])

driver = webdriver.Firefox(service=firefox_services)

def readLinks(path):
    txt = open(path, "r")

    for line in txt.readlines():
        if line.startswith("blackboard"):
            print("collecting blackboard...")
            credentials = (line.split("blackboard: "))[1]
            username = (credentials.split(";"))[0]
            password = (credentials.split(";"))[1]
            openBlackboard(username, password)
        if line.startswith("gradescope"):
            print("collecting gradescope...")
            link = (line.split("gradescope: ")[1])
            collectGradescope(link)
        if line.startswith("webwork"):
            print("collecting webwork...")
            link = (line.split("webwork: ")[1])
            collectWebwork(link)
    txt.close()

def openBlackboard(username, password):
    driver.get("https://learn.rochester.edu/auth-saml/saml/login?apId=_1567_1&redirectUr"
               "l=https%3A%2F%2Flearn.rochester.edu%2Fultra%2Finstitution-page")
    try:
        WebDriverWait(driver, 15).until(
            ec.presence_of_element_located((By.ID, "usernamevis"))
        )
    finally:
        usernameBox = driver.find_element(By.ID, "usernamevis")
        usernameBox.send_keys(username)

        passwordBox = driver.find_element(By.ID, "password")
        passwordBox.send_keys(password)

        login = driver.find_element(By.ID, "log-on")
        login.click()

    try:
        WebDriverWait(driver, 15).until(
            ec.presence_of_element_located((By.CLASS_NAME, "modules-container"))
        )
    finally:
        pass


def collectGradescope(url):
    driver.get(url)
    ariaPattern = re.compile(r'aria-label=\"View.*\"')

    try:
        WebDriverWait(driver, 15).until(
            ec.presence_of_element_located((By.ID, "assignments-student-table"))
        )
    finally:
        first = driver.find_element(By.CLASS_NAME, "even")
        second = driver.find_element(By.CLASS_NAME, "odd")

    if first.find_element(By.CLASS_NAME, "submissionStatus--text").get_attribute("innerHTML") == "No Submission":
        title = ariaPattern.findall(first.get_attribute("innerHTML"))
        title = (title[0].split("View "))[1].split("\"")[0]

        date = first.find_element(By.CLASS_NAME, "submissionTimeChart--dueDate").get_attribute("innerHTML")
        print(title, "due", date)


    if second.find_element(By.CLASS_NAME, "submissionStatus--text").get_attribute("innerHTML") == "No Submission":
        title = ariaPattern.findall(second.get_attribute("innerHTML"))
        title = (title[0].split("View "))[1].split("\"")[0]

        date = first.find_element(By.CLASS_NAME, "submissionTimeChart--dueDate").get_attribute("innerHTML")
        print(title, "due", date)


def collectWebwork(url):
    driver.get(url)

    try:
        WebDriverWait(driver, 15).until(
            ec.presence_of_element_located((By.CLASS_NAME, "page-title"))
        )
    finally:
        rows = driver.find_elements(By.XPATH, "//tr")

    contents = rows[1].find_elements(By.XPATH, "//td")

    status = contents[2].get_attribute("innerHTML")
    title = contents[1].find_element(By.CLASS_NAME, "set-id-tooltip").get_attribute("innerHTML")

    if status.startswith("Open"):
        time = status.split("closes ")
        print(title, "due", (time[1].split("pm"))[0])

readLinks(path)
driver.close()
