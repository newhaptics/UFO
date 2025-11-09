//! Advanced example: Explore Word window structure
//!
//! This example demonstrates:
//! - Finding Word windows
//! - Exploring child elements
//! - Understanding the UI hierarchy
//!
//! This is useful for:
//! - Debugging element discovery
//! - Understanding Word's UI structure
//! - Finding element names and types for implementation
//!
//! Run with:
//! ```
//! cargo run --example explore_window_structure
//! ```

use screenbridge_core::{Result, WordAutomation};
use windows::Win32::UI::Accessibility::TreeScope_Children;

fn main() -> Result<()> {
    println!("ScreenBridge - Word Window Structure Explorer");
    println!("=============================================\n");

    let word = WordAutomation::new()?;
    println!("✓ UI Automation initialized\n");

    let windows = word.find_windows()?;

    if windows.is_empty() {
        println!("✗ No Word windows found. Please open Word first.");
        return Ok(());
    }

    println!("Found {} Word window(s). Exploring first window...\n", windows.len());

    let window = &windows[0];
    println!("Window: {}", window.title);
    println!("========================================\n");

    // Explore immediate children of the window
    println!("Top-level child elements:");
    println!("------------------------");

    let element = window.element();

    unsafe {
        // Use the automation context from WordAutomation
        let automation = word.context().automation();
        let true_condition = automation.CreateTrueCondition()?;

        // Find all immediate children
        match element.inner().FindAll(TreeScope_Children, &true_condition) {
            Ok(children) => {
                let count = children.Length()?;
                println!("Found {} immediate children\n", count);

                for i in 0..count {
                    if let Ok(child) = children.GetElement(i) {
                        let name = child.CurrentName()
                            .map(|s| s.to_string())
                            .unwrap_or_else(|_| "<no name>".to_string());

                        let control_type = child.CurrentLocalizedControlType()
                            .map(|s| s.to_string())
                            .unwrap_or_else(|_| "<unknown>".to_string());

                        let class = child.CurrentClassName()
                            .map(|s| s.to_string())
                            .unwrap_or_else(|_| "<no class>".to_string());

                        let auto_id = child.CurrentAutomationId()
                            .map(|s| s.to_string())
                            .unwrap_or_else(|_| "".to_string());

                        println!("Child #{}", i + 1);
                        println!("  Name:         {}", name);
                        println!("  Type:         {}", control_type);
                        println!("  Class:        {}", class);
                        if !auto_id.is_empty() {
                            println!("  AutomationID: {}", auto_id);
                        }
                        println!();
                    }
                }

                println!("\n💡 Tip: Look for these elements:");
                println!("  - 'MsoDockBottom' class = Status Bar");
                println!("  - 'MsoDockTop' class = Ribbon");
                println!("  - 'MsoDockLeft' class = Navigation Pane");
                println!("  - 'MsoDockRight' class = Editor/Accessibility Pane");
                println!("  - '_WwG' class = Document area");
            }
            Err(e) => {
                println!("✗ Failed to enumerate children: {}", e);
            }
        }
    }

    Ok(())
}
