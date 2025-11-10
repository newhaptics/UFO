//! UI element types and wrappers

use crate::error::{Result, ScreenBridgeError};
use serde::{Deserialize, Serialize};
use windows::Win32::UI::Accessibility::IUIAutomationElement;

/// Wrapper around Windows UI Automation element
#[derive(Clone)]
pub struct UIElement {
    /// The underlying UI Automation element
    element: IUIAutomationElement,
}

impl UIElement {
    /// Create a new UIElement wrapper
    pub fn new(element: IUIAutomationElement) -> Self {
        Self { element }
    }

    /// Get the underlying IUIAutomationElement
    pub fn inner(&self) -> &IUIAutomationElement {
        &self.element
    }

    /// Get the element's name/text
    pub fn name(&self) -> Result<String> {
        unsafe {
            self.element
                .CurrentName()
                .map(|bstr| bstr.to_string())
                .map_err(|e| ScreenBridgeError::PropertyError(format!("Failed to get name: {}", e)))
        }
    }

    /// Get the element's control type name
    pub fn control_type(&self) -> Result<String> {
        unsafe {
            self.element
                .CurrentLocalizedControlType()
                .map(|bstr| bstr.to_string())
                .map_err(|e| {
                    ScreenBridgeError::PropertyError(format!("Failed to get control type: {}", e))
                })
        }
    }

    /// Get the element's automation ID
    pub fn automation_id(&self) -> Result<String> {
        unsafe {
            self.element
                .CurrentAutomationId()
                .map(|bstr| bstr.to_string())
                .map_err(|e| {
                    ScreenBridgeError::PropertyError(format!("Failed to get automation ID: {}", e))
                })
        }
    }

    /// Check if the element is enabled
    pub fn is_enabled(&self) -> Result<bool> {
        unsafe {
            self.element.CurrentIsEnabled().map(|b| b.as_bool()).map_err(
                |e| ScreenBridgeError::PropertyError(format!("Failed to check if enabled: {}", e)),
            )
        }
    }

    /// Check if the element is visible (not hidden)
    ///
    /// This is a UIA property that indicates if the element is visible to the user.
    pub fn is_visible(&self) -> Result<bool> {
        unsafe {
            self.element
                .CurrentIsOffscreen()
                .map(|b| !b.as_bool()) // Invert: if NOT offscreen, then visible
                .map_err(|e| {
                    ScreenBridgeError::PropertyError(format!("Failed to check visibility: {}", e))
                })
        }
    }

    /// Check if the element is offscreen (not visible on any monitor)
    pub fn is_offscreen(&self) -> Result<bool> {
        unsafe {
            self.element.CurrentIsOffscreen().map(|b| b.as_bool()).map_err(
                |e| ScreenBridgeError::PropertyError(format!("Failed to check offscreen: {}", e)),
            )
        }
    }

    /// Check if the element is a keyboard focusable element
    pub fn is_keyboard_focusable(&self) -> Result<bool> {
        unsafe {
            self.element
                .CurrentIsKeyboardFocusable()
                .map(|b| b.as_bool())
                .map_err(|e| {
                    ScreenBridgeError::PropertyError(format!(
                        "Failed to check keyboard focusable: {}",
                        e
                    ))
                })
        }
    }

    /// Get the bounding rectangle of the element
    ///
    /// Returns (left, top, width, height) in screen coordinates
    pub fn bounding_rectangle(&self) -> Result<(i32, i32, i32, i32)> {
        unsafe {
            self.element.CurrentBoundingRectangle().map(|rect| {
                (
                    rect.left as i32,
                    rect.top as i32,
                    (rect.right - rect.left) as i32,
                    (rect.bottom - rect.top) as i32,
                )
            }).map_err(|e| {
                ScreenBridgeError::PropertyError(format!("Failed to get bounding rectangle: {}", e))
            })
        }
    }

    /// Get the framework ID (e.g., "Win32", "WPF", "WinForm")
    pub fn framework_id(&self) -> Result<String> {
        unsafe {
            self.element
                .CurrentFrameworkId()
                .map(|bstr| bstr.to_string())
                .map_err(|e| {
                    ScreenBridgeError::PropertyError(format!("Failed to get framework ID: {}", e))
                })
        }
    }

    /// Get the process ID that owns this element
    pub fn process_id(&self) -> Result<i32> {
        unsafe {
            self.element.CurrentProcessId().map_err(|e| {
                ScreenBridgeError::PropertyError(format!("Failed to get process ID: {}", e))
            })
        }
    }

    /// Get the element's class name
    pub fn class_name(&self) -> Result<String> {
        unsafe {
            self.element
                .CurrentClassName()
                .map(|bstr| bstr.to_string())
                .map_err(|e| {
                    ScreenBridgeError::PropertyError(format!("Failed to get class name: {}", e))
                })
        }
    }

    /// Click/invoke this element
    pub fn click(&self) -> Result<()> {
        // Implementation will use Invoke pattern or Click pattern
        todo!("Implement click action using UI Automation patterns")
    }

