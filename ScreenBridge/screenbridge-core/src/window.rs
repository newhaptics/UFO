//! Window management and discovery

use crate::automation::AutomationContext;
use crate::elements::{UIElement, WindowHandle};
use crate::error::{Result, ScreenBridgeError};
use windows::Win32::UI::Accessibility::{
    IUIAutomation, IUIAutomationCondition, IUIAutomationElement, UIA_ControlTypePropertyId,
    UIA_WindowControlTypeId,
};

/// Find all Microsoft Word windows
///
/// This function:
/// 1. Searches for all Window control type elements
/// 2. Filters for winword.exe process
/// 3. Identifies main document windows vs dialogs
/// 4. Returns handles for all valid Word windows
pub fn find_word_windows(context: &AutomationContext) -> Result<Vec<WindowHandle>> {
    let automation = context.automation();
    let root = context.get_root_element()?;

    // Create condition to find all Window elements
    let window_condition = create_window_condition(automation)?;

    // Find all windows
    let windows = unsafe {
        root.FindAll(
            windows::Win32::UI::Accessibility::TreeScope_Children,
            &window_condition,
        )
        .map_err(|e| ScreenBridgeError::AutomationError(format!("Failed to find windows: {}", e)))?
    };

    let mut word_windows = Vec::new();
    let count = unsafe { windows.Length() }.unwrap_or(0);

    for i in 0..count {
        let element = unsafe {
            windows.GetElement(i).map_err(|e| {
                ScreenBridgeError::ElementNotFound(format!("Failed to get window at index {}: {}", i, e))
            })?
        };

        // Check if this is a Word window
        if let Ok(Some(handle)) = is_word_window(&element) {
            word_windows.push(handle);
        }
    }

    if word_windows.is_empty() {
        return Err(ScreenBridgeError::WindowNotFound(
            "No Word windows found".to_string(),
        ));
    }

    Ok(word_windows)
}

/// Create a condition to find Window control types
fn create_window_condition(automation: &IUIAutomation) -> Result<IUIAutomationCondition> {
    unsafe {
        let window_type = windows::core::VARIANT::from(UIA_WindowControlTypeId.0 as i32);
        automation
            .CreatePropertyCondition(UIA_ControlTypePropertyId, &window_type)
            .map_err(|e| {
                ScreenBridgeError::AutomationError(format!(
                    "Failed to create window condition: {}",
                    e
                ))
            })
    }
}

/// Check if an element is a Word window and return WindowHandle if valid
fn is_word_window(element: &IUIAutomationElement) -> Result<Option<WindowHandle>> {
    // Get process ID
    let process_id = unsafe {
        element.CurrentProcessId().map_err(|e| {
            ScreenBridgeError::PropertyError(format!("Failed to get process ID: {}", e))
        })?
    };

    // Check if it's winword.exe
    if !is_word_process(process_id) {
        return Ok(None);
    }

    // Get window name/title
    let title = unsafe {
        element
            .CurrentName()
            .map(|bstr| bstr.to_string())
            .unwrap_or_default()
    };

    // Filter out certain dialog windows
    // Word main windows typically have " - Word" in the title
    // or are document windows with specific characteristics
    if is_dialog_window(&title) {
        return Ok(None);
    }

    let ui_element = UIElement::new(element.clone());
    Ok(Some(WindowHandle::new(ui_element, title, process_id)))
}

/// Check if a process ID corresponds to winword.exe
fn is_word_process(process_id: i32) -> bool {
    if process_id < 0 {
        return false;
    }
    let process_id = process_id as u32;
    use windows::Win32::System::Threading::{OpenProcess, PROCESS_QUERY_INFORMATION};
    use windows::Win32::System::ProcessStatus::K32GetModuleFileNameExW;
    use windows::Win32::Foundation::{CloseHandle, MAX_PATH};

    unsafe {
        let handle = match OpenProcess(PROCESS_QUERY_INFORMATION, false, process_id) {
            Ok(h) => h,
            Err(_) => return false,
        };

        let mut filename = [0u16; MAX_PATH as usize];
        let len = K32GetModuleFileNameExW(handle, None, &mut filename);

        let _ = CloseHandle(handle);

        if len == 0 {
            return false;
        }

        let path = String::from_utf16_lossy(&filename[..len as usize]);
        path.to_lowercase().contains("winword.exe")
    }
}

/// Check if a window title suggests it's a dialog rather than main window
fn is_dialog_window(title: &str) -> bool {
    // Empty titles are often dialogs
    if title.is_empty() {
        return true;
    }

    // Common dialog titles to exclude
    let dialog_keywords = [
        "Options",
        "Preferences",
        "Settings",
        "Print",
        "Save As",
        "Open",
        "Find and Replace",
        "Font",
        "Paragraph",
    ];

    dialog_keywords.iter().any(|&keyword| title.contains(keyword))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_dialog_window() {
        assert!(is_dialog_window(""));
        assert!(is_dialog_window("Word Options"));
        assert!(is_dialog_window("Print"));
        assert!(!is_dialog_window("Document1 - Word"));
        assert!(!is_dialog_window("My Document.docx - Word"));
    }

    #[test]
    #[ignore] // Requires Word to be running
    fn test_find_word_windows() {
        let context = AutomationContext::new().unwrap();
        let windows = find_word_windows(&context);
        // This test will fail if Word is not running
        // In CI/CD, we'd skip this or mock it
        println!("Found windows: {:?}", windows);
    }
}
