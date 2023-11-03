import json
import os
import time

from selenium import webdriver

from efootprint.utils.graph_tools import WIDTH, HEIGHT


def capture_screenshot(html_file_path, output_image_path, width, height):
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(width, height)

    driver.get(f"file://{html_file_path}")
    time.sleep(2)

    driver.save_screenshot(output_image_path)

    driver.quit()


def save_graph_as_both_html_and_png(input_graph, output_filepath, width=WIDTH, height=HEIGHT):
    input_graph.set_options(json.dumps({'physics': {"springLength": 250}}))
    input_graph.show(f"{output_filepath}")
    capture_screenshot(
        os.path.abspath(f"{output_filepath}"), f"{output_filepath.replace('html', 'png')}", width, height)
