//! Generic window discovery - works with any Windows application
//!
//! This module provides a generic API for discovering and filtering windows
//! from any application, not just Microsoft Word.

use crate::automation::AutomationContext;
use crate::elements::{UIElement, WindowHandle};
use crate::error::{Result, ScreenBridgeError};
use windows::Win32::Foundation::{CloseHandle, MAX_PATH};
use windows::Win32::System::ProcessStatus::K32GetModuleFileNameExW;
use windows::Win32::System::Threading::{OpenProcess, PROCESS_QUERY_INFORMATION};
use windows::Win32::UI::Accessibility::{
    IUIAutomation, IUIAutomationCondition, IUIAutomationElement, UIA_ControlTypePropertyId,
    UIA_PaneControlTypeId, UIA_WindowControlTypeId,
};

/// Criteria for filtering windows
#[derive(Debug, Clone)]
pub struct WindowFilter {
    /// Filter by process name (e.g., "winword.exe", "excel.exe")
    pub process_name: Option<String>,
    /// Filter by window title (substring match)
    pub title_contains: Option<String>,
    /// Exclude windows with these titles
    pub exclude_titles: Vec<String>,
    /// Only include main windows (exclude dialogs)
    pub main_windows_only: bool,
    /// Only include visible windows (not offscreen)
    pub visible_only: bool,
    /// Only include keyboard focusable windows
    pub focusable_only: bool,
}

impl Default for WindowFilter {
    fn default() -> Self {
        Self {
            process_name: None,
            title_contains: None,
            exclude_titles: Vec::new(),
            main_windows_only: false,
            visible_only: false,
            focusable_only: false,
        }
    }
}

impl WindowFilter {
    /// Create a new filter for a specific process
    pub fn for_process(process_name: impl Into<String>) -> Self {
        Self {
            process_name: Some(process_name.into()),
            ..Default::default()
        }
    }

    /// Create a filter for main windows only (exclude dialogs)
    pub fn main_windows() -> Self {
        Self {
            main_windows_only: true,
            ..Default::default()
        }
    }

    /// Add a title filter (substring match)
    pub fn with_title(mut self, title: impl Into<String>) -> Self {
        self.title_contains = Some(title.into());
        self
    }

    /// Exclude windows with specific titles
    pub fn excluding_titles(mut self, titles: Vec<String>) -> Self {
        self.exclude_titles = titles;
        self
    }

    /// Only show main windows (exclude dialogs)
    pub fn only_main_windows(mut self) -> Self {
        self.main_windows_only = true;
        self
    }

    /// Only show visible windows (not offscreen)
    pub fn only_visible(mut self) -> Self {
        self.visible_only = true;
        self
    }

    /// Only show keyboard focusable windows
    pub fn only_focusable(mut self) -> Self {
        self.focusable_only = true;
        self
    }
}

/// Generic window discovery service
pub struct WindowDiscovery<'a> {
    context: &'a AutomationContext,
}

impl<'a> WindowDiscovery<'a> {
    /// Create a new WindowDiscovery instance
    pub fn new(context: &'a AutomationContext) -> Self {
        Self { context }
    }

    /// Find all windows on the desktop
    ///
    /// Returns all top-level windows, regardless of application.
    pub fn find_all_windows(&self) -> Result<Vec<WindowHandle>> {
        self.find_windows_with_filter(&WindowFilter::default())
    }

    /// Find windows matching specific criteria
    ///
    /// # Example
    /// ```no_run
    /// # use screenbridge_core::*;
    /// # fn example(context: &AutomationContext) -> Result<()> {
    /// let discovery = WindowDiscovery::new(context);
    ///
    /// // Find all Word windows
    /// let filter = WindowFilter::for_process("winword.exe");
    /// let word_windows = discovery.find_windows_with_filter(&filter)?;
    ///
    /// // Find all Excel windows
    /// let filter = WindowFilter::for_process("excel.exe");
    /// let excel_windows = discovery.find_windows_with_filter(&filter)?;
    /// # Ok(())
    /// # }
    /// ```
    pub fn find_windows_with_filter(&self, filter: &WindowFilter) -> Result<Vec<WindowHandle>> {
        let automation = self.context.automation();
        let root = self.context.get_root_element()?;

        // Create condition to find all Window elements
        let window_condition = create_window_condition(automation)?;

        // Find all windows
        let windows = unsafe {
            root.FindAll(
                windows::Win32::UI::Accessibility::TreeScope_Children,
                &window_condition,
            )
            .map_err(|e| {
                ScreenBridgeError::AutomationError(format!("Failed to find windows: {}", e))
            })?
        };

        let mut matched_windows = Vec::new();
        let count = unsafe { windows.Length() }.unwrap_or(0);

        for i in 0..count {
            let element = unsafe {
                windows.GetElement(i).map_err(|e| {
                    ScreenBridgeError::ElementNotFound(format!(
                        "Failed to get window at index {}: {}",
                        i, e
                    ))
                })?
            };

            // Try to convert to WindowHandle and apply filter
            if let Ok(Some(handle)) = element_to_window_handle(&element, filter) {
                matched_windows.push(handle);
            }
        }

        Ok(matched_windows)
    }

