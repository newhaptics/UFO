from pywinauto import Application
import psutil

word_document_windows = []

# Iterate through all WINWORD.EXE processes
for proc in psutil.process_iter(attrs=['pid', 'name']):
    if proc.info['name'] == 'WINWORD.EXE':
        try:
            app = Application().connect(process=proc.info['pid'])
            for win in app.windows():
                title = win.window_text().strip()

                # Ensure title is meaningful and belongs to a real Word document
                if len(title) > 5 and (" - Word" in title or " - Microsoft Word" in title):
                    word_document_windows.append((title, win))
        except Exception as e:
            print(f"Could not access {proc.info['pid']}: {e}")

# Display available Word document windows
if word_document_windows:
    print("\nSelect a Microsoft Word document to bring to the front:")
    for idx, (title, _) in enumerate(word_document_windows):
        print(f"  [{idx + 1}] {title}")

    # Get user selection
    try:
        selection = int(input("\nEnter the number of the document to bring to the front: ")) - 1
        if 0 <= selection < len(word_document_windows):
            selected_window = word_document_windows[selection][1]
            selected_window.set_focus()  # Bring to front
            print(f"\n✅ Brought '{word_document_windows[selection][0]}' to the front!")
        else:
            print("\n❌ Invalid selection. Exiting.")
    except ValueError:
        print("\n❌ Invalid input. Please enter a number.")
else:
    print("\nNo active Microsoft Word document windows found.")
