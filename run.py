from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
import argparse
import ast
import time

# Set up the command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--desktop", help="(boolean) Make the tests only run tests on desktop computers. BROWSERSTACK.",
                    action="store_true")
parser.add_argument("--mobile", help="(boolean) Make the tests only run tests on mobile devices. BROWSERSTACK",
                    action="store_true")
parser.add_argument("--use_local", help="(boolean) Use the Local Browserstack selenium testing. BROWSERSTACK",
                    action="store_true")
parser.add_argument("--base_url", help="A way to override the DEFAULT_BASE_URL for your tests.",)
parser.add_argument("--test", help="Only run one test as specified", default="all")
desired_cap_config_notes = "The available values you can pass to this command will depend on the values you have\
                           set in your config.py file. BROWSERSTACK."
parser.add_argument("--browser", help="Desktop: Only run tests on the given browser." +
                    desired_cap_config_notes, default=False)
parser.add_argument("--browser_version", help="Desktop: Only run tests on the given browser version." +
                    desired_cap_config_notes, default=False)
parser.add_argument("--os", help="Desktop: Only run tests on the given operating system." +
                    desired_cap_config_notes, default=False)
parser.add_argument("--os_version", help="Desktop: Only run tests on the given operating system version." +
                    desired_cap_config_notes, default=False)
parser.add_argument("--resolution", help="Desktop: Only run tests on the given screen resolution." +
                    desired_cap_config_notes, default=False)
parser.add_argument("--browserName", help="Mobile: Only run tests on the given the mobile browser name." +
                    desired_cap_config_notes, default=False)
parser.add_argument("--platform", help="Mobile: Only run tests on the given the mobile platform." +
                    desired_cap_config_notes, default=False)
parser.add_argument("--device", help="Mobile: Only run tests on the given the mobile device." +
                    desired_cap_config_notes, default=False)
parser.add_argument("--capabilities", help="Example: \"{'browser': 'IE', 'browser_version': '8.0', 'os': 'Windows', " +
                    "'os_version': '7', 'resolution': '1024x768'}\" Can be used as an alternative to adding many of" +
                    "the arguments above such as mobile, desktop, browser, browser_version, etc.")
parser.add_argument("--browserstack", help="This will make tests execute on the browserstack platform instead" +
                    "the above flags will be ignored", action="store_true")
parser.add_argument("--proxy", help="This will make the tests attempt to run through your browsermob proxy" +
                    ". Wil not work with Browserstack.", action="store_true")
parser.add_argument("--phantom", help="Will run tests via Phantom JS which will be a little faster. Will not work" +
                    " with Browserstack.", action="store_true")
args = parser.parse_args()

# IMPORT ALL VARIABLES
from config import *

if(args.base_url is not None):
    # Override the DEFAULT_BASE_URL value if passed in via the command line arg
    BASE_URL = args.base_url  # Don't touch this
else:
    BASE_URL = DEFAULT_BASE_URL

# Set up phantom js default arguments if it's being used
if(args.phantom):
    phantomjs_args = PHANTOMJS_DEFAULTS

# Set up the browsermob proxy if the argument is passed
if(args.proxy):
    from browsermobproxy import Server
    path_to_bmp = os.path.abspath(os.path.join(os.path.dirname(__file__), "browsermob-proxy-2.0.0/bin"))
    server = Server("%s/browsermob-proxy" % path_to_bmp)
    server.start()
    proxy = server.create_proxy()
    proxy_url = proxy.webdriver_proxy().http_proxy

    # Set up the blacklist
    for regex in PROXY_BLACKLIST:
        proxy.blacklist(regex, 200)

    # Set up the needed arguments for either firefox or phantomjs
    if (args.phantom):
        phantomjs_args.append("--proxy=%s" % (proxy_url))
    else:
        profile  = webdriver.FirefoxProfile()
        profile.set_proxy(proxy.selenium_proxy())


if(args.browserstack):
    # Grab the authentication variables from the environment
    try:
        selenium_username = os.environ['SELENIUM_AUTOMATE_USERNAME']
        selenium_value = os.environ['SELENIUM_AUTOMATE_VALUE']
    except KeyError:
        print "You need to set the environment variables for your username and value. See the README.md for details"
        exit()


if(BASE_URL == ""):
    print "You need to set your DEFAULT_BASE_URL in config.py."
    exit()

