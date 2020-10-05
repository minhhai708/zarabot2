
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import WebDriverException
from Account import AccountList
from Tools import Tools
import os

WAIT_TIME = 2
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
    ERROR_TIMEOUT = -7

class ZaraDownloader(object):
    def clickAlertMessage(self, browser):
        alert = "button-primary.button-big._closeHandler"
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.CLASS_NAME, alert)))
            browser.find_element_by_class_name(alert).click()
            return InvoiceErrorReturn.SUCCESSFUL
        except NoSuchElementException:
            return InvoiceErrorReturn.UNSUCCESSFUL
        except TimeoutException:
            return InvoiceErrorReturn.UNSUCCESSFUL
        except ElementNotInteractableException:
            return InvoiceErrorReturn.UNSUCCESSFUL

    def logIn(self, browser, email, password):
        try:
            browser.get("https://www.zara.com/es/en/logon")
            WebDriverWait(browser, WAIT_TIME).until(EC.presence_of_all_elements_located((By.ID, 'form-input__label-email')))
            emailUser = browser.find_element_by_name('email')  # Find the search box
            passwordUser = browser.find_element_by_name('password')
            print("Log in :" +email)
            emailUser.send_keys(email)
            passwordUser.send_keys(password + Keys.RETURN)
            time.sleep(1)
            return InvoiceErrorReturn.SUCCESSFUL
        except NoSuchElementException:
            print("Unable to login "+ email)
            return InvoiceErrorReturn.ERROR_CLICK_LOGIN
        except TimeoutException:
            print("TimeoutException - LOGIN")
            return InvoiceErrorReturn.ERROR_CLICK_LOGIN
        except WebDriverException:
            print("WebDriverException- LOGIN")
            return InvoiceErrorReturn.ERROR_CLICK_LOGIN

    def clickLogOut(self, browser):
        browser.get("https://www.zara.com/es/es/session/logout")

    def clickInvoices(self, browser):
        browser.implicitly_wait(WAIT_TIME)
        browser.get("https://www.zara.com/es/en/user/invoice")
        return InvoiceErrorReturn.SUCCESSFUL

    def checkExistFinalPage(self, browser):
        isFinalPage = False
        try:
            finalPage = "fonticon.fonticon-right-color-arrow._table-nav-next._prevPage._disabled.font-icon-disabled"
            browser.find_element_by_class_name(finalPage)
            isFinalPage = True
        except TimeoutException:
            return isFinalPage
        except NoSuchElementException:
            isFinalPage = False
            return isFinalPage
        except WebDriverException:
            return isFinalPage

    def clickNextInvoicePage(self, browser):

        attempt = 0
        while attempt < 3:
            nextpage = "fonticon.fonticon-right-color-arrow._table-nav-next._prevPage"
            isFinalPage = False
            try:
                WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.CLASS_NAME, nextpage)))
                browser.find_element_by_class_name(nextpage).click()
                #self.clickAlertMessage(browser)
                return isFinalPage
            except TimeoutException:
                attempt = attempt + 1
                #print("TimeoutException- move_NextPage")
                browser.implicitly_wait(WAIT_TIME)
            except NoSuchElementException:
                print("NoSuchElementException- move_NextPage")
                return isFinalPage
            except WebDriverException:
                print("WebDriverException- move_NextPage")
                return isFinalPage

    def clickDownloadLinks(self, browser, dateLimit, account, outputfile):
        invoicesDownload = "button-secondary.button-medium._invoice-download"
        downloadText = "Download"
        contentTable = "content-single-line-table.invoice-list-table"

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

            for linkIndex in linkList:
                attempt = 1
                if len(linkList) < 5:
                    moreInvoice = False;
                while attempt < 3:
                    try:
                        WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, downloadText)))
                        WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.CLASS_NAME, invoicesDownload)))
                        print("Downloading " + tbodyEle.text.splitlines()[linkIndex*4] +
                                            " " + tbodyEle.text.splitlines()[linkIndex*4 + 1]+
                                            " " + tbodyEle.text.splitlines()[linkIndex*4 + 2])
                        links[linkIndex].click()
                        Tools.invoiceWriter(account, tbodyEle.text.splitlines()[linkIndex*4] +
                                            " " + tbodyEle.text.splitlines()[linkIndex*4 + 1]+
                                            " " + tbodyEle.text.splitlines()[linkIndex*4 + 2], outputfile)
                        break
                    except StaleElementReferenceException:
                        browser.implicitly_wait(WAIT_TIME)
                        attempt = attempt + 1
                    except WebDriverException:
                        browser.implicitly_wait(WAIT_TIME)
                        attempt = attempt + 1
            return moreInvoice
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException, IndexError):
            print("Exception-clickDownloadLinks")
            return

    def getInvoiceByAccount(self, browser, account, dateLimit, outputfile):
        try:
            isFinalPage = False
            moreInvoice = True


            self.logIn(browser, account.getEmail(), account.getPassword())

            if self.clickInvoices(browser) == InvoiceErrorReturn.ERROR_CLICK_INVOICE:
                self.clickLogOut(browser)
                return InvoiceErrorReturn.ERROR_CLICK_INVOICE

            while isFinalPage == False and moreInvoice == True:
                isFinalPage =self.checkExistFinalPage(browser)
                moreInvoice = self.clickDownloadLinks(browser, dateLimit, account, outputfile)
                self.clickNextInvoicePage(browser)

            self.clickLogOut(browser)
            return InvoiceErrorReturn.SUCCESSFUL

        except NoSuchElementException:
            print("NoSuchElementException - getInvoiceByAccount")
            return InvoiceErrorReturn.UNSUCCESSFUL
        except TimeoutException:
            print("TimeoutException - getInvoiceByAccount")
            return InvoiceErrorReturn.UNSUCCESSFUL



    def invoiceDownloader(self, dateLimit, client):
        #Configure browser
        invoiceSaveLink = os.getcwd() + "/"+client
        accountFile = 'ACCOUNT/'+ client + '.csv'
        outputfile = 'InvoiceList.csv'
        first_page = 'https://www.bershka.com/es/logon.html?showRegister=true&showCheckout=false'
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.dir",invoiceSaveLink)

        browser = webdriver.Firefox(profile)
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
            browser.get(first_page)
        browser.close()

def main(argv):
    acction = ZaraDownloader()
    dateLimit = input("nhap MM/DD/YYYY:")
    client = input("Client Name: ")
    acction.invoiceDownloader(dateLimit, client)
    return

if __name__ == '__main__': sys.exit(main(sys.argv))
