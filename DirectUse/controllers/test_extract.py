import re

def extract_info(response_for_human):
    # Extract the activity after "ACTIVITY:"
    activity_match = re.search(r'ACTIVITY:\s*([A-Z\s]+)\n', response_for_human)
    activity = activity_match.group(1).strip() if activity_match else None

    # Extract the coordinates after "TARGET:"
    target_match = re.search(r'TARGET:\s*\(([\d\.\-]+),\s*([\d\.\-]+)\)', response_for_human)
    if target_match:
        coordinates = (float(target_match.group(1)), float(target_match.group(2)))
    else:
        coordinates = None

    return activity, coordinates



mytext = """

Hey, these are the things:
ACTIVITY: TARGETED NAVIGATION
TARGET: (5,8)
"""

act, target = extract_info(mytext) 

if act == "TARGETED NAVIGATION":

    print(act)