# If browserstack is set to be used then do set up the desired capabilities array, etc.
if(args.browserstack):
    if(args.capabilities is not None):
        # If the user passed --capabilities "{...}" then that will be the only platform tested on

        # convert the string into a python dictionary so it can be used in as a desired capability
        desired_cap_list = [ast.literal_eval(args.capabilities)]
    else:
        # If the user did not pass the --capabilities argumen then run all the tests listed below

        # This has been set as an array so that we can set multiple environments and run the tests below in a for loop
        # to repeat the tests for different operating systems. I have set a mobile capability list and
        # desktop capability list to allow the use of either or with a flag. More tests can easily be added. See the
        # browser stack website to get more options.
        # The below tests IE8, IE9, IE10 and IE11 on windows and then chrome, safari and Firefox on a Mac.
        # Pay attention to the version numbers.
        desktop_cap_list = DESKTOP_CAP_LIST_CONFIGS

        # The below tests an iPhone 5 and Samsung Galaxy S5. If your Selenium Automate plan doesn't include Mobile,
        # you will Want to change the following to mobile_cap_list = []
        mobile_cap_list = MOBILE_CAP_LIST_CONFIGS

        # Conditionally create the desired_cap_list list. Didn't use elseif statements to allow for more user error
        desired_cap_list = []
        if(args.desktop):
            # If the desktop argument has been passed, then only run the desktop tests
            desired_cap_list = desired_cap_list + desktop_cap_list
        if(args.mobile):
            # If the mobile argument has been passed, then only run the mobile tests
            desired_cap_list = desired_cap_list + mobile_cap_list
        if(desired_cap_list == []):
            # If no desktop or mobile argument has been passed, then run both the desktop and mobile tests
            desired_cap_list = desktop_cap_list + mobile_cap_list

    # If a specific filter arg was set via the command line, remove anything from the desired_capabilites list that
    # does not meet the requirement
    desired_cap_list_filters = [
        "os",
        "browser",
        "browser_version",
        "resolution",
        "os_version",
        "browserName",
        "platform",
        "device",
    ]
    # Loops through the abev list to do this to prevent duplicate code. You will notice that append was used below,
    # instead of remove. Remove was not acting as hoped so to cut corners, I just did this with addition instead of
    # subtraction
    # to the same affect.
    for the_filter in desired_cap_list_filters:
        if(getattr(args, the_filter) is not False):
            temp_list = desired_cap_list
            desired_cap_list = []
            for desired_cap in temp_list:
                if(the_filter in desired_cap and desired_cap[the_filter] == getattr(args, the_filter)):
                    desired_cap_list.append(desired_cap)
# If the --browserstack argument was not passed, just set one element in the desired_cap_list for the sake
# of using the same logic below. When looping through the elements of the desired_cap_list
else:
    if(args.phantom):
        desired_cap_list = [{"browser": "PhantomJs"}]
    else:
        desired_cap_list = [{"browser": "Firefox"}]

# This will run the the same test code in multiple environments
for desired_cap in desired_cap_list:

    # If the browserstack argument was passed, then use the folowing to output the test headers
    if(args.browserstack):
        # Use browser stack local testing if the argument was passed
        if(args.use_local): desired_cap['browserstack.local'] = True

        # Output a line to show what enivornment is now being tested
        if("browser" in desired_cap):
            # For desktop on browserstack
            print "\nStarting Tests on %s %s on %s %s with a screen resolution of %s " % (desired_cap["browser"],
                desired_cap["browser_version"], desired_cap["os"], desired_cap["os_version"], desired_cap["resolution"])
        else:
            # For mobile on browserstack
            print "\nStarting Tests on a %s" % (desired_cap["device"])
    # Otherwise, just simply output this message
    else:
        # For desktop on localmachine using firefox
        print "\nStarting Tests on %s on your local machine" % (desired_cap["browser"])

    print "--------------------------------------------------\n"

    # If the browserstack argument was passed, then dynamically set up the remote driver.
    if(args.browserstack):
        driver = webdriver.Remote(
            command_executor="http://%s:%s@hub.browserstack.com:80/wd/hub" % (selenium_username, selenium_value),
            desired_capabilities=desired_cap)
    # Otherwise, just run firefox locally.
    else:
        if(args.proxy and args.phantom):
            driver = webdriver.PhantomJS(service_args=phantomjs_args)
        elif(args.proxy):
            # Defaults to firefox
            driver = webdriver.Firefox(firefox_profile=profile)
        elif(args.phantom):
            driver = webdriver.PhantomJS(service_args=phantomjs_args)
            # With Phantom js, we need te set a specific window size to prevent certain tests from failing
            driver.set_window_size(1124, 850)
        else:
            driver = webdriver.Firefox(executable_path="driver/geckodriver")

    tests_to_run = []
    if(args.test == "all"):
        # if args.test == "all" then dynamically set up that list from all the file names in the test folder
        for file in [doc for doc in os.listdir("tests") if doc.endswith(".py") and doc != "__init__.py"
                     and doc != "base_test.py"]:
            tests_to_run.append("tests." + file.split(".")[0])  # remove the .py from the test name
    else:
        # Otherwise, just add the one tests specified when passing the command
        tests_to_run = ["tests." + args.test.split(".")[0]]  # remove the .py from the test name

    # The time when the test started
    all_tests_start_time = time.time()

    # Loop through all the tests_to_run and runs them
    for test_to_run in tests_to_run:
        # The time when the test started
        this_test_start_time = time.time()
        # This dynamically imports all modules in the tests_to_run list. This allows me to import a module using
        # a variable. This is fairly advanced and hard to follow for the beginner.
        current_test = getattr(__import__(test_to_run, fromlist=["Test"]), "Test")
        test = current_test(driver, BASE_URL, test_to_run)
        test.run()

        # If it makes it this far, this means the test passed
        test.passed()

        # Output the amount of time it took this test to run on the current platform
        this_test_seconds_taken = time.time() - this_test_start_time
        if(this_test_seconds_taken > 60):
            print "Time taken: " + str(this_test_seconds_taken / 60) + " minutes"
        else:
            print "Time taken: " + str(this_test_seconds_taken) + " seconds"

    # Output the amount of time it took all tests to run on the current platform
    print "--------------------------------------------------\n"
    all_tests_seconds_taken = (time.time() - all_tests_start_time)
    if(all_tests_seconds_taken > 60):
        print "Time taken for all tests: " + str(all_tests_seconds_taken / 60) + " minutes"
    else:
        print "Time taken for all tests: " + str(all_tests_seconds_taken) + " seconds"

    # Clean Up
    driver.quit()

if(args.proxy): server.stop()
