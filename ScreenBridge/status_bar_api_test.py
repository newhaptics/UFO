from ufo.automator.ui_control.inspector import ControlInspectorFacade
from status_bar_api import WordWindowAPI  # Assuming your class is saved in 'status_bar_api.py'


def test_status_bar_api():
    # Create an instance of StatusBarAPI
    status_bar_api = WordWindowAPI()

    # Test find_all_windows_by_appname
    appname = "winword.exe"  # This can be changed to test other applications
    windows = status_bar_api.find_all_windows_by_appname(appname)

    if windows:
        print(f"Found {len(windows)} windows for application {appname}:")
        for window in windows:
            print(f"- Window: {window.window_text()}")

            # Test get_all_status_bar_items for each window found
            status_bar_api.get_all_status_bar_items(window)
    else:
        print(f"No windows found for {appname}.")


if __name__ == "__main__":
    test_status_bar_api()
