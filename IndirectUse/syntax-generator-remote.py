import os
import subprocess
import time
from openai import OpenAI
from os.path import expanduser

home = expanduser("~")
ARGOSPATH=os.path.join(home, "software/LLM2Swarm/DirectUse/")
default_filepath = os.path.join(ARGOSPATH, "controllers/movement_generated.py")


# Initialize OpenAI client (API key is implicitly read from the environment variable OPENAIKEY)
client = OpenAI()

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
            if filename.endswith('.py'):  # Assuming examples are Python files
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
            continue  # Skip the line with the backticks
        elif "```" in line and in_code_block:
            in_code_block = False
            continue  # Skip the closing backticks line

        if in_code_block:
            code_lines.append(line)

    return "\n".join(code_lines)

def generate_code(system_prompt, custom_prompt):
    completion = client.chat.completions.create(
        model="gpt-4o",  # Using GPT-4o model
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": custom_prompt}
        ]
    )
    
    save_code_to_file("full_LLM_output_generated_conroller.txt", completion.choices[0].message.content)

    # Extract and return only the Python code from the response
    return extract_python_code(completion.choices[0].message.content)

def save_code_to_file(filepath, code):
    with open(filepath, 'w') as file:
        file.write(code)

def run_argos_and_monitor_errors():
    # Change to the specified directory before running ARGoS
    os.chdir(ARGOSPATH)
    
    with open('errors.txt', 'w') as error_file:
        process = subprocess.Popen(['./starter', '-s'], stderr=error_file)
    
    error_file_path = 'errors.txt'
    lines_written = 0
    
    while True:
        time.sleep(1)  # Small delay to allow ARGoS to run and potentially write errors
        
        with open(error_file_path, 'r') as error_file:
            errors = error_file.readlines()
            lines_written = len(errors)
        
        if lines_written > 0:
            subprocess.call(['killall', 'argos3'])  # Kill all instances of ARGoS if errors are detected
            process.terminate()  # Also kill the specific process
            return errors

        if process.poll() is not None:
            break  # ARGoS finished running without errors
    
    return None

def read_input_from_file(filepath):
    with open(filepath, 'r') as file:
        content = file.read()
    return content

def iterative_development():
    # Initial setup
    filepath = "mygoal.txt"
    goal = input("Enter your goal (e.g., create a spinning algorithm) or leave empty for reading from mygoal.txt: ") or read_input_from_file(filepath)
    function_name = "CustomMovement"
    
    examples = load_examples()
    
    # Check if the examples folder is empty and warn the user
    if not examples:
        print("Warning: The examples folder is empty.")
        response = input("Would you like to add examples before proceeding? (y/n): ")
        if response.lower() == 'y':
            print("Please add your examples to the 'examples/' directory and restart the script.")
            return
    
    system_prompt = generate_system_prompt(goal, function_name, examples)
    
    first_run = True
    
    while True:
        if first_run:
            custom_prompt = input("Enter your custom prompt (e.g. any addtional comments) for the controller code: ")
            code = generate_code(system_prompt, custom_prompt)
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
            system_prompt = generate_system_prompt_without(goal, function_name)  # No examples after first run
            code = generate_code(system_prompt, custom_prompt)
        
        # Save code to file
        save_code_to_file(default_filepath, code)
        
        # Run ARGoS and monitor for errors
        errors = run_argos_and_monitor_errors()
        
        if errors is None:
            print("ARGoS ran successfully without errors.")
            break
        else:
            print("Errors detected. Feeding them back to the model for correction.")
            print(errors)
            # Continue loop with new system_prompt and custom_prompt

if __name__ == "__main__":
    iterative_development()
