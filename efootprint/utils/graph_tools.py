WIDTH = 1200
HEIGHT = 900


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
