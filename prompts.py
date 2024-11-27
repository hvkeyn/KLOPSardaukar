import platform
import getpass

USERNAME = getpass.getuser()
OPERATING_SYSTEM = platform.system()
PYTHON_VERSION = platform.python_version()

THEPIPE_DOCS = """<ThePipe Docs>
from thepipe.scraper import scrape_file
chunks = scrape_file(filepath, local=True) # Always use local=True
response = client.chat.completions.create(
    model="...",
    messages=chunks_to_messages(chunks) + messages, # messages is a prompt in canonical OpenAI dict format that contains instructions
)
Note that in thepipe.core, there exists the class Chunk, which contains scraped text and images for a file:
class Chunk:
    def __init__(self, path: Optional[str] = None, texts: Optional[List[str]] = [], images: Optional[List[Image.Image]] = [], audios: Optional[List] = [], videos: Optional[List] = []):
        self.path = path
        self.texts = texts
        self.images = images
</ThePipe Docs>"""

CODE_SYSTEM_CALIBRATION_MESSAGE = f"""
You are PythonGPT. Please write a full {OPERATING_SYSTEM} Python {PYTHON_VERSION} script to solve the user's problem. Return the full code in ``` blocks. Never give explanations. Do not return any text that is not Python code.
Import all needed requirements at the top of the script.
Always use tqdm to show progress for any loops.
If the task involves reading file contents, you can use ThePipe.
{THEPIPE_DOCS}
Return only the code within ```python blocks. Do not include any explanations, imports, or additional code unless necessary. Ensure the code is executable without modifications.
"""


def USER_MESSAGE(goal, current_dir):
    return f"""
(USER: {USERNAME})
(DIRECTORY: {current_dir})
Write {OPERATING_SYSTEM} python {PYTHON_VERSION} code to solve the following problem: {goal}. The code should print the final result directly. Do not include any explanations or additional code. Use only standard Python syntax.
"""


def DEBUG_MESSAGE(code, error):
    return f"""```python
{code}
```
The above code returns the error "{error}". Please briefly explain in plain English why the error is happening, then write the corrected code in a code box."""  # CoT prompting improves debugging
