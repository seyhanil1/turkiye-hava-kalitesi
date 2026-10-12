import re

with open("app_pages/future_fork_page.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
in_markdown = False
for line in lines:
    if "st.markdown(" in line:
        in_markdown = True
    if in_markdown:
        # Strip all leading spaces from HTML lines inside markdown
        stripped = line.lstrip()
        if stripped.startswith(("<", "•", "/*", "*", "DSÖ", "{", "}", "<!--", "-->")):
            new_lines.append(stripped)
        elif line.strip().endswith('unsafe_allow_html=True)'):
            new_lines.append(line)
            in_markdown = False
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open("app_pages/future_fork_page.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Stripped all leading spaces from HTML lines in future_fork_page.py!")
