#!/usr/bin/env python

"""
This is the getter script to extract building energy data from Lucid's website.
The script uses Selenium to automate the manual process of selecting desired
meters, date range, file export base name, and resolution. The user will
be prompted to select meters by entering numbers corresponding to them, provide
start and end dates, and the file name for the exported zip file.

Note: when the Lucid system receives a request from the user, it gathers the
data for the requested meters and prepares a URL link to download the data. It
takes time for the link to appear. So requesting many meters at once can cause
performance issues, as this script will not wait forever for the download to
be ready.
"""

from datetime import datetime
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import sleep

import util

def valid_date(date):
    """
    Checks if DATE is of form MM/DD/YYYY. Does not check if YYYY is correct.
    Also, does not check for edge cases, i.e. Feb 30.
    """
    mdy = date.split("/")
    if (len(mdy) == 3):
        try:
            m = int(mdy[0])
            d = int(mdy[1])
            y = int(mdy[2])
            datetime(y, m, d)
            return True
        except TypeError, ValueError:
            return False
    return False

def get_datetime(date):
    """
    Return the datetime object representing DATE. DATE must be valid.
    """

    mdy = date.split("/")
    m = int(mdy[0])
    d = int(mdy[1])
    y = int(mdy[2])
    return datetime(y, m, d)

def convert_date(date):
    """
    Convert date of form MM/DD/YYYY into YYYY-MM-DD. Assumes date is correct
    form.
    """
    
    mdy = date.split("/")
    m = mdy[0]
    d = mdy[1]
    y = mdy[2]
    newDate = "%s-%s-%s" % (y, m, d)
    return newDate

def get_dates():
    """
    Prompt the user for a start and end date.
    This function will keep prompting until valid dates are entered.
    Returns a tuple of start date and end date strings.
    """

    hasValidStart = False
    hasValidEnd = False
    start = None
    end = None
    while True:
        if not hasValidStart:
            start = raw_input("Enter start date (MM/DD/YYYY): ") 
            if not valid_date(start):
                print("Invalid start date %s" % (start))
                continue
            else:
                hasValidStart = True
        if not hasValidEnd:
            end = raw_input("Enter end date (MM/DD/YYYY): ")
            if not valid_date(end):
                print("Invalid end date %s" % (end))
                continue
            else:
                hasValidEnd = True
        if hasValidStart and hasValidEnd:
            if get_datetime(start) < get_datetime(end):
                decision = raw_input("Is date range %s - %s acceptable? (Y/N)")
                if decision.lower() == "y":
                    break
                else:
                    hasValidStart = False
                    hasValidEnd = False
            else:
                print("End date comes before start. Please enter a valid date.")
                hasValidEnd = False
    return (start, end)

def valid_index(index, left, right):
    """
    Checks if INDEX is a valid number and is within the index range. If valid,
    returns TRUE. Otherwise, returns FALSE.
    """

    try:
        num = int(index)
        return (num >= left and num <= right)
    except ValueError, TypeError:
        return False

def display_meters(all_meters):
    """
    Print meter names and their indices. Meters come from ALL_METERS list.
    Note that indices begin at 1.
    """

    for index, meter in enumerate(all_meters, 1):
        if index < 10:
            print("  %d:  %s" % (index, meter))
        else:
            print("  %d: %s" % (index, meter))
    print "\n"

def get_meters(meters):
    """
    Prompt user to enter indicies of the meters desired. At least one index must
    be entered. Returns the selected indices.
    """

    user_list = []
    atLeastOneMeter = False
    minIndex = 1
    maxIndex = len(meters)
    display_meters(meters)
    print("Please select the indices of the meters desired. Enter 'all' if all"
          "meters are desired (not recommended, as performance will decrease)."
          " Enter 'done' to end selection.")
    while True:
        index = raw_input("Enter a meter index: ") 
        if index == "all":
            return meters
        if not atLeastOneMeter:
            if index == "done":
                print("No meters selected. Please try again.")
                continue
            if not valid_index(index, minIndex, maxIndex):
                print("Invalid meter index.")
                continue
            num = int(index)
            if not num in user_list:
                user_list.append(num)
                atLeastOneMeter = True
            else:
                print("Meter already selected. Please pick a different one")
        else:
            if index == "done":
                return user_list
            if not valid_index(index, minIndex, maxIndex):
                print("Invalid meter index.")
                continue
            num = int(index)
            if not num in user_list:
                user_list.append(num)
            else:
                print("Meter already selected. Please pick a different one")

def clean_up_file_name(filename):
    """
    If FILENAME has spaces in it, replaces them with underscores. Otherwise,
    this function returns the filename unchanged.
    """

    words = filename.split()
    if len(words) > 1:
        filename = "_".join(words)
    return filename

