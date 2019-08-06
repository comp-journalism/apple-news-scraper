'''
get_stories.py

The main script used to collect data from Apple News.
Can be modified to perform extended or selective data collection.

Appium's scroll method has been out of commission,
so this script uses long_press and move_to as workarounds
'''
__author__ = "Jack Bandy"



# user-defined variables
device_name_and_os = 'iPhone XS Max (12.1)'
device_os = '12.1'
udid = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'

output_folder = 'data_output/'


# imports
import pdb
import os
from time import sleep
from shutil import rmtree
from appium import webdriver
from selenium.webdriver.common.keys import Keys
from appium.webdriver.common.touch_action import TouchAction
import datetime
import time
import os
from glob import glob


# constants
APP_PATH = ('/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/Library/CoreSimulator/Profiles/Runtimes/iOS.simruntime/Contents/Resources/RuntimeRoot/Applications/News.app')
# how many secs to wait between pressing "share" and "copy."
# (A hack to get around slower simulators)
SLEEP_T = 5



def main():
    # Locate and erase the cache folder before opening the app
    user = os.environ['USER']
    news_cache_search_path = '/Users/{}/Library/Developer/CoreSimulator/Devices/{}/data/Containers/Data/Application/*/Library/Caches/News'.format(user,udid)
    try:
        news_cache_path = glob(news_cache_search_path)[0]
        wipe_app_data_folder(news_cache_path)
    except:
        print("Couldn't find cache folder")


    # create folder for data output
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print("Opening app...")
    try:
        driver = webdriver.Remote(
                command_executor='http://localhost:4723/wd/hub',
                desired_capabilities={
                  'app':APP_PATH,
                  'deviceName': device_name_and_os,
                  'udid': udid,
                  'automationName': "XCUITest",
                  'platformName': "iOS",
                  'platformVersion':device_os,
                  'noReset': True,
                  'locationServicesEnabled': True,
                  'gpsEnabled': True
                  }
            )
    except:
        print("Error! You probably need to start appium!")
        exit()

    time_st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    date_st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d')

    # give the app a few seconds to load, or for you to click the "Continue"
    # button when opening the app for the first time
    sleep(6)

    try:    
        # grab and save the top stories
        top_stories = get_top_stories(driver)
        top_links = links_from_strings(top_stories)
        top_line = '{},'.format(time_st) + ','.join(top_links) + '\n'
        print("Top: {}".format(top_line))
        top_file_path = '{}/top-{}.csv'.format(output_folder, date_st) 
        with open(top_file_path, 'a') as out:
            out.write(top_line)
        
        # grab and save the trending stories
        print("Scrolling to trending stories...")
        trending_stories = get_trending_stories(driver)
        trending_links = links_from_strings(trending_stories)
        trending_line = '{},'.format(time_st) + ','.join(trending_links) + '\n'
        print('Trending: {}'.format(trending_line))
        trending_file_path = '{}/trending-{}.csv'.format(output_folder, date_st) 
        with open(trending_file_path, 'a') as out:
            out.write(trending_line)
    except:
        # something went wrong
        # catch the error so the script still closes the app
        print("Problem at time {}".format(time_st))

    driver.close_app()
    driver.quit()
        


# find, share/copy, and return the top stories
def get_top_stories(driver):
    actions = TouchAction(driver)
    top_stories = []
    window_height = driver.get_window_size()['height']
    top_acc_id = 'TOP STORIES'
    more_top_acc_id = 'MORE TOP STORIES'

    # scroll to top stories section 
    top_el = bring_element_on_screen(driver, top_acc_id)
    
    # scroll until it's at the top of the screen
    bring_element_to_top(driver, top_el)
    bottom_of_label = top_el.location['y'] + top_el.size['height']

    # find and tap share buttons for whatever is on screen
    buttons = driver.find_elements_by_ios_predicate('type == "XCUIElementTypeButton"')
    print("{} buttons found, looking for on-screen share buttons".format(len(buttons)))
    share_buttons = []
    for b in buttons:
        if b.location['y'] in range(max(bottom_of_label,40),
                window_height-200) and\
                        b.size['width'] in range(9,13) and\
                        b.size['height'] in range(13,18):
            share_buttons.append(b)
    print("{} share buttons found on screen".format(len(share_buttons)))

    for b in share_buttons:
        x_c, y_c = get_button_center(b)
        print("Pressing share button at {}, {}".format(x_c, y_c))
        actions.press(x=x_c, y=y_c).release().perform()
        sleep(SLEEP_T)
        find_and_press_copy_button(driver)
        link = driver.get_clipboard_text()    
        top_stories.append(link)
        sleep(SLEEP_T)

    # scroll to 'more top stories' element and repeat to collect the other stories
    more_top_el = bring_element_on_screen(driver, more_top_acc_id)
    while more_top_el.location['y'] > window_height - 200:
        actions.long_press(x=100,y=600,duration=1000).move_to(x=100,y=550).release().perform()
        
    # find and tap share buttons
    buttons = driver.find_elements_by_ios_predicate('type == "XCUIElementTypeButton"')
    print("{} buttons found, looking for on-screen share buttons".format(len(buttons)))
    share_buttons = []
    for b in buttons:
        if b.location['y'] in range(40, more_top_el.location['y']) and\
                        b.size['width'] in range(9,13) and\
                        b.size['height'] in range(13,18):
            share_buttons.append(b)
    print("{} share buttons found on screen".format(len(share_buttons)))

    for b in share_buttons:
        x_c, y_c = get_button_center(b)
        print("Pressing share button at {}, {}".format(x_c, y_c))
        actions.press(x=x_c, y=y_c).release().perform()
        sleep(SLEEP_T)
        find_and_press_copy_button(driver)
        link = driver.get_clipboard_text()    
        if link not in top_stories :
            top_stories.append(link)
        sleep(SLEEP_T)

    return top_stories
    
    
