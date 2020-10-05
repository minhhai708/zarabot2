import os
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Account import AccountList
from Invoice import Invoice

WAIT_TIME = 3
TRUE = 1
FALSE = 0


class ActionResult(enumerate):
    OUT_OF_INVOICE = 2
    IS_FINAL_PAGE = 2
    SUCCESSFUL = 1
    UNSUCCESSFUL = -1
    ERROR_CLICK_LOGIN = -2
    ERROR_LOGIN = -3
    ERROR_CLICK_ACCOUNTMENU = -4
    ERROR_CLICK_INVOICE = -5
    ERROR_LOG_OUT = -6
    ERROR_TIMEOUT = -7


class Downloader(object):
    def __int__(self):
        self.dateLimit = None
        self.client = None
        self.logFile = None
        self.browser = None

    def setUp(self, dateLimit, pathName):
        self.dateLimit = dateLimit
        self.client = pathName
        self.logFile = "InvoiceLog.csv"

        # Configure browser
        folderInvoice = os.getcwd() + "/" + pathName
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.dir", folderInvoice)
        self.browser = webdriver.Firefox(profile)

    def logIn(self, email, password):
        browser = self.browser
        try:
            browser.get("https://www.zara.com/es/en/logon")
            WebDriverWait(browser, WAIT_TIME).until(
                EC.presence_of_all_elements_located((By.ID, 'form-input__label-email')))
            emailUser = browser.find_element_by_name('email')  # Find the search box
            passwordUser = browser.find_element_by_name('password')
            print("Log in :" + email)
            emailUser.send_keys(email)
            passwordUser.send_keys(password + Keys.RETURN)
            time.sleep(1)
            try:
                ele = browser.find_element_by_class_name("")
                return ActionResult.UNSUCCESSFUL
            except NoSuchElementException:
                return ActionResult.SUCCESSFUL
        except NoSuchElementException:
            print("Unable to login " + email)
            return ActionResult.ERROR_CLICK_LOGIN
        except TimeoutException:
            print("TimeoutException - LOGIN")
            return ActionResult.ERROR_CLICK_LOGIN
        except WebDriverException:
            print("WebDriverException- LOGIN")
            return ActionResult.ERROR_CLICK_LOGIN

    def logout(self):
        self.browser.get("https://www.zara.com/es/es/session/logout")

    def move_InvoicePage(self,numpage):
        browser = self.browser
        browser.implicitly_wait(WAIT_TIME)
        browser.get("https://www.zara.com/es/en/user/invoice#"+str(numpage))

    def move_NextInvoicePage(self):
        browser = self.browser
        pageIndex = browser.find_elements_by_class_name('list-std__footer')
        currentPage = int(pageIndex.text.split()[1])
        totalPage = int(pageIndex.text.split()[3])
        # Check if we are in the final invoice page
        if currentPage == totalPage:
            print("Current page "+pageIndex.text.split()[1] +'/'+pageIndex.text.split()[3])
            return ActionResult.IS_FINAL_PAGE
        else:
            # If we are not in the final page, move to the next page
            self.move_InvoicePage(currentPage +1)
            return ActionResult.SUCCESSFUL

    def click_InvoiceLink(self, account):
        browser = self.browser
        contentTable = "layout__article"
        moreInvoice = True
        fout = self.logFile
        dateLimit = self.dateLimit
        ret = ActionResult.SUCCESSFUL
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.presence_of_all_elements_located((By.CLASS_NAME, contentTable)))
            invoicedate = browser.find_elements_by_class_name("invoice-list-item__date")
            orders = browser.find_elements_by_class_name("invoice-list-item__order")
            amounts = browser.find_elements_by_class_name("invoice-list-item__amount")
            links = browser.find_elements_by_class_name("invoice-list-item__button")
            for i in range(len(orders)):
                inv = Invoice(invoicedate[i].text, orders[i].text, amounts[i].text, account)
                if not inv.isOutdated(dateLimit):
                    print('Downloading...' + str(inv) + str(inv.isOutdated(dateLimit)))
                    inv.export_csv(fout)
                    links[i].click()
                    browser.implicitly_wait(WAIT_TIME)
                else:
                    ret = ActionResult.OUT_OF_INVOICE
        except (TimeoutException):
            print("TimeoutException-clickDownloadLinks")
            ret = ActionResult.UNSUCCESSFUL
        except (IndexError):
            print("IndexError-clickDownloadLinks")
            ret = ActionResult.UNSUCCESSFUL
        except (NoSuchElementException):
            print("NoSuchElementException-clickDownloadLinks")
            ret = ActionResult.UNSUCCESSFUL

        return ret

    def getInvoiceByAccount(self, account):
        print("getInvoiceByAccount")
        # If password and email is wrong

        attempt = 0
        while attempt < 3:
            if self.logIn(account.getEmail(), account.getPassword()) == ActionResult.SUCCESSFUL:
                break
            else:
                attempt += 1

        self.move_InvoicePage(1)
        isFinalPage = ActionResult.SUCCESSFUL
        invoiceIsOutdated = ActionResult.SUCCESSFUL
        while 1:
            if isFinalPage == ActionResult.IS_FINAL_PAGE or invoiceIsOutdated == ActionResult.OUT_OF_INVOICE:
                break
            else:
                invoiceIsOutdated = self.click_InvoiceLink(account)
                isFinalPage = self.move_NextInvoicePage()
        self.logout()
        return ActionResult.SUCCESSFUL

    def startDownloader(self, accList):
        # Configure browser
        # create list of account from a file
        first_page = 'https://www.zara.com/es/en/'
        browser = self.browser
        browser.get(first_page)
        input("Please check autoDownload pdf")
        for account in accList:
            self.getInvoiceByAccount(account)
            browser.get(first_page)
        browser.close()


def main(argv):
    # dateLimit = input("nhap MM/DD/YYYY:")
    # client = input("File Account: ")
    dateLimit = "09/01/2020"
    path = "THUY"

    accList = AccountList(fileName='ACCOUNT/' + path + '.csv')

    action = Downloader()
    action.setUp(dateLimit, path)

    action.startDownloader(accList.getAccList())

    return


if __name__ == '__main__': sys.exit(main(sys.argv))
