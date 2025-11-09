//! Error types for ScreenBridge operations

use thiserror::Error;

/// Result type for ScreenBridge operations
pub type Result<T> = std::result::Result<T, ScreenBridgeError>;

/// Errors that can occur during UI automation operations
#[derive(Error, Debug)]
pub enum ScreenBridgeError {
    /// Failed to initialize Windows UI Automation
    #[error("Failed to initialize UI Automation: {0}")]
    InitializationError(String),

    /// Window not found or invalid
    #[error("Window not found or invalid: {0}")]
    WindowNotFound(String),

    /// UI element not found
    #[error("UI element not found: {0}")]
    ElementNotFound(String),

    /// UI element is no longer valid (stale reference)
    #[error("UI element is stale or no longer accessible: {0}")]
    StaleElement(String),

    /// Operation not supported on this element
    #[error("Operation not supported: {0}")]
    UnsupportedOperation(String),

    /// Windows API error
    #[error("Windows API error: {0}")]
    WindowsError(#[from] windows::core::Error),

    /// COM initialization error
    #[error("COM initialization error: {0}")]
    ComError(String),

    /// Element property access error
    #[error("Failed to access element property: {0}")]
    PropertyError(String),

    /// Pattern not supported by element
    #[error("UI Automation pattern not supported: {0}")]
    PatternNotSupported(String),

    /// Timeout waiting for element or condition
    #[error("Operation timed out: {0}")]
    Timeout(String),

    /// Invalid argument provided
    #[error("Invalid argument: {0}")]
    InvalidArgument(String),

    /// Generic automation error
    #[error("Automation error: {0}")]
    AutomationError(String),
}

/// Convert Windows HRESULT errors to ScreenBridgeError
impl From<i32> for ScreenBridgeError {
    fn from(hr: i32) -> Self {
        ScreenBridgeError::WindowsError(windows::core::Error::from_hresult(
            windows::core::HRESULT(hr),
        ))
    }
}