# find, share/copy, and return the trending stories
# similar to top stories but UI difference requires separate function
def get_trending_stories(driver):
    trending_acc_id = 'TRENDING STORIES'
    trending_el = bring_element_on_screen(driver, trending_acc_id)
    bring_element_to_top(driver, trending_el)
    min_y = trending_el.location['y'] + trending_el.size['height']

    actions = TouchAction(driver)
    trending_stories = []
    window_height = driver.get_window_size()['height']
    # find and tap share buttons
    buttons = driver.find_elements_by_ios_predicate('type == "XCUIElementTypeButton"')
    print("{} buttons found, looking for on-screen share buttons".format(len(buttons)))
    share_buttons = []
    for b in buttons:
        if b.location['y'] in range(max(40,min_y), window_height - 100) and\
                        b.size['width'] in range(9,13) and\
                        b.size['height'] in range(13,18):
            share_buttons.append(b)
    print("{} share buttons found on screen".format(len(share_buttons)))

    for b in share_buttons:
        x_c, y_c = get_button_center(b)
        print("Pressing share button at {}, {}".format(x_c, y_c))
        actions.press(x=x_c, y=y_c).release().perform()
        sleep(SLEEP_T)
        find_and_press_copy_button(driver)
        story = driver.get_clipboard_text()    
        trending_stories.append(story)
        sleep(SLEEP_T)
        last_touched_el = b
        
    # repeat for other trending stories
    bring_element_to_top(driver, last_touched_el)
    
    # find and tap share buttons
    buttons = driver.find_elements_by_ios_predicate('type == "XCUIElementTypeButton"')
    print("{} buttons found, looking for on-screen share buttons".format(len(buttons)))
    share_buttons = []
    for b in buttons:
        if b.location['y'] in range(last_touched_el.location['y'], window_height - 100) and\
                        b.size['width'] in range(9,13) and\
                        b.size['height'] in range(13,18):
            share_buttons.append(b)
    print("{} share buttons found on screen".format(len(share_buttons)))

    for b in share_buttons:
        x_c, y_c = get_button_center(b)
        print("Pressing share button at {}, {}".format(x_c, y_c))
        actions.press(x=x_c, y=y_c).release().perform()
        sleep(SLEEP_T)
        find_and_press_copy_button(driver)
        link = driver.get_clipboard_text()    
        if link not in trending_stories and len(trending_stories) < 6:
            trending_stories.append(link)
        sleep(SLEEP_T)

    return trending_stories




# scrolling and button-pressing functions 

def refresh_app(driver):
    # refresh the app
    actions = TouchAction(driver)
    actions.long_press(x=10,y=10,duration=100).release().perform()
    sleep(1)
    actions.long_press(x=10,y=10,duration=100).release().perform()
    sleep(1)
    actions.long_press(x=100,y=200,duration=1000).move_to(x=100,y=600).release().perform()


def bring_element_on_screen(driver, acc_id):
    actions = TouchAction(driver)
    el = None
    while el == None:
        try:
            el = driver.find_element_by_accessibility_id(acc_id)
        except Exception:
            print("Scrolling in search of element {}...".format(acc_id))
            # trending not on screen, scroll down
            actions.long_press(x=100,y=600,duration=1000).move_to(x=100,y=300).release().perform()
    return el


def bring_element_to_top(driver, element):
    actions = TouchAction(driver)
    while element.location['y'] > 150:
        actions.long_press(x=100,y=600,duration=1000).move_to(x=100,y=500).release().perform()


def bring_element_to_mid(driver, element):
    actions = TouchAction(driver)
    while element.location['y'] not in range(300,600) :
        actions.long_press(x=100,y=600,duration=1000).move_to(x=100,y=500).release().perform()



def find_and_press_copy_button(driver):
    print("Finding and pressing copy button...")
    copy_acc_id = 'Copy'
    act_acc_id = 'ActivityListView'
    copy_button = driver.find_element_by_accessibility_id(copy_acc_id)
    act_list = driver.find_element_by_accessibility_id(act_acc_id)
    copy_x_c = act_list.location['x'] + int(act_list.size['width'] / 8)
    copy_y_c = act_list.location['y'] + int(3 * act_list.size['height'] / 4)
    print("Pressing copy button at {}, {}".format(copy_x_c, copy_y_c))
    actions = TouchAction(driver)
    actions.press(x=copy_x_c, y=copy_y_c).release().perform()





# miscellaneous utility functions

def wipe_app_data_folder(path):
    for f in os.listdir(path):
        if os.path.isfile('{}/{}'.format(path,f)):
            print("Removing file {}".format(f))
            os.remove('{}/{}'.format(path,f))
        else:
            print("Removing folder {}".format(f))
            rmtree('{}/{}'.format(path,f))


def links_from_strings(string_list):
    links_only = []
    for s in string_list:
        link_ind = s.find('https://apple.news')
        links_only.append(s[link_ind:])
    return links_only


def get_button_center(a_button):
    x_c = a_button.location['x'] + int(a_button.size['width'] / 2)
    y_c = a_button.location['y'] + int(a_button.size['height'] / 2)
    return x_c, y_c





if __name__ == '__main__':
    main()

