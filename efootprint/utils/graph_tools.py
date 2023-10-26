import os
import json
import time
from selenium import webdriver

WIDTH = 1200
HEIGHT = 900


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


def set_string_max_width(s, max_width):
    lines = s.split('\n')
    formatted_lines = []

    for line in lines:
        words = line.split()
        current_line = []
        current_len = 0

        for word in words:
            if current_len + len(word) > max_width:
                formatted_lines.append(' '.join(current_line))
                current_line = [word]
                current_len = len(word) + 1
            else:
                current_line.append(word)
                current_len += len(word) + 1

        if current_line:
            formatted_lines.append(' '.join(current_line))

    return '\n'.join(formatted_lines)