def err(msg, browser, display, code=1):
    """
    Print error message, closes the BROWSER and DISPLAY, and quits script
    with exit code CODE.
    """

    print("ERROR: %s\n" % msg)
    browser.quit()
    display.stop()
    exit(code)

def setup():
    """
    Sets up the display and browser for running Selenium with headless
    Firefox. Returns a tuple of (browser, display) objects.
    """

    print("\nSetting up browser, this may take a while..."),
    display = Display(visible=0, size=(800, 600))
    display.start()
    p = webdriver.FirefoxProfile()
    p.set_preference("browser.download.folderList", 2)
    p.set_preference("browser.download.manager.showWhenStarting", False)
    p.set_preference("browser.download.dir", util.DATA_PATH)
    p.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip")
    browser = webdriver.Firefox(firefox_profile=p)
    print("done")
    return (browser, display)

def login(browser, display):
    """
    Logs into the Lucid website. On failure, exits the script.
    """

    print("Loading page... "),
    browser.get(util.URL)
    print("done")
    username = browser.find_element_by_id("id_username")
    password = browser.find_element_by_id("id_password")
    username.send_keys(util.USER)
    password.send_keys(util.PASS)
    browser.find_element_by_name("submit").click()
    if not "home" in browser.title.lower():
        err("log in failed.", browser, display)
    else:
        print("Logged in as %s" % util.USER)

def get_data_page(browser, display):
    """
    Navigate to the data export page. If failure, exits the script.
    """

    browser.get("https://buildingos.com/exports/create")
    if not "export" in browser.title.lower():
        err("Export page not available.", browser, display)
    else:
        print("Export page found.")

def interact(browser):
    """
    Get list of meters available in the Lucid system, get user response, and
    forward response to Lucid system for meter download. Returns the string
    that's the name of the link to click on for download.
    """

    meter_xpath = "//*[@id=\"pointForm\"]/fieldset/div[2]/div/a"
    meter_select = browser.find_element_by_xpath(meter_xpath)
    meter_select.click()
    # Let page load.
    sleep(3)
    raw_meter_list = browser.find_elements_by_class_name("ms-elem-selectable")
    all_meters = [ meter.get_attribute("title") for meter in raw_meter_list ]

    meter_indices = sorted(get_meters(all_meters))
    meter_list = [ all_meters[index - 1] for index in meter_indices ]

    print("Selecting meters...")
    for meter in meter_list:
        print("Selecting meter: %s" % (meter))
        elem = browser.find_element_by_xpath("//*[@title=\"%s\"]/span" % (meter))
        elem.click()
    print("Selection done.")

    add_button_xpath = "//*[@id=\"addPoints\"]/form/fieldset/div[3]/button"
    browser.find_element_by_xpath(add_button_xpath).click()
    count = browser.find_element_by_id("numPoints")
    print("Number of points selected: %s" % (count.text))

    start_date, end_date = get_dates()
    filename = raw_input("Enter a base file name (spaces will be replaced with"
                         " an underscore): ")
    filename = clean_up_file_name(filename)

    start = browser.find_element_by_id("id_start").clear()
    end = browser.find_element_by_id("id_end").clear()
    start_script = "document.getElementById('id_start').value = '%s';" % (start_date)
    end_script = "document.getElementById('id_end').value = '%s';" % (end_date)
    browser.execute_script(start_script)
    browser.execute_script(end_script)

    export_string = "%s_%s_%s" % (filename, convert_date(start_date),
                                  convert_date(end_date))
    export_name_box = browser.find_element_by_id("id_name")
    export_name_box.send_keys(export_string)

    browser.find_element_by_xpath("//select[@id='id_resolution']/option[@value='1']").click()

    submit_div = browser.find_element_by_class_name("form-actions")
    submit_div.find_element_by_tag_name("button").click()

    return export_string

def download(export_string, browser, display):
    """
    Downloads the data from the link whose name is EXPORT_STRING. On error,
    quits the script.
    """

    print("Waiting for download to be ready.")
    waitCount = 0
    link = None
    while waitCount < util.MAX_RETRIES:
        sleep(util.DATA_WAIT_PERIOD)
        browser.refresh()
        waitCount += 1
        try:
            link = browser.find_element_by_link_text(export_string)
            print("Link found.")
            break
        except NoSuchElementException:
            continue
    if link:
        try:
            url = link.get_attribute("href")
            browser.get(url)
            print("Downloading file %s" % link.text)
        except NoSuchElementException:
            err("Link not found", browser, display)
    else:
        err("Link not found", browser, display)

def main():
    """
    Main function.
    """

    browser, display = setup()
    login(browser, display)
    get_data_page(browser, display)
    export_string = interact(browser)
    download(export_string, browser, display)

    print("Exiting...")
    browser.quit()
    display.stop()

if __name__ == "__main__":
    main()
