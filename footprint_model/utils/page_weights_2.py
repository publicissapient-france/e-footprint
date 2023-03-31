from selenium import webdriver
import time

# specify the path to the Chrome driver executable
driver_path = "/path/to/chromedriver"

# create a new Chrome browser instance
browser = webdriver.Chrome(executable_path=driver_path)

# specify the URL of the web page to load
url = "https://www.example.com"

# navigate to the URL
browser.get(url)

# wait for the page to load completely
time.sleep(5)

# get the size of the web page in bytes
size_in_bytes = len(browser.page_source.encode('utf-8'))

# convert the size to megabytes
size_in_megabytes = size_in_bytes / (1024 * 1024)

# print the size in megabytes
print(f"Size of {url}: {size_in_megabytes:.2f} MB")

# close the browser
browser.quit()
