# Apple News Scraper

![](Demo.gif)

This repository provides code and data used in the following paper:

Bandy, Jack and Nicholas Diakopoulos. "**Auditing News Curation Systems: A Case Study Examining Algorithmic and Editorial Logic in Apple News.**" *To Appear in* Proceedings of the Fourteenth International AAAI Conference on Web and Social Media (ICWSM 2020).


## Installation and Setup Instructions

#### Install Appium
Download appium-desktop: https://github.com/appium/appium-desktop/releases/latest
(You can try the brew/npm installation - https://appium.io - but those releases have been buggier in my experience)

And the python client: `pip install Appium-Python-Client`

Also, carthage (another dependency) often does not install automatically. Run `brew install carthage` to be sure.


#### Install apple-news-scraper
After cloning this repository onto your computer,
1. Run `instruments -s devices` in your terminal
2. Choose a device, something like `iPhone XS Max (12.1) [XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX] (Simulator)`
3. Open `get_stories.py` and replace the first few lines with your device information. Afterwards, it may look something like:
```python
# user-defined variables
device_name_and_os = 'iPhone XS Max (12.1)'
device_os = '12.1'
udid = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
```
4. Change the output folder, where you want to save the data:
```python
# easy relative path, keep data in repository
output_folder = 'data_output/'
```
or,
```python
# put data in a folder on the desktop
output_folder = '~/apple_news_data/'
```


## Execution
First, run the simulator of choice and open the Apple News app: `instruments -w "iPhone XS Max (12.1)"`

Execution should be as easy as `python get_stories.py`

To run repeatedly, I recommend cron. Just make sure you use absolute paths. For example, to run collection every five minutes, add something like this to your crontab:
```
*/5 * * * * /usr/local/bin/python /Users/jack/dev/apple-news-scraper/get_stories.py
```

If you're in a hurry, you can also just hack out a shell script:
```
while true
do
        python get_stories.py &
        sleep 300
done
```
