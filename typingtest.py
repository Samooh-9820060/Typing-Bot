import time
import base64
from PIL import Image
from io import BytesIO
import pytesseract
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import re

# Set the path to the browser driver
driver_path = "D:\Software\chromedriver.exe"

# Set the URL to open
url = "https://typingtest.com/"

# Set WPM target
wpm_target = 1000
typist_speed = 2.0 / (wpm_target)

# Set the path to the Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize WebDriver
driver = webdriver.Chrome(executable_path=driver_path)

# Open the website
driver.get(url)

# Wait until the "Start Test" button is clickable and click it
#start_button = WebDriverWait(driver, 10).until(
#    EC.element_to_be_clickable((By.XPATH, '//*[@id="testStartForm"]/button'))
#)
#start_button.click()

# Wait for the text to appear in the canvas
WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.TAG_NAME, 'canvas'))
)

# Define a global variable for the screenshot counter
screenshot_counter = 0
time.sleep(10)


def get_canvas_text(filename=None):
    global screenshot_counter

    # Capture a screenshot of the div element and convert it to an image
    div = driver.find_element(By.ID, 'test-container')
    div_base64 = div.screenshot_as_base64
    div_image = Image.open(BytesIO(base64.b64decode(div_base64)))

    # Crop the image from the top if this is not the first screenshot
    if screenshot_counter > 0:
        cropped_image = div_image.crop((0, 128, div_image.size[0], div_image.size[1]))
        #div_image = cropped_image

    cropped_image = div_image.crop((0  , 0, div_image.size[0], div_image.size[1]-125))
    div_image = cropped_image

    # Save the image to a file if a filename is provided
    if filename:
        div_image.save(filename)

    # Extract text from the image using OCR
    custom_config = r'--psm 6'
    text = pytesseract.image_to_string(div_image, config=custom_config)

   # Remove unwanted words and any text that appears before them
    unwanted_words = ["MODE Pro", "CLOSE", "@"]
    for word in unwanted_words:
        word_index = text.find(word)
        if word_index != -1:
            text = text[word_index+len(word):].lstrip()

    # Increment the screenshot counter
    screenshot_counter += 1

    return text

# Type the words at the target WPM speed
input_field = driver.find_element(By.CSS_SELECTOR, 'input[type="text"]')

# Define a global variable for the screenshot counter
screenshot_counter = 0

while True:

    # Get the current canvas text
    current_text = get_canvas_text("canvas_image.png")

    # Split the text into words and remove any empty strings
    words = [word for word in current_text.replace('\n', ' ').split(' ') if word]


    # Type the words at the target WPM speed
    for word in words:
        for char in word:
            # Simulate keyboard input on the browser window
            actions = ActionChains(driver)
            actions.send_keys(char)
            actions.perform()
            time.sleep(typist_speed)
        actions = ActionChains(driver)
        actions.send_keys(Keys.SPACE)
        actions.perform()

    # Wait for the next line to appear
    time.sleep(0.5)

    # Check if the test has ended
    try:
        WebDriverWait(driver, 1).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.test-ended'))
        )
        break
    except Exception:
        pass

# Sleep for a few seconds to observe the result before closing the browser
time.sleep(5)