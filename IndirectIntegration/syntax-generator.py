import os
import subprocess
import time
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import OpenAI, Ollama
from langchain_openai import ChatOpenAI
from os.path import expanduser

home = expanduser("~")
ARGOSPATH=os.path.join(home, "software/LLM2Swarm/DirectIntegration/")
default_filepath = os.path.join(ARGOSPATH, "controllers/movement_generated.py")


def get_llm_client(model_name="gpt-4", provider="openai"):
    """
    Initialize the language model client based on the provider. 
    
    :param model_name: The model to use, e.g., "gpt-4" for OpenAI, "llama2" for Ollama.
    :param provider: The provider, either "openai" or "ollama".
    :return: Initialized LLM client.
    """
    if provider == "openai":
        return ChatOpenAI(model=model_name)  # OpenAI GPT models
    elif provider == "ollama":
        return Ollama(model=model_name)  # Local Ollama models
    else:
        raise ValueError("Unsupported provider. Choose 'openai' or 'ollama'.")

def generate_system_prompt(goal, function_name, examples):
    examples_text = "\n\n".join([f"### Example Controller {i+1}:\n{example}" for i, example in enumerate(examples)])

    with open("Vector2D.py", 'r') as file:
        vector2d = file.read()
    
    return f"""
You are creating a controller in Python for the ARGoS robot swarm simulator. 
Goal: {goal}
Class name for newly generated class: {function_name}

Rules:
- Don't call any undefined methods
- The code that you generate will be saved in the file movement_generated.py
- In the main.py controller file, the class that you generated is initialized as follows:
    from controllers.movement_generated import CustomMovement
    rw = CustomMovement(robot, cp['scout_speed'])
- In every timestep, the step function is executed as follows:
    rw.step()
- Do not execute or generate the commands in the two previous bullet points. Your generate script will be executed from main.py, which is static.

Use this information to generate the new controller code.

Here are some successful examples of controllers:
{examples_text}

For your information, the Vector2D class is implemented as follows:
{vector2d}
    """

def generate_system_prompt_without(goal, function_name):
    return f'''
You are creating a controller in Python for the ARGoS robot swarm simulator. 
Goal: {goal}
{function_name}
    '''
    


def load_examples():
    examples_dir = 'controller_examples'
    examples = []
    print("Using the following examples: ")
    if os.path.exists(examples_dir):
        for filename in os.listdir(examples_dir):
            if filename.endswith('.py'):
                print(filename)
                with open(os.path.join(examples_dir, filename), 'r') as file:
                    examples.append(file.read())
    return examples

def extract_python_code(text):
    """
    Extracts Python code from text, specifically looking for code blocks
    enclosed within triple backticks (```python).
    """    
    in_code_block = False
    code_lines = []
    for line in text.splitlines():
        if "```python" in line:
            in_code_block = True
            continue
        elif "```" in line and in_code_block:
            in_code_block = False
            continue
        if in_code_block:
            code_lines.append(line)
    return "\n".join(code_lines)

def generate_code(system_prompt, custom_prompt, llm_client):
    prompt_template = PromptTemplate(
        input_variables=["system_prompt", "custom_prompt"],
        template="""
{system_prompt}
User: {custom_prompt}
""")
    # Create a runnable sequence (prompt -> LLM)
    chain = prompt_template | llm_client | StrOutputParser()
    
    # Generate code using invoke method
    response = chain.invoke({"system_prompt": system_prompt, "custom_prompt": custom_prompt})
    
    save_code_to_file("full_output.txt", response)
    
    return extract_python_code(response)

def save_code_to_file(filepath, code):
    with open(filepath, 'w') as file:
        file.write(code)

def run_argos_and_monitor_errors():
    os.chdir(ARGOSPATH)

    with open('errors.txt', 'w') as error_file:
        process = subprocess.Popen(['./starter', '-s'], stderr=error_file)
    
    error_file_path = 'errors.txt'
    lines_written = 0
    
    while True:
        time.sleep(1)
        with open(error_file_path, 'r') as error_file:
            errors = error_file.readlines()
            lines_written = len(errors)
        
        if lines_written > 0:
            subprocess.call(['killall', 'argos3'])
            process.terminate()
            return errors

        if process.poll() is not None:
            break
    
    return None

def read_input_from_file(filepath):
    with open(filepath, 'r') as file:
        content = file.read()
    return content

def iterative_development():
    filepath = "mygoal.txt"
    goal = input("Enter your goal (e.g., create a flocking algorithm) - or leave empty to read from file mygoal.txt: ") or read_input_from_file(filepath)
    function_name = "CustomMovement"
    examples = load_examples()
    
    if not examples:
        print("Warning: The examples folder is empty.")
        response = input("Would you like to add examples before proceeding? (y/n): ")
        if response.lower() == 'y':
            print("Please add your examples to the 'examples/' directory and restart the script.")
            return
    
    system_prompt = generate_system_prompt(goal, function_name, examples)
    
    # Choose LLM provider and model
    provider = input("Enter the LLM provider (openai/ollama) - default is ollama: ").strip().lower() or "ollama"
    model_name = input("Enter the model name (e.g., gpt-4 for OpenAI or llama2 for Ollama) - default is tinyllama: ").strip() or "qwen2.5-coder:1.5b"
    
    llm_client = get_llm_client(model_name, provider)
    
    first_run = True
    
    while True:
        if first_run:
            custom_prompt = input("Enter your custom prompt for the controller code (e.g., any additional comments): ")
            code = generate_code(system_prompt, custom_prompt, llm_client)
            first_run = False
        else:
            with open(default_filepath, 'r') as code_file:
                latest_code = code_file.read()
            
            additional_comments = input("Enter any additional comments for refining the controller (or press Enter to skip): ")
            custom_prompt = f"""
Errors encountered during ARGoS run:

{''.join(errors)}

Here is the latest controller code:

{latest_code}

{additional_comments}

Please improve the controller.
            """
            print("New prompt")
            print(custom_prompt)
            system_prompt = generate_system_prompt_without(goal, function_name)
            code = generate_code(system_prompt, custom_prompt, llm_client)
        
        save_code_to_file(default_filepath, code)
        
        errors = run_argos_and_monitor_errors()
        
        if errors is None:
            print("ARGoS ran successfully without errors.")
            break
        else:
            print("Errors detected. Feeding them back to the model for correction.")
            print(errors)

if __name__ == "__main__":
    iterative_development()
