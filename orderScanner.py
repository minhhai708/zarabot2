import os
import sys
import time
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Account import AccountList
from Invoice import Invoice

WAIT_TIME = 20


class ActionRet(enumerate):
    SUCCESSFUL = 1
    UNSUCCESSFUL = -1


class Downloader(object):
    def __init__(self, dateLimit, client):
        # Configure browser
        folderInvoice = os.getcwd() + "/" + client
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.dir", folderInvoice)
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", 'application/pdf ')

        self.browser = webdriver.Firefox(profile)

        # Max date to download
        self.dateLimit = dateLimit

        # Log file location
        self.logFile = os.getcwd() + '/Log/' + datetime.now().strftime("%d_%m_%Y_%H:%M:%S") + '.csv'

        # Current invoice page location
        self.currentpage = 1

        #Accountlocation
        self.accList = AccountList(fileName='ACCOUNT/' + client + '.csv')
        self.outofInvocie = False
        self.isfinalpage = False

    def logout(self):
        self.browser.get("https://www.zara.com/es/es/session/logout")

    def goto_NextInvoicePage(self):
        browser = self.browser
        WebDriverWait(browser, WAIT_TIME).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "list-std__footer")))
        pageIndex = browser.find_element_by_class_name('list-std__footer')
        print("Page line:", pageIndex.text)
        currentPage = int(pageIndex.text.split()[1])
        totalPage = int(pageIndex.text.split()[3])
        # Check if we are in the final invoice page
        print("Current page ", currentPage, '/', totalPage)

        if currentPage == totalPage:
            self.isfinalpage = True
        else:
            next_page = "https://www.zara.com/es/en/user/invoice#" + str(currentPage + 1)
            # If we are not in the final page, move to the next page
            browser.get(next_page)
            return ActionRet.SUCCESSFUL

    def login(self, account):
        """
        This funtion will login and check if login is successful by go to menu of user and see all
        """
        self.isfinalpage = False
        self.outofInvocie = False
        self.currentpage = 1

        email = account.getEmail()
        password = account.getPassword()
        browser = self.browser
        attempt = 0
        while attempt < 3:
            try:
                browser.get("https://www.zara.com/es/en/logon")
                time.sleep(3)
                browser.implicitly_wait(3)
                WebDriverWait(browser, WAIT_TIME).until(
                    EC.presence_of_all_elements_located((By.ID, 'form-input__label-email')))
                emailUser = browser.find_element_by_name('email')  # Find the search box
                passwordUser = browser.find_element_by_name('password')
                print("Log in :" + email)
                emailUser.send_keys(email)
                passwordUser.send_keys(password + Keys.RETURN)
                if self.isLoggedIn(account):
                    return True
                else:
                    return False
            except (TimeoutException, StaleElementReferenceException, ElementClickInterceptedException,
                    WebDriverException) as exception:
                print(repr(exception), " ErrorLogin ", email)
                attempt = attempt + 1
        return False

    def isLoggedIn(self, account):
        browser = self.browser
        time.sleep(3)
        browser.implicitly_wait(3)
        browser.get("https://www.zara.com/es/en/user/invoice")
        try:
            WebDriverWait(browser, WAIT_TIME).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "layout__article")))
            WebDriverWait(browser, WAIT_TIME).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "invoice-list-item__button")))

            # Check if all elements of menu present
            invoicedate = browser.find_elements_by_class_name("invoice-list-item__date")
            orders = browser.find_elements_by_class_name("invoice-list-item__order")
            amounts = browser.find_elements_by_class_name("invoice-list-item__amount")
            links = browser.find_elements_by_class_name("invoice-list-item__button")
            return True
        except (TimeoutException, StaleElementReferenceException, ElementClickInterceptedException,
                NoSuchElementException) as exception:
            print(repr(exception), "Is not logged in")
            return False

    def click_InvoiceLink(self, account):
        browser = self.browser
        fout = self.logFile
        dateLimit = self.dateLimit

        wait_element = 20
        attempt = 0
        while attempt < 3:
            try:
                time.sleep(3)
                WebDriverWait(browser, wait_element).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "layout__article")))
                WebDriverWait(browser, wait_element).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "invoice-list-item__button")))
                WebDriverWait(browser, wait_element).until(
                    EC.presence_of_all_elements_located(
                        (By.CLASS_NAME, "button.button--secondary.button--small.invoice-list-item__button")))

                invoicedate = browser.find_elements_by_class_name("invoice-list-item__date")
                orders = browser.find_elements_by_class_name("invoice-list-item__order")
                amounts = browser.find_elements_by_class_name("invoice-list-item__amount")
                links = browser.find_elements_by_class_name("invoice-list-item__button")
                listhref = [elem.get_attribute('href') for elem in links]

                # Download all invoice
                for i in range(len(orders)):
                    inv = Invoice(invoicedate[i].text, orders[i].text, amounts[i].text, listhref[i], account)
                    # invoice invoice date is lower than limit date then finish
                    if inv.isOutdated(dateLimit):
                        print("END.")
                        self.outofInvocie = True
                        return ActionRet.SUCCESSFUL
                    print('Downloading...' + str(inv))
                    links[i].click()
                    # links[i].send_keys(Keys.CONTROL + Keys.RETURN)
                    time.sleep(3)
                    inv.export_csv(fout)
                time.sleep(2)
                self.goto_NextInvoicePage()
                return ActionRet.SUCCESSFUL
            except (TimeoutException,
                    StaleElementReferenceException,
                    ElementClickInterceptedException,
                    NoSuchElementException) as exception:
                attempt += 1
                print(repr(exception), " clickDownloadLinks ")
        return ActionRet.UNSUCCESSFUL

    def downloadInvoiceByAccount(self, account):
        # If password and email is wrong
        if self.login(account) == False:
            return
        # Go to the first invoice page
        while (self.outofInvocie == False and self.isfinalpage == False):
            if self.click_InvoiceLink(account) == ActionRet.UNSUCCESSFUL:
                self.logout()
                return ActionRet.UNSUCCESSFUL

        self.logout()
        return ActionRet.SUCCESSFUL

    def execute(self):
        # Configure browser
        # create list of account from a file
        first_page = 'https://www.zara.com/es/en/'
        browser = self.browser
        for account in self.accList.getAccList():
            browser.get(first_page)
            self.downloadInvoiceByAccount(account)

        browser.close()


def main(argv):
    # dateLimit = input("nhap MM/DD/YYYY:")
    # client = "THUY"

    client = input("File Account: ")
    dateLimit = "01/01/2021"
    action = Downloader(dateLimit, client)
    input("Please check autoDownload pdf")
    action.execute()
    return

if __name__ == '__main__': sys.exit(main(sys.argv))
