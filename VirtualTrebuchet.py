from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import itertools
import pandas as pd
import os
import copy


class VirtualTrebuchet():
    """ Enables interaction with online Virtual Trebuchet simulator, alowing for tests to be completed with the data
    being recorded to CSVs """

    # Hardcoded site variables that may change and break the script
    MAX_WAIT_TIME = 15  # seconds
    VIRTUAL_TREBUCHET_URL = "http://www.virtualtrebuchet.com"
    SUBMIT_BUTTON_XPATH = '//*[@id="Inputs"]/table/tbody/tr[22]/td/button'
    METRIC_SELECTION_XPATH = '//*[@id="topLeft"]/div[1]/select/option[1]'
    CUSTOM_PROJECTILE_XPATH = '//*[@id="Inputs"]/table/tbody/tr[15]/td[2]/select/option[1]'

    def __init__(self, initial_values: dict) -> None:
        """ Initialises the VirtualTrebuchet object, initializing and saving the Selenium driver"""

        # Launch Chrome and go to the virtual trebuchet site
        self.driver = webdriver.Chrome()
        self.driver.get(self.VIRTUAL_TREBUCHET_URL)

        # Change units to metric
        self.driver.find_element_by_xpath(self.METRIC_SELECTION_XPATH).click()

        # Set custom projectile (to specify projectile mass and diameter)
        self.driver.find_element_by_xpath(self.CUSTOM_PROJECTILE_XPATH).click()

        # Hardcode input fields where data is inputted using html id
        self.input_fields = {
            "length_short_arm": self.driver.find_element_by_id("txt_LengthArmShort"),
            "length_long_arm": self.driver.find_element_by_id("txt_LengthArmLong"),
            "length_sling": self.driver.find_element_by_id("txt_LengthSling"),
            "length_weight": self.driver.find_element_by_id("txt_LengthWeight"),
            "height_pivot": self.driver.find_element_by_id("txt_HeightOfPivot"),
            # ------------------------------------------------------------------------
            "arm_mass": self.driver.find_element_by_id("txt_MassArm"),
            # ------------------------------------------------------------------------
            "weight_mass": self.driver.find_element_by_id("txt_MassWeight"),
            "weight_inertia": self.driver.find_element_by_id("txt_InertiaWeight"),
            # ------------------------------------------------------------------------
            "projectile_mass": self.driver.find_element_by_id("txt_MassProjectile"),
            "projectile_diameter": self.driver.find_element_by_id("txt_ProjectileDiameter"),
            "wind_speed": self.driver.find_element_by_id("txt_WindSpeed"),
            # ------------------------------------------------------------------------
            "release_angle": self.driver.find_element_by_id("txt_ReleaseAngle")
        }

        # Initially set the input_values to the given initial_values (These will mutate)
        self.input_values = initial_values

        # Initalise the results_list to store the recorded data when conducting tests
        self.results_list = []

    def save_data(self, filename: str, **inputs: list) -> None:
        """ Automatically tests and saves all of the different trebuchet combinations, given a filename and some inputs """

        # Retrieve inputs keys and the lists within the dict
        input_keys = list(inputs)
        input_lists = []
        for key in input_keys:
            input_lists.append(inputs[key])

        # Generate all possible combinations of the input list and add to input_values_list
        input_values_list = []
        for input_combination in itertools.product(*input_lists):
            for i in range(len(input_keys)):
                self.input_values[input_keys[i]] = input_combination[i]
            input_values_list.append(copy.deepcopy(self.input_values))

        # Get and save data
        self.get_data(input_values_list)
        self.save(filename)

    def get_data(self, input_values_list: list) -> None:
        """ Retrives distance and range values for a given dict setup """

        for i in range(len(input_values_list)):
            input_values = input_values_list[i]

            # Update input fields
            for element in self.input_fields:
                value = str(input_values[element])
                current_value = str(
                    self.input_fields[element].get_attribute("value"))

                # Only update input field if values are different
                if value != current_value:
                    self.input_fields[element].clear()
                    self.input_fields[element].send_keys(value)

            # Submit inputted data
            self.driver.find_element_by_xpath(self.SUBMIT_BUTTON_XPATH).click()

            # Get and store the results
            try:
                def wait_until_visible(HTML_id: str): return WebDriverWait(
                    self.driver, self.MAX_WAIT_TIME).until(EC.visibility_of_element_located((By.ID, HTML_id)))

                max_distance = wait_until_visible("maxDistance")
                energy_efficiency = wait_until_visible("energyEfficiency")
                range_efficiency = wait_until_visible("rangeEfficiency")
                release_velocity = wait_until_visible("releaseVelocity")

                # Do not record data if there is an error
                error_message = self.driver.find_element_by_id("errorMessages")
                if str(error_message.text) != "":
                    print(
                        f"Results: {i}/{len(input_values_list)} {str(error_message.text)}")
                    continue

                # Strip the non numeric data
                results = {
                    "max_distance": float(max_distance.text[:-2]),
                    "energy_efficiency": float(energy_efficiency.text),
                    "range_efficiency": float(range_efficiency.text),
                    "release_velocity": float(release_velocity.text[:-4]),
                }

                # Store the results and input values in the results_list
                print(f"Results: {i}/{len(input_values_list)}", results)
                self.results_list.append({**results, **input_values})

            except TimeoutException:
                print("Something went wrong when waiting for results!")

    def save(self, filename: str) -> None:
        """ Save the results as a csv file in the same folder as the script """
        module_path = os.path.dirname(os.path.realpath(__file__))
        output_path = os.path.join(module_path, f'{filename}.csv')

        results_df = pd.DataFrame(self.results_list)
        results_df.to_csv(output_path)

        # Clear results list so that data does not get written multiple times
        self.results_list = []

        print("\n", results_df)

    def quit(self) -> None:
        """ Closes the Chrome instance """

        # Quit the Chrome instance
        self.driver.quit()
