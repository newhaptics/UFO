//! # ScreenBridge Core
//!
//! Rust library for Microsoft Word UI automation via Windows UI Automation.
//!
//! ## Overview
//!
//! ScreenBridge provides programmatic access to Microsoft Word UI elements that aren't
//! accessible through Word's COM API, including:
//!
//! - Status bars and navigation panes
//! - Accessibility checker
//! - Grammar and spelling tools
//! - Ribbon controls
//! - Language settings
//! - Text prediction options
//!
//! ## Example
//!
//! ```no_run
//! use screenbridge_core::WordAutomation;
//!
//! fn main() -> Result<(), Box<dyn std::error::Error>> {
//!     let word = WordAutomation::new()?;
//!
//!     // Find all Word windows
//!     let windows = word.find_windows()?;
//!
//!     // Get status bar items
//!     let status_bar = word.get_status_bar_items(&windows[0])?;
//!     println!("Page number: {:?}", status_bar.page_number);
//!
//!     Ok(())
//! }
//! ```
//!
//! ## Architecture
//!
//! The library is organized into several modules:
//!
//! - `automation`: Core UI Automation initialization
//! - `elements`: Type-safe UI element wrappers
//! - `window`: Window management and discovery
//! - `status_bar`: Status bar extraction
//! - `navigation`: Navigation pane access
//! - `accessibility`: Accessibility checker integration
//! - `grammar`: Grammar and spelling tools
//! - `ribbon`: Ribbon control access
//!

#![cfg(windows)]
#![warn(missing_docs)]

// Public modules
pub mod error;
pub mod elements;
pub mod automation;
mod window;

// Re-exports
pub use error::{Result, ScreenBridgeError};
pub use elements::*;
pub use automation::AutomationContext;

/// Main API for Word UI automation
pub struct WordAutomation {
    context: AutomationContext,
}

impl WordAutomation {
    /// Create a new WordAutomation instance
    ///
    /// This initializes the UI Automation context.
    pub fn new() -> Result<Self> {
        let context = AutomationContext::new()?;
        Ok(Self { context })
    }

    /// Get a reference to the underlying automation context
    ///
    /// This is useful for advanced scenarios where you need direct access
    /// to the UI Automation API.
    pub fn context(&self) -> &AutomationContext {
        &self.context
    }

    /// Find all Microsoft Word windows
    ///
    /// Returns a list of window handles for all open Word windows.
    /// Optionally filters out dialog windows.
    pub fn find_windows(&self) -> Result<Vec<WindowHandle>> {
        window::find_word_windows(&self.context)
    }

    /// Get status bar items from a Word window
    ///
    /// Extracts all status bar elements including page number, language,
    /// zoom controls, and other buttons.
    pub fn get_status_bar_items(&self, _window: &WindowHandle) -> Result<StatusBarItems> {
        // TODO: Implement status bar extraction
        todo!("Implement status bar extraction")
    }

    /// Get navigation pane items from a Word window
    ///
    /// Accesses the navigation pane with search box and tabs.
    pub fn get_navigation_pane(&self, _window: &WindowHandle) -> Result<NavigationPane> {
        // TODO: Implement navigation pane access
        todo!("Implement navigation pane access")
    }

    /// Get accessibility checker items from a Word window
    ///
    /// Accesses the Accessibility Assistant pane with issue categories.
    pub fn get_accessibility_items(&self, _window: &WindowHandle) -> Result<AccessibilityItems> {
        // TODO: Implement accessibility checker access
        todo!("Implement accessibility checker access")
    }

    /// Get grammar check items from a Word window
    ///
    /// Accesses the Editor pane with spelling/grammar suggestions.
    pub fn get_grammar_check_items(&self, _window: &WindowHandle) -> Result<GrammarCheckItems> {
        // TODO: Implement grammar check access
        todo!("Implement grammar check access")
    }

    /// Get font controls from the ribbon
    ///
    /// Accesses font-related controls in the Home tab ribbon.
    pub fn get_font_controls(&self, _window: &WindowHandle) -> Result<FontControls> {
        // TODO: Implement ribbon font controls access
        todo!("Implement ribbon font controls access")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_word_automation_creation() {
        let word = WordAutomation::new();
        assert!(word.is_ok());
    }
}
