import os
import sys
import subprocess
import io
import contextlib
import platform
import requests
from colorama import Fore, Style
from prompts import *

MODEL = "gpt-4o-mini"
API_URL = "http://127.0.0.1:1234/v1/chat/completions"

# Убедимся, что API_KEY и URL для локальной модели установлены (если нужно)
API_KEY = os.environ.get("API_KEY")

sys.stdout.reconfigure(encoding="utf-8")


# Чтение версии из файла
def read_version():
    version_file = "version.txt"
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            return f.read().strip()
    return "0.0.0"  # Если файла нет, версия по умолчанию


# Запись новой версии в файл
def write_version(version):
    with open("version.txt", "w") as f:
        f.write(version)


# Автоматическое увеличение PATCH версии
def increment_version(version):
    major, minor, patch = map(int, version.split("."))
    patch += 1  # Увеличиваем PATCH версию
    return f"{major}.{minor}.{patch}"


# Функция для раскраски версии
def color_version(version):
    major, minor, patch = version.split(".")
    # Применяем разные цвета для разных частей версии
    colored_version = f"{Fore.RED}{major}{Style.RESET_ALL}.{Fore.YELLOW}{minor}{Style.RESET_ALL}.{Fore.BLUE}{patch}{Style.RESET_ALL}"
    return colored_version


def print_formatted(text, color=Fore.WHITE):
    print(f"{Style.RESET_ALL}{color}{text}{Style.RESET_ALL}")


def clean_code(code):
    between_code_tags = code.split("```")[1] if "```" in code else code.strip("`")
    between_code_tags = between_code_tags.strip()
    if between_code_tags.startswith("python"):
        between_code_tags = between_code_tags[6:]
    return between_code_tags.strip()


def run_code(code):
    print_formatted("Running code:", Fore.YELLOW)
    print_formatted(code, Fore.CYAN)
    try:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(code, globals())
        return True, output.getvalue()
    except Exception as e:
        return False, f"Error: {type(e).__name__}: {str(e)}"


def install_package(error):
    package = error.split("'")[-2]
    print_formatted(f"Installing {package}...", Fore.YELLOW)
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def get_local_model_response(messages):
    headers = {"Authorization": f"Bearer {API_KEY}" if API_KEY else ""}
    payload = {"model": MODEL, "messages": messages}
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error contacting local model: {e}")
        return None


def run_shell():
    memory = [
        {"role": "system", "content": CODE_SYSTEM_CALIBRATION_MESSAGE},
    ]

    # Получаем и увеличиваем версию
    current_version = read_version()
    new_version = increment_version(current_version)
    colored_version = color_version(new_version)  # Раскрасим версию
    print_formatted(
        f"КЛОП {Fore.MAGENTA}Сардаукар{Style.RESET_ALL} ({Fore.YELLOW}Калькулятор Логических Операций Персональный{Style.RESET_ALL}) - Версия {colored_version}",
        Fore.GREEN,
    )
    write_version(new_version)  # Обновляем версию в файле

    print_formatted("Готов к работе и выполнению команд!", Fore.CYAN)

    while True:
        user_input = input(f"{os.getcwd()} {Fore.CYAN}Сардаукар>{Style.RESET_ALL} ")

        if user_input.lower() == "clear":
            os.system("cls" if platform.system() == "Windows" else "clear")
            memory = memory[:1]
            continue

        # Преобразуем ввод в команду для выполнения
        memory.append(
            {"role": "user", "content": USER_MESSAGE(user_input, os.getcwd())}
        )

        # Попробуем подключиться к модели один раз
        response = get_local_model_response(memory)

        if not response:
            print_formatted(
                "Error: Unable to get response from local model. Please check the connection and try again.",
                Fore.RED,
            )
            continue  # Возвращаемся в консоль и ждем новую команду

        # Очистим код, полученный от модели
        code = clean_code(response["choices"][0]["message"]["content"])
        memory.append({"role": "assistant", "content": code})

        # Выполним сгенерированный код
        success, output = run_code(code)

        if success:
            print_formatted(output or "Code executed successfully.", Fore.GREEN)
        elif "No module named" in output or "ImportError" in output:
            install_package(output)
        else:
            print_formatted(output, Fore.RED)
            memory.append({"role": "system", "content": DEBUG_MESSAGE(code, output)})

        memory.append({"role": "system", "content": output})


if __name__ == "__main__":
    if os.name == "nt":
        os.system("")
    run_shell()
