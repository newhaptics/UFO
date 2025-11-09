from pywinauto import Application
import json

# Step 1: Connect to Microsoft Word
try:
    app = Application(backend="uia").connect(path="WINWORD.EXE")
    word_window = app.window(class_name="OpusApp")
except Exception as e:
    print("Error connecting to Microsoft Word:", e)
    exit()

# Step 2: Locate the MsoDockBottom Pane
try:
    mso_dock_bottom = word_window.child_window(title_re="MsoDockBottom", control_type="Pane")
except Exception as e:
    print("Error locating MsoDockBottom pane:", e)
    exit()

# Step 3: Locate the Status Bar inside MsoDockBottom
try:
    status_bar = mso_dock_bottom.descendants(control_type="StatusBar")
    if not status_bar.exists():
        raise Exception("StatusBar not found inside MsoDockBottom.")
except Exception as e:
    print("Error locating the StatusBar:", e)
    exit()

# Step 4: Extract Status Bar Information
try:
    status_elements = status_bar.children()
    status_info = {}

    for elem in status_elements:
        name = elem.window_text()
        control_type = elem.element_info.control_type

        if name:
            status_info[name] = {
                "control_type": control_type,
                "value": elem.get_value() if hasattr(elem, "get_value") else "N/A"
            }
except Exception as e:
    print("Error extracting status bar information:", e)
    exit()

# Step 5: Convert to JSON and Save
status_json = json.dumps(status_info, indent=4)
with open("word_status_bar.json", "w") as json_file:
    json_file.write(status_json)

print("Status bar information extracted and saved to word_status_bar.json")
