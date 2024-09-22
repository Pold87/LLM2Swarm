import os
import subprocess
from openai import OpenAI

from os.path import expanduser

home = expanduser("~")
ARGOSPATH=os.path.join(home, "software/LLM2Swarm/DirectIntegration/")
INDIRECTPATH=os.path.join(home, "software/LLM2Swarm/IndirectIntegration/")
default_filepath = os.path.join(ARGOSPATH, "controllers/movement_generated.py")


# Initialize OpenAI client (API key is implicitly read from the environment variable OPENAIKEY)
client = OpenAI()

def load_latest_controller(filepath):
    """
    Load the latest generated controller from the specified file.
    """
    with open(filepath, 'r') as file:
        return file.read()

def generate_refinement_prompt(controller_code, current_behavior, desired_behavior, errors):
    """
    Generate a prompt for refining the controller based on its current behavior and the desired behavior.
    """
    
    with open(os.path.join(INDIRECTPATH, "Vector2D.py"), 'r') as file:
        vector2d = file.read()    
    return f"""
You are improving a controller in Python for the ARGoS robot swarm simulator. 

The current robot swarm controller exhibits the following behavior:

{current_behavior}

If errors occurred during execution, they are stated in the following:
%%% BEGIN ERRORS
{''.join(errors)}
%%% END ERRORS

However, the desired behavior is:

{desired_behavior}

Please modify the following controller code to achieve the desired behavior:

%%% Begin controller code
{controller_code}
%%% End controller code


Here is some more information:

Rules:
- Don't call any undefined methods
- The code that you generate will be saved in the file movement_generated.py
- In the main.py controller file, the class that you generated is initialized as follows:
    from controllers.movement_generated import CustomMovement
    rw = CustomMovement(robot, cp['scout_speed'])
- In every timestep, the step function is executed as follows:
    rw.step()
- Do not execute or generate the commands in the two previous bullet points. Your generate script will be executed from main.py, which is static.


For your information, the Vector2D class is implemented as follows:
{vector2d}


"""

def generate_refined_code(prompt):
    """
    Generate refined controller code based on the provided prompt.
    """
    completion = client.chat.completions.create(
        model="gpt-4o",  # Using GPT-4o model
        temperature=0.4,
        messages=[
            {"role": "system", "content": "You are an expert in swarm robotics and control algorithms."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return extract_python_code(completion.choices[0].message.content)

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

def save_code_to_file(filepath, code):
    """
    Save the refined controller code to the specified file.
    """
    with open(filepath, 'w') as file:
        file.write(code)

def run_argos(timeout=60):
    """
    Run the ARGoS simulator using the `starter` script with a timeout.
    """
    # Change to the specified directory before running ARGoS
    os.chdir(ARGOSPATH)
    
    with open('errors.txt', 'w') as error_file:
        process = subprocess.Popen(['./starter', '-s'], stderr=error_file)
        
    try:
        # Wait for the process to complete or timeout
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        print("ARGoS process timed out. Terminating...")
        process.kill()
        subprocess.call(['killall', 'argos3'])
    return process

def check_for_errors():
    """
    Check if the errors.txt file exists and is not empty.
    """
    error_file_path = os.path.join(ARGOSPATH, "errors.txt")
    if os.path.exists(error_file_path):
        with open(error_file_path, 'r') as file:
            errors = file.readlines()
            if len(errors) > 1:
                return True, errors
    return False, []

def generate_error_prompt(controller_code, errors):
    """
    Generate a prompt to ask ChatGPT to fix errors in the controller code.
    """
    return f"""
The following errors were encountered while running the ARGoS simulation:

{''.join(errors)}

The current controller code is as follows:

{controller_code}

Please fix the errors in the above code to ensure the ARGoS simulation runs correctly.
"""

def iterative_refinement():
    # Default file path
    
    # Get the desired behavior once at the beginning
    desired_behavior = input("Describe the desired behavior of the robots: ")

    while True:

        # Load the latest controller
        latest_code = load_latest_controller(default_filepath)
        
        # Run ARGoS
        process = run_argos()

        # Continue refinement?
        response = input("Would you like to refine the controller further? Press Ctrl + c for exit: ")
        
        # Wait for the user to describe the current behavior
        current_behavior = input("Describe the current behavior of the robots: ")
        
        # Check for errors in the errors.txt file
        has_errors, errors = check_for_errors()
        #if has_errors:
        # Kill ARGoS if there are errors
        process.kill()
        subprocess.call(['killall', 'argos3'])
        print("ARGoS terminated.")
        print("Errors: ", "\n".join(errors))
            
        # Generate error prompt for ChatGPT
        #error_prompt = generate_error_prompt(latest_code, errors)
        #refined_code = generate_refined_code(error_prompt)
        
        # Generate refinement prompt
        prompt = generate_refinement_prompt(latest_code, current_behavior, desired_behavior, errors)

        print(prompt)
        
        refined_code = generate_refined_code(prompt)
        
        # Save the refined code back to the file
        save_code_to_file(default_filepath, refined_code)
        

if __name__ == "__main__":
    iterative_refinement()