    /// Find windows by process name
    ///
    /// Convenience method for finding windows of a specific application.
    ///
    /// # Example
    /// ```no_run
    /// # use screenbridge_core::*;
    /// # fn example(context: &AutomationContext) -> Result<()> {
    /// let discovery = WindowDiscovery::new(context);
    /// let word_windows = discovery.find_by_process("winword.exe")?;
    /// let excel_windows = discovery.find_by_process("excel.exe")?;
    /// let chrome_windows = discovery.find_by_process("chrome.exe")?;
    /// # Ok(())
    /// # }
    /// ```
    pub fn find_by_process(&self, process_name: &str) -> Result<Vec<WindowHandle>> {
        let filter = WindowFilter::for_process(process_name);
        self.find_windows_with_filter(&filter)
    }

    /// Find windows by title (substring match)
    pub fn find_by_title(&self, title: &str) -> Result<Vec<WindowHandle>> {
        let filter = WindowFilter::default().with_title(title);
        self.find_windows_with_filter(&filter)
    }
}

/// Create a condition to find Window AND Pane control types
///
/// We search for both because some applications (like Electron apps: Slack, VS Code)
/// expose themselves as "pane" instead of "window" type.
fn create_window_condition(automation: &IUIAutomation) -> Result<IUIAutomationCondition> {
    unsafe {
        // Create condition for "window" type
        let window_type = windows::core::VARIANT::from(UIA_WindowControlTypeId.0 as i32);
        let window_condition = automation
            .CreatePropertyCondition(UIA_ControlTypePropertyId, &window_type)
            .map_err(|e| {
                ScreenBridgeError::AutomationError(format!(
                    "Failed to create window condition: {}",
                    e
                ))
            })?;

        // Create condition for "pane" type
        let pane_type = windows::core::VARIANT::from(UIA_PaneControlTypeId.0 as i32);
        let pane_condition = automation
            .CreatePropertyCondition(UIA_ControlTypePropertyId, &pane_type)
            .map_err(|e| {
                ScreenBridgeError::AutomationError(format!(
                    "Failed to create pane condition: {}",
                    e
                ))
            })?;

        // Combine with OR - match either window OR pane
        automation
            .CreateOrCondition(&window_condition, &pane_condition)
            .map_err(|e| {
                ScreenBridgeError::AutomationError(format!(
                    "Failed to create OR condition: {}",
                    e
                ))
            })
    }
}

/// Convert a UI element to WindowHandle if it matches the filter
fn element_to_window_handle(
    element: &IUIAutomationElement,
    filter: &WindowFilter,
) -> Result<Option<WindowHandle>> {
    // Get process ID
    let process_id = unsafe {
        element.CurrentProcessId().map_err(|e| {
            ScreenBridgeError::PropertyError(format!("Failed to get process ID: {}", e))
        })?
    };

    // Get window name/title
    let title = unsafe {
        element
            .CurrentName()
            .map(|bstr| bstr.to_string())
            .unwrap_or_default()
    };

    // Create UIElement wrapper for property queries
    let ui_element = UIElement::new(element.clone());

    // Apply visibility filter (if requested)
    if filter.visible_only {
        if let Ok(visible) = ui_element.is_visible() {
            if !visible {
                return Ok(None);
            }
        }
    }

    // Apply focusable filter (if requested)
    if filter.focusable_only {
        if let Ok(focusable) = ui_element.is_keyboard_focusable() {
            if !focusable {
                return Ok(None);
            }
        }
    }

    // Apply process name filter
    if let Some(ref process_name) = filter.process_name {
        if !matches_process(process_id, process_name) {
            return Ok(None);
        }
    }

    // Apply title filter
    if let Some(ref title_filter) = filter.title_contains {
        if !title.contains(title_filter) {
            return Ok(None);
        }
    }

    // Apply title exclusion filter
    for excluded in &filter.exclude_titles {
        if title.contains(excluded) {
            return Ok(None);
        }
    }

    // Apply main windows filter
    if filter.main_windows_only && is_dialog_window(&title) {
        return Ok(None);
    }

    // All filters passed, create WindowHandle
    Ok(Some(WindowHandle::new(ui_element, title, process_id)))
}

/// Check if a process ID corresponds to a specific process name
fn matches_process(process_id: i32, target_process_name: &str) -> bool {
    if process_id < 0 {
        return false;
    }
    let process_id = process_id as u32;

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
        let lowercase_path = path.to_lowercase();
        let lowercase_target = target_process_name.to_lowercase();

        // Match either the full path or just the executable name
        lowercase_path.contains(&lowercase_target)
            || lowercase_path.ends_with(&format!("\\{}", lowercase_target))
    }
}

/// Check if a window title suggests it's a dialog rather than main window
fn is_dialog_window(title: &str) -> bool {
    // Empty titles are often dialogs
    if title.is_empty() {
        return true;
    }

    // Common dialog keywords
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
        "Properties",
    ];

    dialog_keywords
        .iter()
        .any(|&keyword| title.contains(keyword))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_window_filter_builder() {
        let filter = WindowFilter::for_process("winword.exe")
            .with_title("Document")
            .only_main_windows();

        assert_eq!(filter.process_name, Some("winword.exe".to_string()));
        assert_eq!(filter.title_contains, Some("Document".to_string()));
        assert!(filter.main_windows_only);
    }

    #[test]
    fn test_is_dialog_window() {
        assert!(is_dialog_window(""));
        assert!(is_dialog_window("Word Options"));
        assert!(is_dialog_window("Print"));
        assert!(!is_dialog_window("Document1 - Word"));
        assert!(!is_dialog_window("My Document.docx - Word"));
    }
}