    /// Set value for this element (for editable controls)
    pub fn set_value(&self, _value: &str) -> Result<()> {
        // Implementation will use Value pattern
        todo!("Implement set_value using Value pattern")
    }
}

// Implement Debug for UIElement
impl std::fmt::Debug for UIElement {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("UIElement")
            .field("name", &self.name().unwrap_or_default())
            .field("control_type", &self.control_type().unwrap_or_default())
            .finish()
    }
}

/// Window handle wrapper
#[derive(Debug, Clone)]
pub struct WindowHandle {
    /// The UI element representing the window
    element: UIElement,
    /// Window title
    pub title: String,
    /// Process ID
    pub process_id: i32,
}

impl WindowHandle {
    /// Create a new WindowHandle
    pub fn new(element: UIElement, title: String, process_id: i32) -> Self {
        Self {
            element,
            title,
            process_id,
        }
    }

    /// Get the underlying UI element
    pub fn element(&self) -> &UIElement {
        &self.element
    }
}

/// Status bar items extracted from Word
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StatusBarItems {
    /// Page number text (if available)
    pub page_number: Option<String>,
    /// Language setting text (if available)
    pub language: Option<String>,
    /// Text predictions status (if available)
    pub text_predictions: Option<String>,
    /// Accessibility checker status (if available)
    pub accessibility_checker: Option<String>,
    /// Zoom controls
    #[serde(skip)]
    pub zoom_controls: Vec<UIElement>,
    /// Other interactive buttons
    #[serde(skip)]
    pub buttons: Vec<UIElement>,
    /// Sliders (e.g., zoom slider)
    #[serde(skip)]
    pub sliders: Vec<UIElement>,
}

impl Default for StatusBarItems {
    fn default() -> Self {
        Self {
            page_number: None,
            language: None,
            text_predictions: None,
            accessibility_checker: None,
            zoom_controls: Vec::new(),
            buttons: Vec::new(),
            sliders: Vec::new(),
        }
    }
}

/// Navigation pane structure
#[derive(Debug)]
pub struct NavigationPane {
    /// Search box element
    pub search_box: Option<UIElement>,
    /// Search button element
    pub search_button: Option<UIElement>,
    /// Tab elements
    pub tabs: NavigationTabs,
}

/// Navigation pane tabs
#[derive(Debug)]
pub struct NavigationTabs {
    /// Headings tab
    pub headings: Option<UIElement>,
    /// Pages tab
    pub pages: Option<UIElement>,
    /// Results tab
    pub results: Option<UIElement>,
}

/// Accessibility assistant items
#[derive(Debug)]
pub struct AccessibilityItems {
    /// "Looks good" button
    pub looks_good_button: Option<UIElement>,
    /// Accessibility issues by category
    pub issues: AccessibilityIssues,
}

/// Categorized accessibility issues
#[derive(Debug)]
pub struct AccessibilityIssues {
    /// Color contrast issues
    pub color_contrast: Vec<UIElement>,
    /// Media/illustration issues
    pub media_illustration: Vec<UIElement>,
    /// Table issues
    pub tables: Vec<UIElement>,
    /// Document structure issues
    pub document_structure: Vec<UIElement>,
    /// Document access issues
    pub document_access: Vec<UIElement>,
}

/// Grammar and spelling check items
#[derive(Debug)]
pub struct GrammarCheckItems {
    /// Editor score element
    pub score: Option<UIElement>,
    /// Corrections category
    pub corrections: GrammarCorrections,
    /// Refinements category
    pub refinements: GrammarRefinements,
}

/// Grammar corrections
#[derive(Debug)]
pub struct GrammarCorrections {
    /// Spelling issues
    pub spelling: Option<UIElement>,
    /// Grammar issues
    pub grammar: Option<UIElement>,
}

/// Grammar refinements
#[derive(Debug)]
pub struct GrammarRefinements {
    /// Clarity suggestions
    pub clarity: Option<UIElement>,
    /// Conciseness suggestions
    pub conciseness: Option<UIElement>,
    /// Formality suggestions
    pub formality: Option<UIElement>,
}

/// Font controls from ribbon
#[derive(Debug)]
pub struct FontControls {
    /// Font name dropdown
    pub font_name: Option<UIElement>,
    /// Font size dropdown
    pub font_size: Option<UIElement>,
    /// Grow font button
    pub grow_font: Option<UIElement>,
    /// Shrink font button
    pub shrink_font: Option<UIElement>,
    /// Clear formatting button
    pub clear_formatting: Option<UIElement>,
    /// Bold button
    pub bold: Option<UIElement>,
    /// Italic button
    pub italic: Option<UIElement>,
    /// Underline button
    pub underline: Option<UIElement>,
    /// Strikethrough button
    pub strikethrough: Option<UIElement>,
    /// Subscript button
    pub subscript: Option<UIElement>,
    /// Superscript button
    pub superscript: Option<UIElement>,
}
