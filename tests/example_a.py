from tests.base_test import BaseTest
import time
from datetime import datetime

class Test(BaseTest):
    def __init__(self, driver, base_url, module):
        super(Test, self).__init__(driver, base_url, module)

    def run(self):

        # Set how many times script should be ran
        numberOfRetries = 1

        # Set target Page URL
        pageUrl = "https://miausinna.github.io/Test%20Player_Player%20Revenue%20verification.html"

        # Set how long in seconds video should be watched
        videoTime = 10



        while numberOfRetries <= numberOfRetries:
            try:
                print("RUN #" + str(numberOfRetries) + " STARTED AT " + str(datetime.now().time()))
                # RUN FIREFOX AND OPEN TARGET PAGE
                self.driver.get(pageUrl)
                time.sleep(1)

                # SWITCH TO PLAYER IFRAME
                iframe = self.driver.find_elements_by_tag_name('iframe')[0]
                self.driver.switch_to_default_content()
                self.driver.switch_to_frame(iframe)
                print("SWITCHED TO PLAYER FRAME")

                # CLICK ON PLAYER TO START VIDEO
                time.sleep(1)
                player = self.driver.find_element_by_id('AolHtml5Player')
                player.click()
                print("VIDEO STARTED")

                time.sleep(videoTime)
            finally:
                print("RUN #" + str(numberOfRetries) + " FINISHED AT " + str(datetime.now().time()))
                numberOfRetries += 1
                time.sleep(3)

        self.driver.quit()
