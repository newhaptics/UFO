from ufo.automator.ui_control.inspector import ControlInspectorFacade
# Initialize ControlInspectorFacade
inspector = ControlInspectorFacade()

# Get all desktop windows
desktop_windows = inspector.get_desktop_windows()

# Filter for WINWORD.EXE windows
word_windows = []
for window in desktop_windows:
    if inspector.get_application_root_name(window) == "WINWORD.EXE":
       word_windows.append(window)


# Now you have a list of UIAWrapper objects for the WINWORD.EXE application
# Example: Find all Button controls within the filtered word windows
for window in word_windows:
  button_controls = inspector.find_control_elements_in_descendants(
        window, control_type_list=["StatusBar"]
    )
  if button_controls:
    for control in button_controls:
        print(f"Found button control: {control}")
        controls = inspector.find_control_elements_in_descendants(control,depth=4)
        print("controls of the status bar", controls)
  else:
      print(f"No button controls found in {window.window_text()}")
