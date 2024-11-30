import os
import sys
import subprocess
import io
import contextlib
import requests
from colorama import Fore, Style
from prompts import *  # Importing prompts.py
import importlib

API_URL = "http://127.0.0.1:1234/v1/chat/completions"

sys.stdout.reconfigure(encoding='utf-8')


def read_version():
    version_file = "version.txt"
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            return f.read().strip()
    return "0.0.0"


def write_version(version):
    with open("version.txt", "w") as f:
        f.write(version)


def increment_version(version):
    major, minor, patch = map(int, version.split('.'))
    patch += 1
    return f"{major}.{minor}.{patch}"


def color_version(version):
    major, minor, patch = version.split('.')
    colored_version = f"{Fore.RED}{major}{Style.RESET_ALL}.{Fore.YELLOW}{minor}{Style.RESET_ALL}.{Fore.BLUE}{patch}{Style.RESET_ALL}"
    return colored_version


def print_formatted(text, color=Fore.WHITE):
    print(f"{Style.RESET_ALL}{color}{text}{Style.RESET_ALL}")


def clean_code(code):
    between_code_tags = code.split('```')[1] if '```' in code else code.strip('`')
    between_code_tags = between_code_tags.strip()
    if between_code_tags.startswith("python"):
        between_code_tags = between_code_tags[6:]
    return between_code_tags.strip()


def install_package(error):
    """
    Install the package from error message by extracting the module name
    and ensuring that we install the correct one (without submodules like `editor`).
    """
    # Extract the module name (before the dot) for installation
    package = error.split("'")[-2].split('.')[0]  # Take only the part before the dot
    print_formatted(f"Installing {package}...", Fore.YELLOW)
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    # Reload the installed module to make sure it's available
    try:
        importlib.import_module(package)  # Try reloading the module
        print(f"Module {package} reloaded successfully.")
    except ImportError:
        print(f"Error: Failed to reload the module {package}.")


def get_local_model_response(messages):
    payload = {
        'messages': messages
    }
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error contacting local model: {e}")
        return None


def send_error_to_gpt(code: str, error_message: str, attempt: int) -> str:
    """
    Send the error message and code for fixing by the local model.
    Retry multiple times if necessary.
    Return the fixed code as a string or the same code if no fix is provided.
    """
    print(f"Error occurred: {error_message}")
    print(f"Attempting to fix the code... Attempt #{attempt}")

    # Send the current code for fixing by the model
    prompt = f"""
    The following Python code has the error "{error_message}". Please fix the code:
    ```python
    {code}
    ```
    Provide the corrected code only, no explanations.
    """

    # Request the model to fix the code
    messages = [
        {"role": "system", "content": CODE_SYSTEM_CALIBRATION_MESSAGE},
        {"role": "user", "content": prompt},
    ]

    response = get_local_model_response(messages)

    if response:
        # Extract the corrected code from the model's response
        fixed_code = clean_code(response['choices'][0]['message']['content'])
        print(f"Model fixed the code: {fixed_code}")  # Debug info
        return fixed_code
    else:
        print("Error: Failed to get fixed code from the model.")
        return code  # Return original code if model fails


def apply_changes(code: str, changes: str) -> str:
    """
    Apply the changes to the code string.
    """
    print("Applying changes...")
    return changes + code  # Prepend the fixes to the original code


def run_code(code: str):
    """
    Executes the Python code and returns the result or any error.
    """
    print_formatted("Running code:", Fore.YELLOW)
    print_formatted(code, Fore.CYAN)

    try:
        output = io.StringIO()

        # Debug: Confirm code is being passed to exec()
        print("Before exec...")  # Debug statement

        with contextlib.redirect_stdout(output):
            exec(code, globals())  # Execute the code
            #print_formatted("Exec code! Result:", Fore.YELLOW)  # Debug that exec() happened

        # Capture the result
        result = output.getvalue()

        #print("After exec...")  # Debug statement to check the flow
        #print_formatted(result, Fore.BLUE)
        return True, result

    except Exception as e:
        print(f"Exec failed with error: {str(e)}")  # Debug error message
        return False, f"Error: {type(e).__name__}: {str(e)}"


def run_code_with_error_checking(code: str):
    """Циклическая проверка на ошибки с исправлением"""
    installed_modules = set()  # Track installed modules to avoid reinstallation
    attempts = 0  # Keep track of the number of attempts
    max_attempts = 3  # Set the maximum number of attempts
    module_error_count = {}  # To count repeated errors for specific modules

    while True:
        try:
            print("Executing code...")  # Debug statement
            success, output = run_code(code)  # Запуск сгенерированного кода

            if success:
                print_formatted(output or "Code executed successfully.", Fore.GREEN)
                break  # Выход из цикла, если код выполнен успешно
            elif "No module named" in output or "ImportError" in output:
                # Extract module name from the error message
                missing_module = output.split("'")[1].split('.')[0]
                if missing_module not in installed_modules:
                    install_package(output)  # Устанавливаем недостающие модули
                    installed_modules.add(missing_module)  # Track the installed module
                    module_error_count[missing_module] = 1
                else:
                    module_error_count[missing_module] += 1
                    if module_error_count[missing_module] >= 2:  # If module fails twice
                        print(f"Module '{missing_module}' failed twice. Sending for further fixes...")
                        raise Exception(f"Module '{missing_module}' failed to resolve after 2 attempts.")
                    else:
                        print(f"Module '{missing_module}' already installed, continuing...")
            else:
                print_formatted(f"Error occurred: {output}", Fore.RED)
                raise Exception(f"Script error: {output}")

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Sending error for fixing...")

            # Send error to GPT for fixing with attempt count
            attempts += 1
            fixed_code = send_error_to_gpt(code, str(e), attempts)

            if fixed_code != code:  # Проверяем, были ли изменения
                code = fixed_code  # Обновляем код с исправлениями
                print("Changes applied. Retrying...")
                if attempts >= max_attempts:
                    print("Max attempts reached. Exiting.")
                    break  # Exit if we've reached the max number of attempts
                continue  # Repeat with the fixed code
            else:
                print("No changes applied, stopping.")
                break  # Stop if no changes are made


def run_shell():
    memory = [
        {"role": "system", "content": CODE_SYSTEM_CALIBRATION_MESSAGE},
    ]

    current_version = read_version()
    new_version = increment_version(current_version)
    colored_version = color_version(new_version)
    print_formatted(
        f"КЛОП {Fore.MAGENTA}Сардаукар{Style.RESET_ALL} ({Fore.YELLOW}Калькулятор Логических Операций Персональный{Style.RESET_ALL}) - Версия {colored_version}",
        Fore.GREEN)
    write_version(new_version)
    print_formatted("Готов к работе и выполнению команд!", Fore.CYAN)

    while True:
        user_input = input(f"{os.getcwd()} {Fore.CYAN}Сардаукар>{Style.RESET_ALL} ")

        if user_input.lower() == 'clear':
            os.system("cls" if platform.system() == "Windows" else "clear")
            memory = memory[:1]
            continue

        if user_input.lower() == 'exit':
            break

        memory.append({"role": "user", "content": USER_MESSAGE(user_input, os.getcwd())})

        response = get_local_model_response(memory)

        if not response:
            print_formatted(
                "Error: Unable to get response from local model. Please check the connection and try again.", Fore.RED)
            continue

        code = clean_code(response['choices'][0]['message']['content'])
        memory.append({"role": "assistant", "content": code})

        # Запуск с циклической проверкой на ошибки
        run_code_with_error_checking(code)


if __name__ == "__main__":
    run_shell()