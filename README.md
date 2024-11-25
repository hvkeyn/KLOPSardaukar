# KLOP Sardaukar (Personal Logic Operations Calculator)

## A Command-Line Tool for Interacting with AI Models

KLOP Sardaukar is a personal logic operations calculator built to work with AI models through a command-line interface. This tool allows users to generate code, execute tasks, and perform logical operations using an AI model. It’s perfect for those who need a simple yet powerful tool to run AI-powered operations from their console.

## How to use:
1. Install the requirements with the command:  
   `pip install -r requirements.txt`
   
2. Set the environment variable for API access:
   - For OpenAI, use: `export OPENAI_API_KEY=your_api_key`
   - Or for OpenRouter, use: `export OPENROUTER_API_KEY=your_api_key`

3. Run the program:  
   `python sardaukar.py`

4. **Optional: Working with LM Studio**  
   You can also use **LM Studio** as a local server by setting it up at `http://127.0.0.1:1234`. The application can work in **client mode** to connect directly to a locally running instance of LM Studio, providing an even more powerful and customizable AI experience.

## Key Features:
- **Smart Error Handling**: If there is an issue connecting to the AI model, the program will display an error message and return to the console, waiting for a new command. This avoids continuous retries and allows users to move forward quickly.
- **Version Control**: The tool automatically increments and updates its version, with each part of the version being color-coded for better readability.
- **Code Execution**: Once a command is issued, the program generates the corresponding code and runs it in the console. It can also automatically install missing packages if necessary.
- **AI Interaction**: KLOP interacts with local AI models via API calls, which allows it to generate code based on user inputs, such as performing logical operations or calculations.
- **LM Studio Client Mode**: For those with LM Studio installed, the tool can connect to the local instance of LM Studio, allowing for even faster and more flexible AI processing, without relying on external API services.

### 🌟 **Examples of Use**:
- **General Tasks**:
  - Calculate the Fibonacci sequence and save it as a text file.
  - Create directories and organize files in the current directory based on their type.
  - Fetch weather data for a specific city and display it in a formatted table.
  - Generate a Python script to calculate complex mathematical equations and execute them.

- **Complexity Tests**:
  - Ask the AI to generate code to calculate mathematical derivatives using libraries like SymPy.
  - Request the AI to create a presentation about a scientific topic, such as the Eddington Luminosity.
  - Analyze financial data (e.g., $VIX and $SPY), merge them, and plot the results using libraries like Matplotlib.

- **Safety Tests**:
  - The program runs with built-in safety checks, ensuring that no harmful or undefined behavior occurs when executing arbitrary code. To ensure the integrity of your system, we recommend using a sandboxed environment when testing such scripts.
  - Generate and view an HTML template for displaying content, or even display live camera feeds via an ngrok server.

### 🧠 **Code Overview**:
The `KLOP Sardaukar` is designed to interact with a large language model (LLM) and perform various tasks based on user input. The main components of the system are:

- **prompts.py**: Contains predefined prompts, calibration messages, and instructions for the LLM.
- **sardaukar.py**: The main script that handles user input, interacts with the local AI model (either OpenAI, OpenRouter, or LM Studio), and executes the generated code.

### **How It Works**:
1. **User Input**: The system waits for the user to input a command.
2. **Prompt Generation**: The input is converted into a structured prompt, which is sent to the AI model.
3. **Code Execution**: The model generates the code based on the prompt, and the system attempts to execute it.
4. **Error Handling**: If the code execution fails or dependencies are missing, the system automatically handles the error and installs missing packages.
5. **Output**: The generated output is shown to the user, and the program continues to wait for the next command.

The `KLOP Sardaukar` tool can handle multiple types of tasks, from simple logical operations to complex AI-powered code generation, offering a seamless interface for interacting with models.

---

**Important Notes**:
- The program will not retry endlessly if the AI model is unavailable. If no connection is established, the system will notify the user and return to the command prompt, allowing them to try again.
- Each run automatically increments the version of the program, ensuring the latest improvements and features are in use.
- **Security Warning**: Always use this tool in a controlled environment, as executing arbitrary code could potentially cause issues on your system.

Enjoy the power of AI directly in your terminal with **KLOP Sardaukar** — now with **LM Studio Client Mode** for an even more powerful local experience!