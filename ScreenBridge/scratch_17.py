from ufo.automator.ui_control.inspector import ControlInspectorFacade

# Initialize ControlInspectorFacade
inspector = ControlInspectorFacade()

# Get all desktop windows
desktop_windows = inspector.get_desktop_windows()

# Define the target application name
target_app_name = "WINWORD.EXE"  # Change this to the application you want to target

# Filter for the specific application window containing the status bar
app_windows = [
    window
    for window in desktop_windows
    if inspector.get_application_root_name(window) == target_app_name
]

if not app_windows:
    print(f"No application windows found with the name: {target_app_name}")
else:
    # Look for the status bar within each application window
    for window in app_windows:
        print("WORD DOC WINDOW:",window.window_text())
        status_bars = inspector.find_control_elements_in_descendants(
            window, control_type_list=["StatusBar"]
        )

        if not status_bars:
            print(f"No status bar found in the window: {window.window_text()}")
        else:
            for status_bar in status_bars:
                # Now find controls within the status bar, for example, Buttons:
                descendant_buttons = inspector.find_control_elements_in_descendants(
                    status_bar, control_type_list=["Button"]
                )

                if descendant_buttons:
                    for button in descendant_buttons:
                        print(
                            f"Found button control in status bar: {button.window_text()}"
                        )
                else:
                    print(
                        f"No button controls found in the status bar of {window.window_text()}"
                    )
        print("---------------------------------")