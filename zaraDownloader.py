
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from Account import AccountList
from Tools import Tools
import os

WAIT_TIME = 5
TRUE = 1
FALSE = 0

class InvoiceErrorReturn(enumerate):
    SUCCESSFUL = 1
    UNSUCCESSFUL = -1
    ERROR_CLICK_LOGIN = -2
    ERROR_LOGIN = -3
    ERROR_CLICK_ACCOUNTMENU = -4
    ERROR_CLICK_INVOICE = -5
    ERROR_LOG_OUT = -6
class ZaraDownloader(object):
    def clickLogIn(self, browser):
        loginLink = '_accountLink._login'
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.CLASS_NAME, loginLink)))
            browser.find_element_by_class_name(loginLink).click()
            return InvoiceErrorReturn.SUCCESSFUL
        except NoSuchElementException:
            print("NoSuchElementException- clickLogIn")
            return InvoiceErrorReturn.ERROR_CLICK_LOGIN
        except TimeoutException:
            print("TIME OUT")
            return InvoiceErrorReturn.ERROR_CLICK_LOGIN

    def logIn(self, browser, email, password):
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.presence_of_all_elements_located((By.ID, 'sign-in-form')))
            emailUser = browser.find_element_by_id('email')  # Find the search box
            passwordUser = browser.find_element_by_id('password')
            print("Log in :" +email)
            emailUser.send_keys(email)
            passwordUser.send_keys(password + Keys.RETURN)
        except NoSuchElementException:
            print("Unable to login "+ email)
            return InvoiceErrorReturn.ERROR_LOGIN
        except TimeoutException:
            return InvoiceErrorReturn.ERROR_LOGIN
    def clickAccountMenu(self, browser):
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.CLASS_NAME, '_accountLink._userName')))
            browser.find_element_by_class_name('_accountLink._userName').click()
            return InvoiceErrorReturn.SUCCESSFUL
        except NoSuchElementException:
            print("NoSuchElementException- clickAccountMenu")
            return InvoiceErrorReturn.ERROR_CLICK_ACCOUNTMENU
        except TimeoutException:
            print("TimeoutException- clickAccountMenu")
            return InvoiceErrorReturn.ERROR_CLICK_ACCOUNTMENU

    def clickLogOut(self, browser):
        logOutLink = '_accountLink._logout'
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.CLASS_NAME, logOutLink)))
            browser.find_element_by_class_name(logOutLink).click()
            InvoiceErrorReturn.SUCCESSFUL
        except NoSuchElementException:
            print("NoSuchElementException- clickLogOut")
            return InvoiceErrorReturn.ERROR_LOG_OUT
        except TimeoutException:
            print("TimeoutException- clickLogOut")
            return InvoiceErrorReturn.ERROR_LOG_OUT

    def clickInvoices(self, browser):
        invoicesLink = "Invoices"
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, invoicesLink)))
            browser.find_element_by_partial_link_text(invoicesLink).click()
            return InvoiceErrorReturn.SUCCESSFUL
        except (NoSuchElementException, TimeoutException):
            print("Exception - clickInvoices")
            return InvoiceErrorReturn.ERROR_CLICK_INVOICE


    def clickNextInvoicePage(self, browser):
        nextpage = 'icon-arrow-right._table-nav-next._prevPage'
        isFinalPage = False
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.CLASS_NAME, nextpage)))
            browser.find_element_by_class_name(nextpage).click()
            return isFinalPage
        except TimeoutException:
            print("MOVE TO FINAL PAGE")
            isFinalPage = True
            return isFinalPage
        except NoSuchElementException:
            print("NoSuchElementException- move_NextPage")
            isFinalPage = True
            return isFinalPage


    def clickDownloadInvoice(self, browser, dateLimit, account, outputfile):
        invoicesDownload = "button-primary.button-medium._invoice-download"
        downloadText = "Download"
        contentTable = "content-dotted-table.invoice-list-table"
        tbodyTAG = "tbody"
        moreInvoice = True

        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.presence_of_all_elements_located((By.CLASS_NAME, contentTable)))
            WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, downloadText)))
            tbodyEle = browser.find_element_by_tag_name(tbodyTAG)
            links = browser.find_elements_by_class_name(invoicesDownload)
            linkList = Tools.zaraGetDownloadIndexByDate(tbodyEle.text, dateLimit)

            if not linkList:
                moreInvoice = False
                return moreInvoice
            print(linkList)
            for linkIndex in linkList:
                attempt = 1
                while attempt < 3:
                    try:
                        WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, downloadText)))
                        print("Downloading " + tbodyEle.text.splitlines()[linkIndex])
                        links[linkIndex].click()
                        Tools.invoiceWriter(account, tbodyEle.text.splitlines()[linkIndex]+ " "+links[linkIndex].get_attribute("href"), outputfile)

                        break
                    except StaleElementReferenceException:
                        browser.implicitly_wait(WAIT_TIME)
                        attempt = attempt + 1
            return moreInvoice

        except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
            print("Exception-clickDownloadInvoice")
            return


    def getInvoiceByAccount(self, browser, account, dateLimit, outputfile):
        attempt = 0
        try:
            isFinalPage = False
            moreInvoice = True
            if self.clickLogIn(browser) == InvoiceErrorReturn.ERROR_CLICK_LOGIN:
                return InvoiceErrorReturn.ERROR_CLICK_LOGIN
            if self.logIn(browser, account.getEmail(), account.getPassword()) == InvoiceErrorReturn.ERROR_LOGIN:
                return InvoiceErrorReturn.ERROR_LOGIN
            if self.clickAccountMenu(browser) == InvoiceErrorReturn.ERROR_CLICK_ACCOUNTMENU:
                self.clickLogOut(browser)
                return InvoiceErrorReturn.ERROR_CLICK_ACCOUNTMENU
            if self.clickInvoices(browser) == InvoiceErrorReturn.ERROR_CLICK_INVOICE:
                self.clickLogOut(browser)
                return InvoiceErrorReturn.ERROR_CLICK_INVOICE

            while isFinalPage == False and moreInvoice == True:
                moreInvoice = self.clickDownloadInvoice(browser, dateLimit, account, outputfile)
                isFinalPage = self.clickNextInvoicePage(browser)
            self.clickLogOut(browser)
            return InvoiceErrorReturn.SUCCESSFUL
        except NoSuchElementException:
            return InvoiceErrorReturn.UNSUCCESSFUL
        except TimeoutException:
            return InvoiceErrorReturn.UNSUCCESSFUL


    def invoiceDownloader(self, dateLimit):
        invoiceSaveLink = os.getcwd() + "/invoices"
        accountFile = 'AccountList.csv'
        outputfile = 'InvoiceList.csv'
        first_page = 'https://www.zara.com/es/en/'

        profile = webdriver.FirefoxProfile()
        profile.set_preference('browser.download.dir',invoiceSaveLink)
        profile.set_preference('browser.download.folderList', 2)
        profile.set_preference("browser.helperApps.alwaysAsk.force", False);
        profile.set_preference("browser.download.manager.showWhenStarting", False);
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', "application/PDF")
        browser = webdriver.Firefox(profile)
        # somethine = input("Your age? ")
        browser.get(first_page)
        # create list of account from a file
        accList = AccountList()
        accList.accGetter(accountFile)
        input("Please check autoDownload pdf")
        for account in accList.getAccList():
            auxReturn = self.getInvoiceByAccount(browser, account, dateLimit, outputfile)
            if (auxReturn == InvoiceErrorReturn.ERROR_CLICK_LOGIN or auxReturn == InvoiceErrorReturn.ERROR_LOGIN):
                browser.get(first_page)
                self.getInvoiceByAccount(browser, account, dateLimit, outputfile)
            elif (auxReturn == InvoiceErrorReturn.ERROR_CLICK_ACCOUNTMENU or
                          auxReturn == InvoiceErrorReturn.ERROR_CLICK_INVOICE ):
                browser.get(first_page)
                self.getInvoiceByAccount(browser, account, dateLimit, outputfile)
                print("ERROR ACCESSING")


        browser.close()
def main(argv):
    acction = ZaraDownloader()
    dateLimit = "10/27/2017"
    acction.invoiceDownloader(dateLimit)

    return

if __name__ == '__main__': sys.exit(main(sys.argv))

