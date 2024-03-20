import uuid

WIDTH = "1200px"
HEIGHT = "900px"


def set_string_max_width(input_string, max_width):
    sections = input_string.split("\n \n")
    formatted_sections = []
    for section in sections:
        lines = section.split('\n')
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
                
        formatted_sections.append('\n'.join(formatted_lines))

    return "\n \n".join(formatted_sections)


def add_unique_id_to_mynetwork(filename):
    with open(filename, "r") as file:
        html_content = file.read()

    # Replace "mynetwork" in js scripts with "mynetwork+uuid" so that several graphs displayed on the same
    # page don’t collide with one another
    html_content = html_content.replace("mynetwork", f"mynetwork_{str(uuid.uuid4())[:6]}")

    with open(filename, "w") as file:
        file.write(html_content)
