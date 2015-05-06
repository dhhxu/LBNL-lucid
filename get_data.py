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

Dependencies: util.py
"""

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import sleep

import util

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
    util.alert("done")
    return (browser, display)

def login(browser):
    """
    Logs into the Lucid website. On failure, exits the script.
    """

    print("Loading page... "),
    browser.get(util.URL)
    util.alert("done")
    username = browser.find_element_by_id("id_username")
    password = browser.find_element_by_id("id_password")
    username.send_keys(util.USER)
    password.send_keys(util.PASS)
    browser.find_element_by_name("submit").click()
    if not "home" in browser.title.lower():
        util.err("log in failed.")
    else:
        util.alert("Logged in as %s" % util.USER)

def get_data_page(browser):
    """
    Navigate to the data export page. If failure, exits the script.
    """

    browser.get("https://buildingos.com/exports/create")
    if not "export" in browser.title.lower():
        util.err("export page not available")
    else:
        util.alert("export page found")

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
    all_meters = []
    for meter in raw_meter_list:
        name = meter.get_attribute("title")
        all_meters.append(name)

    meter_list = []
    meter_indices = sorted(util.get_meters(all_meters))
    for index in meter_indices:
        meter_list.append(all_meters[index - 1])

    util.alert("Selecting meters...")
    for meter in meter_list:
        util.alert("Selecting meter: %s" % (meter))
        elem = browser.find_element_by_xpath("//*[@title=\"%s\"]/span" % (meter))
        elem.click()
    util.alert("Selection done.")

    add_button_xpath = "//*[@id=\"addPoints\"]/form/fieldset/div[3]/button"
    browser.find_element_by_xpath(add_button_xpath).click()
    count = browser.find_element_by_id("numPoints")
    util.alert("number of points selected: %s" % (count.text))

    start_date, end_date = util.get_dates()
    filename = raw_input("Enter a base file name (spaces will be replaced with"
                         " an underscore): ")
    filename = util.clean_up_file_name(filename)

    start = browser.find_element_by_id("id_start").clear()
    end = browser.find_element_by_id("id_end").clear()
    start_script = "document.getElementById('id_start').value = '%s';" % (start_date)
    end_script = "document.getElementById('id_end').value = '%s';" % (end_date)
    browser.execute_script(start_script)
    browser.execute_script(end_script)

    export_string = "%s_%s_%s" % (filename, util.convert_date(start_date), \
                                  util.convert_date(end_date))
    export_name_box = browser.find_element_by_id("id_name")
    export_name_box.send_keys(export_string)

    browser.find_element_by_xpath("//select[@id='id_resolution']/option[@value='1']").click()

    submit_div = browser.find_element_by_class_name("form-actions")
    submit_div.find_element_by_tag_name("button").click()

    return export_string

def download(browser, export_string):
    """
    Downloads the data from the link whose name is EXPORT_STRING. On error,
    exits.
    """

    util.alert("Waiting for download to be ready.")
    waitCount = 0
    link = None
    while waitCount < util.MAX_RETRIES:
        sleep(util.DATA_WAIT_PERIOD)
        browser.refresh()
        waitCount += 1
        try:
            link = browser.find_element_by_link_text(export_string)
            util.alert("Link found.")
            break
        except NoSuchElementException:
            continue
    if link:
        try:
            url = link.get_attribute("href")
            browser.get(url)
            util.alert("Downloading file %s" % link.text)
        except NoSuchElementException:
            util.err("Link not found")
    else:
        util.err("Link not found")

def main():
    """
    Main function.
    """

    browser, display = setup()
    login(browser)
    get_data_page(browser)
    export_string = interact(browser)
    download(browser, export_string)

    util.alert("Exiting...")
    browser.quit()
    display.stop()

if __name__ == "__main__":
    main()
