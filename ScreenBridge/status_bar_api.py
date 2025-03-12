from pywinauto.controls.uiawrapper import UIAWrapper
import pywinauto
from ufo.automator.ui_control.inspector import ControlInspectorFacade
from ufo.automator.ui_control.controller import ControlReceiver
class WordWindowAPI():
    def __init__(self):
        self.inspector = ControlInspectorFacade(backend="uia")
        self.desktop_windows = self.inspector.get_desktop_windows()
        self.app_window = None

    def find_all_windows_by_appname(self, appname="winword.exe", close_dialogs=True):
        target_app_name = appname.upper()
        main_windows = []
        dialogs_to_close = []

        for window in self.desktop_windows:
            if self.inspector.get_application_root_name(window) == target_app_name:
                # Multiple checks to identify main Word windows
                is_main_window = False

                # Check 1: Ribbon elements existence
                try:
                    ribbon_elements = window.descendants(title="Ribbon", control_type="Pane", depth=20)
                    if ribbon_elements:
                        is_main_window = True
                except:
                    pass

                # Check 2: Main document window typically has "Document" control
                try:
                    document_elements = window.descendants(control_type="Document", depth=10)
                    if document_elements:
                        is_main_window = True
                except:
                    pass

                # Check 3: Window title ends with "- Word"
                title = window.window_text()
                if title and title.endswith("- Word"):
                    is_main_window = True

                if is_main_window:
                    main_windows.append(window)
                elif close_dialogs:
                    # Additional safety check - don't add main document window to dialogs list
                    if not (title and "Word" in title and "Count" not in title and "Dialog" not in title):
                        dialogs_to_close.append(window)

        # Handle dialogs only after identifying all main windows
        if close_dialogs and dialogs_to_close:
            # Safety check - don't close if we're about to close the only window
            if len(main_windows) == 0 and len(dialogs_to_close) == 1:
                print("Only one Word window found, keeping it open")
                return dialogs_to_close

            for dialog in dialogs_to_close:
                try:
                    # One more safety check before closing
                    if dialog in main_windows:
                        print(f"Skipping closure of potential main window: {dialog.window_text()}")
                        continue

                    close_buttons = dialog.descendants(
                        control_type="Button",
                        title="Close",
                        depth=5
                    )

                    if close_buttons:
                        print(f"Found 'Close' button for dialog: {dialog.window_text()}")
                        close_buttons[0].click()
                    else:
                        close_pane_buttons = dialog.descendants(
                            control_type="Button",
                            title="Close pane",
                            depth=5
                        )
                        if close_pane_buttons:
                            print(f"Found 'Close pane' button for dialog: {dialog.window_text()}")
                            close_pane_buttons[0].click()
                        else:
                            print(f"No close button found for dialog: {dialog.window_text()}")
                except Exception as e:
                    print(f"Failed to close dialog {dialog.window_text()}: {str(e)}")

        if not main_windows:
            if dialogs_to_close:
                print("No main windows found, but dialogs exist. Keeping dialogs.")
                return dialogs_to_close
            print(f"No windows found for: {target_app_name}")
            return []

        return main_windows

    def get_word_count_window_items(self, window):
        # Find the Word Count window
        word_count_window = window.descendants(
            control_type="Window",
            title="Word Count"
        )

        if not word_count_window:
            print("Word Count window not found")
            return {}

        # Get all text and button elements
        word_count_elements = self.inspector.find_control_elements_in_descendants(
            word_count_window[0],
            control_type_list=["Text", "Button"]
        )

        # Format the statistics into a numbered dictionary
        response = {0: "Statistics"}
        index = 1

        # Extract the statistics values in order
        stats_order = ["Pages", "Words", "Characters (no spaces)",
                       "Characters (with spaces)", "Paragraphs", "Lines"]

        # Process each statistic in order
        for stat_name in stats_order:
            for element in word_count_elements:
                if element.control_type == "Text" and stat_name in element.name:
                    value = element.name.split()[-1]
                    response[index] = f"{stat_name}: {value}"
                    index += 1
                    break

        # Add checkbox as the last item
        checkbox = word_count_window[0].descendants(
            control_type="CheckBox",
            title="Include textboxes, footnotes and endnotes"
        )
        if checkbox:
            response[index] = checkbox[0]

        return response

    def get_grammar_check_menu_items(self, window, button):
        self.app_window = window
        self.app_window.set_focus()
        print("WORD DOC WINDOW:", window.window_text())

        # Define the structure of the result dictionary upfront
        result = {
            "score": None,
            "Corrections": {
                "Spelling": None,
                "Grammar": None
            },
            "Refinements": {
                "Clarity": None,
                "Conciseness": None,
                "Formality": None
            }
        }

        # First, find the MsoDockRight pane
        mso_dock_right = window.descendants(
            control_type="Pane",
            title="MsoDockRight",
            depth=10
        )

        if not mso_dock_right:
            self.invoke_button(button)
            print("MsoDockRight pane not found, trying with greater depth...")
            mso_dock_right = window.descendants(
                control_type="Pane",
                title="MsoDockRight",
                depth=10
            )

        if mso_dock_right:
            # Find the Editor pane which is a child of MsoDockRight
            editor_pane = mso_dock_right[0].descendants(
                control_type="Window",
                title="Editor",
                depth=2
            )

            if editor_pane:
                # Check if we're in a spell check detail view and need to go back
                # Look for the "Back" button that indicates we're in a detail view
                back_buttons = editor_pane[0].descendants(
                    control_type="Button",
                    title="Back",
                    depth=5
                )

                if back_buttons:
                    print("Found 'Back' button - we're in a spell check detail view")
                    print("Clicking 'Back' button to return to main Editor view...")
                    back_buttons[0].click()

                    # Wait a moment for the UI to update
                    import time
                    time.sleep(0.5)

                    # Re-find the Editor pane after clicking back
                    editor_pane = mso_dock_right[0].descendants(
                        control_type="Window",
                        title="Editor",
                        depth=2
                    )

                    if not editor_pane:
                        print("Editor pane not found after clicking Back button")
                        return None

                # Look for Editor Score
                # Using string matching after retrieval instead of regex
                score_buttons = [b for b in editor_pane[0].descendants(
                    control_type="Button",
                    depth=5
                ) if "Editor Score" in b.window_text()]

                if score_buttons:
                    result["score"] = score_buttons[0]
                else:
                    # Alternative approach if button not found
                    # Using string matching after retrieval
                    score_texts = [t for t in editor_pane[0].descendants(
                        control_type="Text",
                        depth=5
                    ) if "Editor Score" in t.window_text()]
                    if score_texts:
                        result["score"] = score_texts[0]

                # Find elements for each category
                for category in ["Corrections", "Refinements"]:
                    category_groups = editor_pane[0].descendants(
                        control_type="Group",
                        title=category,
                        depth=5
                    )

                    if category_groups:
                        category_group = category_groups[0]

                        # Find subcategories for this category
                        if category == "Corrections":
                            subcategories = ["Spelling", "Grammar"]
                        else:  # Refinements
                            subcategories = ["Clarity", "Conciseness", "Formality"]

                        for subcategory in subcategories:
                            # Find buttons or groups for this subcategory
                            # Get all elements and filter by text content
                            all_elements = category_group.descendants(depth=3)
                            subcategory_elements = [e for e in all_elements
                                                    if subcategory in e.window_text()]

                            if subcategory_elements:
                                # Store the first matching element
                                result[category][subcategory] = subcategory_elements[0]

                # Print what we found for debugging
                print(f"Found score element: {'Yes' if result['score'] else 'No'}")

                for category in ["Corrections", "Refinements"]:
                    found_items = [k for k, v in result[category].items() if v is not None]
                    print(f"Found {category} items: {found_items}")

                return result
            else:
                print("Editor pane not found inside MsoDockRight")
        else:
            print("MsoDockRight pane not found")

        return None

    def get_navigation_pane_items(self, window,button):
        """
        Get specific elements from the Word Navigation pane:
        - Search document edit box
        - Search button
        - Headings tab
        - Pages tab
        - Results tab

        Returns a dictionary with these elements organized by type
        """
        self.app_window = window
        self.app_window.set_focus()

        # Find the MsoDockLeft pane which contains the Navigation panel
        navigation_pane = window.descendants(
            control_type="Pane",
            title="MsoDockLeft",
            depth=3  # Shallower depth for better performance
        )

        if not navigation_pane:
            self.invoke_button(button)
            print("Navigation pane not found, trying with greater depth...")
            navigation_pane = window.descendants(
                control_type="Pane",
                title="MsoDockLeft",
                depth=10
            )

        result = {
            "search_box": None,
            "search_button": None,
            "tabs": {
                "Headings": None,
                "Pages": None,
                "Results": None
            }
        }

        if navigation_pane:
            nav_pane = navigation_pane[0]

            # 1. Find the Search document edit box
            search_boxes = nav_pane.descendants(
                control_type="Edit",
                title="Search document",
                depth=10
            )
            if search_boxes:
                result["search_box"] = search_boxes[0]

            # 2. Find the Search button (part of a SplitButton control)
            split_buttons = nav_pane.descendants(
                control_type="SplitButton",
                title="Search",
                depth=10
            )
            if split_buttons:
                # Get the actual button part of the split button
                search_button = split_buttons[0].children(control_type="Button")
                if search_button:
                    result["search_button"] = search_button[0]

            # 3. Find the Tab Items (Headings, Pages, Results)
            tab_items = nav_pane.descendants(
                control_type="TabItem",
                depth=10
            )

            # Filter tabs by their names
            for tab in tab_items:
                tab_name = tab.window_text()
                if tab_name in ["Headings", "Pages", "Results"]:
                    result["tabs"][tab_name] = tab

            # Print what we found for debugging
            print(f"Found search box: {'Yes' if result['search_box'] else 'No'}")
            print(f"Found search button: {'Yes' if result['search_button'] else 'No'}")
            print(f"Found tabs: {[k for k, v in result['tabs'].items() if v is not None]}")

            return result
        else:
            print("Navigation pane not found")
            return None

    def get_all_status_bar_items(self, window, excluded_items=None):
        """
        Reliably access status bar items in Microsoft Word by closing interfering panes
        and locating the status bar.

        Args:
            window: The application window
            excluded_items: Optional list of strings to exclude items with matching window_text
        """
        self.app_window = window
        self.app_window.set_focus()

        # Send Alt+Ctrl+P keyboard shortcut
        # import pywinauto
        # pywinauto.keyboard.send_keys('^%p')  # ^ is Ctrl, % is Alt, p is P

        # Initialize empty list if excluded_items is None
        if excluded_items is None:
            excluded_items = []

        def close_accessibility_assistant():
            """Specifically close the Accessibility Assistant pane if open"""
            # Find the Accessibility Assistant pane
            accessibility_panes = window.descendants(
                control_type="Pane",
                title="Accessibility Assistant",
                depth=10
            )
            if accessibility_panes:
                pane = accessibility_panes[0]
                print("Found Accessibility Assistant pane, attempting to close...")

                close_buttons = accessibility_panes[0].children(control_type="Button")
                if close_buttons:
                    print("Clicking close button in title bar")
                    close_buttons[-1].click()
                    return True

                # If no title bar or couldn't find button there, look for any close button
                close_buttons = pane.descendants(control_type="Button")
                # Filter buttons that might be close buttons
                for btn in close_buttons:
                    btn_text = btn.name()
                    if btn_text in ["X", "×", "Close Pane", "Close"]:
                        print(f"Found potential close button: '{btn_text}'")
                        btn.click()
                        return True

            return False

        def close_interfering_panes():
            """Close known panes that might interfere with status bar access"""
            # Close these panes in order of likelihood to interfere
            pane_types = [
                {"name": "Accessibility Assistant", "title": "Accessibility Assistant"},
                {"name": "Editor", "title": "Editor"},
                {"name": "Navigation", "title": "Navigation"},
            ]

            for pane_type in pane_types:
                panes = window.descendants(
                    control_type="Pane",
                    title=pane_type["title"],
                    depth=10
                )

                for pane in panes:
                    print(f"Found {pane_type['name']} pane, closing...")

                    # Try to find a specific "Close pane" button first
                    close_pane_button = pane.descendants(
                        control_type="Button",
                        title="Close pane",
                        depth=5
                    )

                    if close_pane_button:
                        print("Found 'Close pane' button")
                        close_pane_button[0].click()
                        continue

                    # Next try to find any close button in the title bar
                    title_bars = pane.children(control_type="TitleBar")
                    if title_bars:
                        buttons = title_bars[0].children(control_type="Button")
                        # Usually the last button is the close button
                        if buttons:
                            print("Clicking close button in title bar")
                            buttons[-1].click()
                            continue

                    # Last resort: Look for X button elsewhere
                    all_buttons = pane.descendants(control_type="Button", depth=5)
                    for button in all_buttons:
                        button_text = button.window_text().strip()
                        if button_text in ["X", "×", "Close", ""]:
                            print(f"Clicking potential close button: '{button_text}'")
                            button.click()
                            break

        # First, close any panes that might be in the way
        close_interfering_panes()

        # Specifically handle Accessibility Assistant as it's mentioned as a problem
        if close_accessibility_assistant():
            import time
            time.sleep(0.5)  # Brief pause after closing

        # Now search for the status bar
        panes = window.descendants(control_type="Pane", depth=10)
        mso_dock_bottom_panes = [pane for pane in panes if "MsoDockBottom" in pane.window_text()]

        if not mso_dock_bottom_panes:
            print("MsoDockBottom pane not found, trying direct status bar search...")
            # Try to find status bar directly
            status_bars = window.descendants(control_type="StatusBar", depth=15)
        else:
            # Search for StatusBars within the MsoDockBottom pane
            status_bars = mso_dock_bottom_panes[0].descendants(control_type="StatusBar")

        if not status_bars:
            print("No status bars found. Status bar might be hidden or disabled.")
            return None

        status_bar = status_bars[0]

        # Find controls within the status bar
        descendant_controls = self.inspector.find_control_elements_in_descendants(
            status_bar,
            control_type_list=["Button", "Slider", "Text"]
        )

        if descendant_controls:
            # First pass: collect all items and identify special cases
            filtered_items = []  # Store (item, is_zoom_percentage) tuples
            zoom_percentage_items = []  # Store only the zoom percentage items
            zoom_in_out_items = []  # Store only zoom in/out items
            other_items = []  # Store all other items

            import re
            zoom_percentage_pattern = re.compile(r'^Zoom\s+\d+%$')

            # To store the specific buttons we need as strings
            page_number_str = None
            language_str = None
            text_predictions_str = None
            accessibility_checker_str = None

            for item in descendant_controls:
                # Check if interactive or has meaningful text
                is_interactive = getattr(item.element_info.element, 'CurrentIsKeyboardFocusable', False)
                has_text = item.window_text().strip() != ""
                item_text = item.window_text().strip()

                # We now handle capturing specific buttons in the code block below

                # Check if it's one of our special buttons to capture as string only
                is_special_button = False
                if "Page Number" in item_text:
                    page_number_str = item_text
                    should_exclude = True
                    is_special_button = True
                elif "Language" in item_text:
                    language_str = item_text
                    should_exclude= True
                    is_special_button = True
                elif "Text Predictions" in item_text:
                    text_predictions_str = item_text
                    is_special_button = True
                elif "Accessibility Checker" in item_text or "Accessibility:" in item_text:
                    accessibility_checker_str = item_text
                    is_special_button = True

                # Skip if it's a special button (to be included only as string)
                if is_special_button:
                    continue

                # Skip excluded items
                should_exclude = False
                for excluded_text in excluded_items:
                    if excluded_text == item_text:  # Exact match exclusion
                        should_exclude = True
                        print(f"Excluding item with exact text: '{item_text}'")
                        break

                if should_exclude:
                    continue

                # Only include interactive or text-containing items
                if is_interactive or has_text:
                    # Categorize by type
                    if zoom_percentage_pattern.match(item_text):
                        # This is a "Zoom XX%" button
                        zoom_percentage_items.append(item)
                        print(f"Found zoom percentage {item.element_info.control_type}: '{item_text}'")
                    elif item_text in ["Zoom In", "Zoom Out"]:
                        # This is a zoom in/out button
                        zoom_in_out_items.append(item)
                        print(f"Found zoom control {item.element_info.control_type}: '{item_text}'")
                    else:
                        # This is another type of button
                        other_items.append(item)
                        print(f"Found other {item.element_info.control_type} in status bar: '{item_text}'")

            # Create result dictionary with ordered items
            result_dict = {}
            idx = 0

            # Add other items first
            for item in other_items:
                result_dict[idx] = item
                idx += 1

            # Add zoom percentage items next (before zoom in/out)
            for item in zoom_percentage_items:
                result_dict[idx] = item
                idx += 1

            # Add zoom in/out items last
            for item in zoom_in_out_items:
                result_dict[idx] = item
                idx += 1

            # Add the specific button strings to the result
            if page_number_str:
                result_dict["page_number"] = page_number_str
            if language_str:
                result_dict["language"] = language_str
            if text_predictions_str:
                result_dict["text_predictions"] = text_predictions_str
            if accessibility_checker_str:
                result_dict["accessibility_checker"] = accessibility_checker_str

            if not result_dict:
                print("No non-excluded controls found in the status bar")
                return None

            return result_dict
        else:
            print("No controls found in the status bar")
            return None

    def access_language_dialog(self, window, button):
        """
        Find and interact with the Language dialog in Word
        Returns a dictionary with UI automation objects
        """
        # Get button text for Language heading
        language_heading = button.window_text() if button else "N/A"

        # Define the structure of the result dictionary
        result = {
            "dialog": None,
            "language_list": None,
            "radio_buttons": {
                "selected_text": None,
                "current_document": None
            },
            "checkboxes": {
                "do_not_check_spelling": None,
                "detect_language": None
            }
        }

        # Find the Language dialog window
        language_dialog = window.descendants(
            title="Language",
            control_type="Window",
            depth=3
        )

        if not language_dialog:
            print("Language dialog not found")
            return None

        result["dialog"] = language_dialog[0]

        # Extract language list
        language_lists = result["dialog"].descendants(control_type="List")
        if not language_lists:
            print("Language list not found")
            return None

        result["language_list"] = language_lists[0]

        # Get all languages from the list
        all_languages = []
        if result["language_list"]:
            all_languages = [item.window_text() for item in result["language_list"].children()]

        # Get radio buttons
        selected_text_radios = result["dialog"].descendants(
            title="Selected text",
            control_type="RadioButton"
        )

        current_document_radios = result["dialog"].descendants(
            title="Current Document",
            control_type="RadioButton"
        )

        if selected_text_radios:
            result["radio_buttons"]["selected_text"] = selected_text_radios[0]

        if current_document_radios:
            result["radio_buttons"]["current_document"] = current_document_radios[0]

        # Get checkboxes
        do_not_check_spelling = result["dialog"].descendants(
            title="Do not check spelling or grammar",
            control_type="CheckBox"
        )

        detect_language = result["dialog"].descendants(
            title="Detect language automatically",
            control_type="CheckBox"
        )

        if do_not_check_spelling:
            result["checkboxes"]["do_not_check_spelling"] = do_not_check_spelling[0]

        if detect_language:
            result["checkboxes"]["detect_language"] = detect_language[0]

        # Get "Change proofing language for" text element
        change_proofing_text = result["dialog"].descendants(
            title="Change proofing language for:",
            control_type="Text"
        )

        # Find the selected language item in the list
        selected_language = None
        if result["language_list"]:
            list_items = result["language_list"].children()
            for item in list_items:
                if item.is_selected() == 1:
                    selected_language = item
                    break

        def clean_language_string(text):
            # Method 1: Using string replace for specific escape sequences
            text = text.replace('\uffff', '').replace('\x02', '')

            # Method 2: Using regex to remove all non-printable characters
            import re
            text = re.sub(r'[^\x20-\x7E]', '', text)

            # Method 3: Filter out all control characters
            result = ''.join(char for char in text if ord(char) >= 32 or char == '\n')

            return result
        # Structure the result according to the requested format
        structured_result = {
            "Language": language_heading,
            "Available language": {
                "0": "Available language :",
                "1": "   "+clean_language_string(", ".join(all_languages[:2] if all_languages else [])),
                "2": "   "+str(len(all_languages) - 3 if len(all_languages) > 3 else 0) + " more"
            },
            "Proofing Lang": {
                "change_proofing_text": change_proofing_text[0] if change_proofing_text else None,
                "selected_text": result["radio_buttons"]["selected_text"],
                "current_document": result["radio_buttons"]["current_document"]
            },
            "Checkbox": {
                "do_not_check_spelling": result["checkboxes"]["do_not_check_spelling"],
                "detect_language": result["checkboxes"]["detect_language"]
            }
        }

        # Print the structure for reference
        print(f"\n{structured_result['Language']}:")
        if selected_language:
            print(f"Selected: {selected_language.window_text()}")

        preview_langs = [lang for lang in structured_result["Available language"]["1"]]
        print(f"Available language: {preview_langs} and {structured_result['Available language']['2']} ")

        print("Radio buttons: {")
        print(
            f"    selected_text: {'Selected' if structured_result['Proofing Lang']['selected_text'] and structured_result['Proofing Lang']['selected_text'].is_selected() == 1 else 'Not Selected'},")
        print(
            f"    current_document: {'Selected' if structured_result['Proofing Lang']['current_document'] and structured_result['Proofing Lang']['current_document'].is_selected() == 1 else 'Not Selected'}")
        print("}")

        print("Checkbox: {")
        print(
            f"    do_not_check_spelling: {'Checked' if structured_result['Checkbox']['do_not_check_spelling'] and structured_result['Checkbox']['do_not_check_spelling'].get_toggle_state() == 1 else 'Not Checked'},")
        print(
            f"    detect_language: {'Checked' if structured_result['Checkbox']['detect_language'] and structured_result['Checkbox']['detect_language'].get_toggle_state() == 1 else 'Not Checked'}")
        print("}")

        return structured_result

    def get_accessibility_assistant_items(self, window, button):
        """
        Get specific elements from the Word Accessibility Assistant pane:
        - "Looks good No issues" button
        - Color and Contrast group and its buttons
        - Media and Illustration group and its buttons
        - Tables group and its buttons
        - Document Structure group and its buttons
        - Document Access group and its buttons

        Returns a dictionary with these elements organized by group in a flattened structure
        """
        self.app_window = window
        self.app_window.set_focus()

        # Find the MsoDockRight pane which contains the Accessibility Assistant
        accessibility_pane = window.descendants(
            control_type="Pane",
            title="MsoDockRight",
            depth=10
        )

        if not accessibility_pane:
            self.invoke_button(button)
            print("Accessibility pane not found, trying with greater depth...")
            accessibility_pane = window.descendants(
                control_type="Pane",
                title="MsoDockRight",
                depth=10
            )

        # Create a flattened structure where buttons are at the same level as group
        result = {
            "looks_good_button": None,
            "color_contrast": {},
            "media_illustration": {},
            "tables": {},
            "document_structure": {},
            "document_access": {}
        }

        if accessibility_pane:
            pane = accessibility_pane[0]

            # 1. Find the "Looks good No issues" button
            looks_good_buttons = pane.descendants(
                control_type="Button")
            if looks_good_buttons:
                btn = [button for button in looks_good_buttons if
                       "looks good" in button.window_text().lower() or "keep going" in button.window_text().lower()]
                # Filter out the debug/placeholder button
                real_buttons = [button for button in btn if "Checking Button Text" not in button.window_text()]
                if real_buttons:
                    result["looks_good_button"] = real_buttons[0]

            # 2. Find all groups
            groups = pane.descendants(
                control_type="Group",
                depth=10
            )

            # Process each group
            for group in groups:
                group_name = group.window_text()
                buttons = group.children(control_type="Button")

                # Color and Contrast group
                if "Color and Contrast" in group_name:
                    result["color_contrast"]["group"] = group
                    # Add buttons directly to the color_contrast dictionary with numerical keys
                    for i, button in enumerate(buttons):
                        result["color_contrast"][f"button_{i + 1}"] = button

                # Media and Illustration group
                elif "Media and Illustration" in group_name:
                    result["media_illustration"]["group"] = group
                    for i, button in enumerate(buttons):
                        result["media_illustration"][f"button_{i + 1}"] = button

                # Tables group
                elif "Tables" in group_name:
                    result["tables"]["group"] = group
                    for i, button in enumerate(buttons):
                        result["tables"][f"button_{i + 1}"] = button

                # Document Structure group
                elif "Document Structure" in group_name:
                    result["document_structure"]["group"] = group
                    for i, button in enumerate(buttons):
                        result["document_structure"][f"button_{i + 1}"] = button

                # Document Access group
                elif "Document Access" in group_name:
                    result["document_access"]["group"] = group
                    for i, button in enumerate(buttons):
                        result["document_access"][f"button_{i + 1}"] = button

            # Print summary of what we found
            print(f"Found 'Looks good' button: {'Yes' if result['looks_good_button'] else 'No'}")

            # Update summary prints to reflect new structure
            print(
                f"Found Color and Contrast group: {'Yes' if 'group' in result['color_contrast'] else 'No'} with {len(result['color_contrast']) - ('group' in result['color_contrast'])} buttons")
            print(
                f"Found Media and Illustration group: {'Yes' if 'group' in result['media_illustration'] else 'No'} with {len(result['media_illustration']) - ('group' in result['media_illustration'])} buttons")
            print(
                f"Found Tables group: {'Yes' if 'group' in result['tables'] else 'No'} with {len(result['tables']) - ('group' in result['tables'])} buttons")
            print(
                f"Found Document Structure group: {'Yes' if 'group' in result['document_structure'] else 'No'} with {len(result['document_structure']) - ('group' in result['document_structure'])} buttons")
            print(
                f"Found Document Access group: {'Yes' if 'group' in result['document_access'] else 'No'} with {len(result['document_access']) - ('group' in result['document_access'])} buttons")

            return result
        else:
            print("Accessibility pane not found")
            return None

    def get_accessibility_issue_elements(self, window):
        """
        Get only the specified elements from Word Accessibility Assistant issue pane.
        Returns a simplified dictionary with only the required elements for each issue type.
        """
        self.app_window = window
        self.app_window.set_focus()

        # Find the Accessibility Assistant pane
        accessibility_pane = window.descendants(
            control_type="Pane",
            title="MsoDockRight",
            depth=10
        )

        result = {}

        if accessibility_pane:
            pane = accessibility_pane[0]

            # Find the Custom Control that contains the Accessibility Assistant UI
            accessibility_control = pane.descendants(
                control_type="Custom",
                title="Accessibility Assistant",
                depth=5
            )

            if accessibility_control:
                assistant_ui = accessibility_control[0]

                # Get all Text elements
                text_elements = assistant_ui.descendants(control_type="Text", depth=10)

                # Get all buttons
                all_buttons = assistant_ui.descendants(control_type="Button", depth=10)

                # Find the issue title and determine issue type
                issue_title = None
                issue_type = None

                for text in text_elements:
                    text_content = text.window_text()
                    if " of " in text_content and " - " in text_content:
                        issue_title = text
                        result["issue_title"] = text

                        # Determine the issue type from the title
                        if "Color and Contrast" in text_content:
                            issue_type = "color_contrast"
                        elif "Media and Illustrations" in text_content:
                            issue_type = "missing_alt_text"
                        elif "Document Structure" in text_content:
                            issue_type = "document_structure"
                        break

                # Common buttons for all issue types
                for button in all_buttons:
                    button_name = button.window_text().lower()

                    # Back button - specifically look for exact 'back' text
                    if button_name == "back":
                        result["back_button"] = button

                    # Previous issue button
                    elif "previous issue" in button_name:
                        result["previous_issue_button"] = button

                    # Next issue button
                    elif "next issue" in button_name:
                        result["next_issue_button"] = button

                # Process specific elements based on issue type
                if issue_type == "color_contrast":
                    # For Color and Contrast issues
                    # Find the issue header (Hard-to-read text contrast)
                    for text in text_elements:
                        text_content = text.window_text().lower()
                        if "hard-to-read" in text_content and text != issue_title:
                            result["issue_header"] = text
                            break

                    # Find "Try one of these colors to resolve" text
                    for text in text_elements:
                        text_content = text.window_text().lower()
                        if "try one of these colors" in text_content:
                            result["try_colors_text"] = text
                            break

                    # Find color option buttons - specifically look for the three unlabelled buttons
                    # These are typically square color swatches with no text
                    color_buttons = []
                    unlabelled_buttons = []

                    # First collect all unlabelled buttons
                    for button in all_buttons:
                        button_name = button.window_text()
                        if button_name == "" or button_name == " ":
                            rect = button.rectangle()
                            # Color swatches are typically small and square
                            if rect.width() < 50 and rect.height() < 50 and abs(rect.width() - rect.height()) < 10:
                                unlabelled_buttons.append(button)

                    # From the tree view in the screenshot, we can see there are exactly 3 unlabelled buttons
                    # in a row that represent the color options
                    if len(unlabelled_buttons) >= 3:
                        # Take the first 3 unlabelled buttons that are likely the color options
                        for i in range(min(3, len(unlabelled_buttons))):
                            color_buttons.append(unlabelled_buttons[i])
                            result[f"color_button_{i + 1}"] = unlabelled_buttons[i]

                    # Make sure we don't return "Page Background" button in our filtered results
                    # unless specifically requested
                    page_background_button = None
                    for button in all_buttons:
                        if "page background" in button.window_text().lower():
                            page_background_button = button
                            # Don't add to result

                elif issue_type == "document_structure":
                    # For Document Structure issues
                    # Find "No headings in document" header
                    for text in text_elements:
                        text_content = text.window_text().lower()
                        if "no headings in document" in text_content:
                            result["issue_header"] = text
                            break

                    # Find "Review document navigation" button
                    for button in all_buttons:
                        button_name = button.window_text().lower()
                        if "review document navigation" in button_name:
                            result["review_document_navigation_button"] = button
                            break

                elif issue_type == "missing_alt_text":
                    # For Missing Alt Text issues
                    # Find "Missing alt text" header
                    for text in text_elements:
                        text_content = text.window_text().lower()
                        if "missing alt text" in text_content and text != issue_title:
                            result["issue_header"] = text
                            break

                    # Find "Generate Description" button
                    for button in all_buttons:
                        button_name = button.window_text().lower()
                        if "generate description" in button_name:
                            result["generate_description_button"] = button
                            break

                return result
            else:
                print("Accessibility Assistant control not found")
                return None
        else:
            print("MsoDockRight pane not found")
            return None

    def get_navigation_tab_subitems(self,navigation_dict, window):
        """
        Extract items from Word's Navigation pane based on which tab is selected.
        Handles both Headings tab and Pages tab.

        Args:
            navigation_dict: Dictionary containing navigation bar items
            window: The Word application window

        Returns:
            dict: Dictionary of navigation items (headings or pages)
        """
        result = {}
        index = 0

        # Determine which tab is selected
        selected_tab_name = None
        selected_tab = None

        for tab_name, tab_control in navigation_dict["tabs"].items():
            try:
                # Check if tab is selected using selection pattern
                selection_pattern = tab_control.get_selection_item_pattern()
                if selection_pattern and selection_pattern.CurrentIsSelected:
                    selected_tab = tab_control
                    selected_tab_name = tab_name
                    break
            except:
                try:
                    # Fallback to is_selected method
                    if tab_control.is_selected():
                        selected_tab = tab_control
                        selected_tab_name = tab_name
                        break
                except:
                    pass

        # If no tab is found selected via patterns, use visual cues
        if not selected_tab:
            # In Word's UI, the selected tab typically has a blue highlight/underline
            # We could check for this by examining tab names or other properties
            # For now, we'll check if "Pages" tab has focus indicators
            pages_tab = navigation_dict["tabs"].get("Pages")
            if pages_tab:
                try:
                    # Check if Pages tab has the IsSelected property set to True
                    # or any other focus indicator
                    if hasattr(pages_tab, "Focusable") and pages_tab.Focusable:
                        selected_tab = pages_tab
                        selected_tab_name = "Pages"
                except:
                    pass

        # Add the selected tab name as the first item
        if selected_tab:
            result[index] = selected_tab_name
            index += 1
        else:
            # If no tab is clearly selected, return empty result
            return result

        # Find the Navigation control
        navigation_controls = window.descendants(
            control_type="Custom",
            title="Navigation",
            depth=10
        )

        if not navigation_controls:
            print("Navigation control not found")
            return result

        navigation_control = navigation_controls[0]

        # Process based on which tab is selected
        if selected_tab_name == "Headings":
            # Get heading items when Headings tab is selected
            # Look for containers that might hold the headings
            heading_containers = []

            # Check for TreeView first (most common)
            tree_views = navigation_control.descendants(control_type="Tree", depth=5)
            if tree_views:
                heading_containers.extend(tree_views)

            # If no TreeView, check for other containers
            if not heading_containers:
                panes = navigation_control.descendants(control_type="Pane", depth=5)
                heading_containers.extend(panes)

            # Process each potential container
            for container in heading_containers:
                # Get all heading elements
                heading_elements = []

                # Try buttons first (common in Word's Navigation pane)
                buttons = container.descendants(control_type="Button", depth=15)
                if buttons:
                    heading_elements.extend(buttons)

                # Also check for tree items
                tree_items = container.descendants(control_type="TreeItem", depth=15)
                if tree_items:
                    heading_elements.extend(tree_items)

                # Process each heading element
                for element in heading_elements:
                    heading_text = element.window_text().strip()

                    # Skip empty headings or UI controls that aren't actual headings
                    if not heading_text or "111111" in heading_text:
                        continue

                    # Add to result with simple numbering
                    result[index] = element
                    index += 1

        elif selected_tab_name == "Pages":
            # For Pages tab, we need to look for the Document control that contains the pages
            # This is not under the Navigation control but is a separate element in the window

            # First, get the Word document name to help filter
            document_name = None
            try:
                # Try to get the document name from window title
                window_title = window.window_text()
                if " - Word" in window_title:
                    document_name = window_title.split(" - Word")[0].strip()
            except:
                pass

            # Find the Document control(s)
            print(f"doc name {document_name}")
            document_controls = window.descendants(control_type="Document", depth=10)

            if not document_controls:
                print("no fdoc control found")
                # If no Document controls found, try looking for a control with the document name
                if document_name:
                    potential_docs = window.descendants(title=document_name, depth=10)
                    if potential_docs:
                        document_controls = potential_docs

            if document_controls:
                print("doc control found")
                # Now look for page elements in the document
                for doc in document_controls:
                    # First try to find specific "page" elements
                    page_elements = doc.descendants(control_type="page", depth=5)

                    if not page_elements:
                        # If that doesn't work, look for text or elements containing "Page"
                        page_elements = []

                        # Check for elements with "Page" in their title/text
                        potential_pages = doc.descendants(depth=15)
                        for element in potential_pages:
                            try:
                                text = element.window_text().strip()
                                if text.startswith("page 'Page") or (
                                        text.startswith("Page ") and any(char.isdigit() for char in text)):
                                    page_elements.append(element)
                            except:
                                pass

                    # Process found page elements
                    for element in page_elements:
                        element_text = element.window_text().strip()
                        if element_text:
                            result[index] = element
                            index += 1
            else:
                # Alternative approach: directly search for page elements in the window
                # Look specifically for elements with text matching page patterns
                all_elements = window.descendants(depth=20)
                page_elements = []

                for element in all_elements:
                    try:
                        print("tryiong something else....")
                        text = element.window_text().strip()
                        # Look for patterns like "page 'Page 1'" or "Page 1"
                        if (text.startswith("page 'Page") or
                                (text.startswith("Page ") and any(char.isdigit() for char in text))):
                            page_elements.append(element)
                    except:
                        pass

                # Process found page elements
                for element in page_elements:
                    element_text = element.window_text().strip()
                    if element_text:
                        result[index] = element
                        index += 1
        print("API RESULTL:",result)
        return result


    def get_text_prediction_options(self, window):
        """
        Find and interact with text prediction options in Word Options dialog
        Returns a dict with the actual checkbox control objects
        """
        # Find the Word Options dialog window
        word_options_dialog = window.descendants(
            title="Word Options",
            control_type="Window",
            depth=3
        )

        if not word_options_dialog:
            print("Word Options dialog not found")
            return None

        dialog = word_options_dialog[0]

        # Find the specific checkboxes
        auto_complete_checkboxes = dialog.descendants(
            title="Show AutoComplete suggestions",
            control_type="CheckBox",
            depth=10
        )

        text_predictions_checkboxes = dialog.descendants(
            title="Show text predictions while typing",
            control_type="CheckBox",
            depth=10
        )

        if not auto_complete_checkboxes and not text_predictions_checkboxes:
            return None

        # Create result with direct checkbox objects
        result = {
                "autocomplete": auto_complete_checkboxes[0] if auto_complete_checkboxes else None,
                "text_predictions": text_predictions_checkboxes[0] if text_predictions_checkboxes else None
            }


        # # Add tooltip element if visible
        # tooltip_text = dialog.descendants(
        #     title="Turn off this option to stop text predictions.",
        #     control_type="Text"
        # )
        #
        # if tooltip_text:
        #     result["tooltip"] = tooltip_text[0]

        return result

    def perform_click(self,button):
        control_receiver = ControlReceiver(control=button,application=self.app_window)
        params = {"button": "left", "double": False}
        control_receiver.atomic_execution("click",params)

    def invoke_button(self, button):
        print(f"Button pressed: {button.window_text()}")
        try:
            button.invoke()
        except:
            button.toggle()

    def slider_set(self, slider):
        print(f"{slider [0]} setting to value {slider [1]}")
        slider[0].set_value(slider[1]/10*slider[0].max_value())

    def get_ribbon_font_controls(self, window):
        """
                Find font-related controls in the Word ribbon Font group with minimal UIA calls.
                Returns the actual UIA control elements with numeric indices.

                Args:
                    window: The Word application window object

                Returns:
                    Dictionary of UIA control elements indexed by position where:
                    0: Font Name dropdown
                    1: Font Size dropdown
                    2: Grow Font
                    3: Shrink Font
                    4: Clear Formatting
                    5: Bold
                    6: Italic
                    7: Underline
                    8: Strikethrough
                    9: Subscript
                    10: Superscript

                    Returns None if controls cannot be found
        """
        def close_interfering_panes(window):
            """Close all panes that might interfere with ribbon access"""
            print("Checking for interfering panes...")

            # Comprehensive list of panes that could interfere
            interfering_panes = [
                # Direct matches
                {"type": "exact", "name": "Accessibility Assistant"},
                {"type": "exact", "name": "Editor"},
                {"type": "exact", "name": "Navigation"},

                # Partial matches
                {"type": "partial", "name": "MsoDockRight"},
                {"type": "partial", "name": "MsoDockLeft"},
                {"type": "partial", "name": "MsoDockBottom"},
            ]

            # Get all panes in a single query for efficiency
            try:
                all_panes = window.descendants(control_type="Pane", depth=10)
                print(f"Found {len(all_panes)} panes to check")
            except Exception as e:
                print(f"Error retrieving panes: {e}")
                all_panes = []

            # Process the panes in memory
            for pane in all_panes:
                try:
                    pane_text = pane.window_text()
                    should_close = False
                    matched_name = ""

                    # Check if this is a pane we want to close
                    for interfering_pane in interfering_panes:
                        if (interfering_pane["type"] == "exact" and pane_text == interfering_pane["name"]) or \
                                (interfering_pane["type"] == "partial" and interfering_pane["name"] in pane_text):
                            should_close = True
                            matched_name = interfering_pane["name"]
                            break

                    if should_close:
                        print(f"Attempting to close: {matched_name}")
                        try:
                            # Try different methods to close the pane
                            # 1. Look for a "Close pane" button
                            close_pane_buttons = pane.descendants(control_type="Button", title="Close pane", depth=4)
                            if close_pane_buttons:
                                print(f"Clicking 'Close pane' button for {matched_name}")
                                close_pane_buttons[0].click()
                                import time
                                time.sleep(0.1)
                                continue

                            # 2. Look for buttons with "Close" or "X" in the text
                            close_buttons = pane.descendants(control_type="Button", depth=4)
                            close_found = False
                            for button in close_buttons:
                                button_text = button.window_text().strip()
                                if button_text in ["X", "×", "Close", ""]:
                                    print(f"Clicking '{button_text}' button for {matched_name}")
                                    button.click()
                                    close_found = True
                                    import time
                                    time.sleep(0.1)
                                    break

                            if close_found:
                                continue

                            # 3. Try to find the last button in the title bar (usually the close button)
                            title_bars = pane.children(control_type="TitleBar")
                            if title_bars:
                                buttons = title_bars[0].children(control_type="Button")
                                if buttons:
                                    print(f"Clicking title bar close button for {matched_name}")
                                    buttons[-1].click()
                                    import time
                                    time.sleep(0.1)
                                    continue

                            # We don't use keyboard shortcuts as requested
                        except Exception as e:
                            print(f"Error closing pane {matched_name}: {e}")
                            continue  # Continue to next pane if this one fails
                except Exception as e:
                    print(f"Error processing pane: {e}")
                    continue

        def activate_ribbon_and_find_font_group(window):
            """Use UIA to find and activate the ribbon Home tab and locate the Font group"""
            import time
            font_group = None

            # Step 1: First check if ribbon is already visible and Home tab is active
            print("Checking if ribbon is already visible...")

            # Try to find the ribbon directly first
            ribbon_panes = None
            try:
                ribbon_panes = window.descendants(control_type="Pane", title="Ribbon", depth=5)
                if ribbon_panes:
                    print("Ribbon found")
            except Exception as e:
                print(f"Error finding ribbon: {e}")

            # Step 2: If ribbon not found or not visible, try to find the ribbon display toggle
            if not ribbon_panes:
                try:
                    # Look for ribbon display options or toggle buttons
                    ribbon_buttons = window.descendants(control_type="Button", depth=5)
                    for button in ribbon_buttons:
                        button_text = button.window_text().lower()
                        if "ribbon" in button_text and ("display" in button_text or "show" in button_text):
                            print("Clicking ribbon display button")
                            button.click()
                            time.sleep(0.2)
                            break

                    # Try to find ribbon again after toggle
                    ribbon_panes = window.descendants(control_type="Pane", title="Ribbon", depth=5)
                except Exception as e:
                    print(f"Error toggling ribbon display: {e}")

            # Step 3: Try to find and activate Home tab
            print("Looking for Home tab...")
            try:
                # First look for all tabs in one query
                tab_items = window.descendants(control_type="TabItem", depth=8)
                home_tab = None

                # Filter in memory for Home tab
                for tab in tab_items:
                    tab_text = tab.window_text().lower()
                    if "home" in tab_text:
                        home_tab = tab
                        break

                # If found, click it
                if home_tab:
                    print("Found Home tab, clicking to activate")
                    home_tab.click()
                    time.sleep(0.2)
                else:
                    print("Home tab not found")
            except Exception as e:
                print(f"Error finding/activating Home tab: {e}")

            # Step 4: Look for Font group with different strategies
            print("Searching for Font group...")

            # Strategy 1: Direct path from ribbon if we found it
            if ribbon_panes:
                try:
                    # Find Lower Ribbon pane
                    lower_ribbons = ribbon_panes[0].descendants(control_type="Pane", title="Lower Ribbon", depth=2)
                    if lower_ribbons:
                        # Direct search for Font group
                        font_groups = lower_ribbons[0].descendants(control_type="Group", title="Font", depth=2)
                        if font_groups:
                            print("Found Font group through direct ribbon path")
                            font_group = font_groups[0]
                except Exception as e:
                    print(f"Error in strategy 1: {e}")

            # Strategy 2: Efficient broad search if direct path failed
            if not font_group:
                try:
                    # Get all groups in one query
                    all_groups = window.descendants(control_type="Group", depth=12)
                    print(f"Found {len(all_groups)} total groups to check")

                    # Filter in memory - much faster than multiple UIA calls
                    for group in all_groups:
                        group_text = group.window_text()
                        if "Font" in group_text:
                            print(f"Found Font group through broad search: '{group_text}'")
                            font_group = group
                            break
                except Exception as e:
                    print(f"Error in strategy 2: {e}")

            return font_group

        self.app_window = window
        self.app_window.set_focus()

        # Close interfering panes first
        close_interfering_panes(window)

        # Find and activate the ribbon
        print("Looking for ribbon...")
        font_group = activate_ribbon_and_find_font_group(window)

        # If we still can't find the Font group
        if not font_group:
            print("Font group not found after all attempts")
            return None

        print("Font group found - extracting controls")
        # Get ALL controls from the Font group in a SINGLE query
        all_controls = []
        try:
            # Get all needed controls in one go - much faster than multiple queries
            all_controls = font_group.descendants(depth=3)
        except Exception as e:
            print(f"Error getting font group controls: {e}")
            try:
                # Fallback with explicit control types if needed
                for control_type in ["Button", "ComboBox", "SplitButton"]:
                    controls = font_group.descendants(control_type=control_type, depth=3)
                    all_controls.extend(controls)
            except Exception as e:
                print(f"Error in fallback method: {e}")
                pass

        if not all_controls:
            print("No controls found in font group")
            return None

        # Process everything in memory - no more UIA calls
        combo_boxes = []
        buttons = []
        split_buttons = []

        # Sort controls by type (in memory)
        for control in all_controls:
            try:
                control_type = control.element_info.control_type
                if control_type == "ComboBox":
                    combo_boxes.append(control)
                elif control_type == "Button":
                    buttons.append(control)
                elif control_type == "SplitButton":
                    split_buttons.append(control)
            except:
                pass

        # Create the final dict with exactly the controls we want, in the right order
        result_dict = {}

        # 1. FONT COMBOBOX - index 0
        for combo in combo_boxes:
            try:
                text = combo.window_text().strip()
                # Font combo might have current font name or empty text
                if not text or ("font" in text.lower() and "size" not in text.lower()):
                    result_dict[0] = combo  # Store the actual UIA element
                    break
            except:
                pass

        if 0 not in result_dict and combo_boxes:
            # Just take the first combo box if we can't specifically identify the font one
            result_dict[0] = combo_boxes[0]

        # 2. FONT SIZE - store at index 1 as requested
        for combo in combo_boxes:
            try:
                text = combo.window_text().strip()
                if "size" in text.lower() or any(c.isdigit() for c in text):
                    # Store the actual UIA element
                    result_dict[1] = combo
                    break
            except:
                pass

        # Rest of the controls in order
        control_indices = {
            "Grow Font": 2,
            "Shrink Font": 3,
            "Clear Formatting": 4,
            "Bold": 5,
            "Italic": 6,
            "Underline": 7,
            "Strikethrough": 8,
            "Subscript": 9,
            "Superscript": 10
        }

        # Find specific buttons by name
        for button in buttons:
            try:
                text = button.window_text().strip()
                for control_name, index in control_indices.items():
                    if control_name.lower() in text.lower():
                        # Store the actual UIA element
                        result_dict[index] = button
                        break
            except:
                pass

        # Handle special case for Underline which might be a SplitButton
        if 7 not in result_dict:
            for split in split_buttons:
                try:
                    if "underline" in split.window_text().lower():
                        result_dict[7] = split  # Store the actual UIA element
                        break
                except:
                    pass

        # Check if we found enough controls to consider this successful
        if len(result_dict) < 5:  # Need at least font, bold, italic, etc.
            print(f"Not enough controls found in font group, only found {len(result_dict)}")
            return None

        print(f"Successfully found {len(result_dict)} font controls")
        return result_dict


