//! Core Windows UI Automation initialization and utilities

use crate::error::{Result, ScreenBridgeError};
use windows::Win32::System::Com::{
    CoCreateInstance, CoInitializeEx, CoUninitialize, CLSCTX_INPROC_SERVER,
    COINIT_APARTMENTTHREADED, COINIT_DISABLE_OLE1DDE,
};
use windows::Win32::UI::Accessibility::{CUIAutomation, IUIAutomation};

/// UI Automation context manager
/// Handles COM initialization and IUIAutomation instance
pub struct AutomationContext {
    /// The UI Automation instance
    automation: IUIAutomation,
    /// Whether this context initialized COM
    owns_com: bool,
}

impl AutomationContext {
    /// Initialize UI Automation context
    ///
    /// This will:
    /// 1. Initialize COM if not already initialized
    /// 2. Create the IUIAutomation instance
    pub fn new() -> Result<Self> {
        // Try to initialize COM
        // If already initialized by another component, that's okay
        let owns_com = unsafe {
            let hr = CoInitializeEx(
                None,
                COINIT_APARTMENTTHREADED | COINIT_DISABLE_OLE1DDE,
            );
            // S_OK (0) or S_FALSE (1) are both success
            if hr.is_ok() || hr.0 == 0x00000001 {
                hr.is_ok() // Only own COM if we actually initialized it (S_OK)
            } else {
                return Err(ScreenBridgeError::ComError(format!(
                    "Failed to initialize COM: HRESULT {:x}",
                    hr.0
                )));
            }
        };

        // Create IUIAutomation instance using CoCreateInstance
        let automation: IUIAutomation = unsafe {
            CoCreateInstance(&CUIAutomation, None, CLSCTX_INPROC_SERVER).map_err(|e| {
                ScreenBridgeError::InitializationError(format!(
                    "Failed to create IUIAutomation: {}",
                    e
                ))
            })?
        };

        Ok(Self {
            automation,
            owns_com,
        })
    }

    /// Get the IUIAutomation instance
    pub fn automation(&self) -> &IUIAutomation {
        &self.automation
    }

    /// Get the root element (desktop)
    pub fn get_root_element(&self) -> Result<windows::Win32::UI::Accessibility::IUIAutomationElement> {
        unsafe {
            self.automation.GetRootElement().map_err(|e| {
                ScreenBridgeError::InitializationError(format!("Failed to get root element: {}", e))
            })
        }
    }
}

impl Drop for AutomationContext {
    fn drop(&mut self) {
        // Only uninitialize COM if we initialized it
        if self.owns_com {
            unsafe {
                CoUninitialize();
            }
        }
    }
}

// Thread safety: UI Automation should be used from the same thread
// COM apartment threading requires operations on the same thread
// Note: These types contain raw COM pointers that aren't thread-safe
// Users should ensure AutomationContext stays on one thread

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_automation_context_creation() {
        let context = AutomationContext::new();
        assert!(context.is_ok());
    }

    #[test]
    fn test_get_root_element() {
        let context = AutomationContext::new().unwrap();
        let root = context.get_root_element();
        assert!(root.is_ok());
    }
}
