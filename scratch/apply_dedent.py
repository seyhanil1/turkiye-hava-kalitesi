import re

with open("app_pages/future_fork_page.py", "r", encoding="utf-8") as f:
    code = f.read()

# Add import textwrap if not present
if "import textwrap" not in code:
    code = code.replace("import streamlit as st\nimport pandas as pd", "import streamlit as st\nimport pandas as pd\nimport textwrap")

# Replace st.markdown(f""" or st.markdown(""" with textwrap.dedent
# Regex to find st.markdown(f""" or st.markdown("""
# We can do this cleanly:
code = re.sub(
    r'st\.markdown\(f"""([\s\S]*?)""",\s*unsafe_allow_html=True\)',
    r'st.markdown(textwrap.dedent(f"""\1""").strip(), unsafe_allow_html=True)',
    code
)
code = re.sub(
    r'st\.markdown\("""([\s\S]*?)""",\s*unsafe_allow_html=True\)',
    r'st.markdown(textwrap.dedent("""\1""").strip(), unsafe_allow_html=True)',
    code
)

with open("app_pages/future_fork_page.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated app_pages/future_fork_page.py with textwrap.dedent successfully!")
