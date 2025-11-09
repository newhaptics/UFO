//! Basic example: Find and inspect Word windows
//!
//! This example demonstrates:
//! - Initializing WordAutomation
//! - Finding all open Word windows
//! - Reading basic window properties
//!
//! Prerequisites:
//! - Microsoft Word must be running
//! - At least one document should be open
//!
//! Run with:
//! ```
//! cargo run --example find_word_windows
//! ```

use screenbridge_core::{Result, WordAutomation};

fn main() -> Result<()> {
    println!("ScreenBridge - Word Window Discovery Example");
    println!("=============================================\n");

    // Initialize the automation context
    println!("Initializing UI Automation...");
    let word = WordAutomation::new()?;
    println!("✓ UI Automation initialized\n");

    // Find all Word windows
    println!("Searching for Word windows...");
    match word.find_windows() {
        Ok(windows) => {
            println!("✓ Found {} Word window(s)\n", windows.len());

            // Print information about each window
            for (i, window) in windows.iter().enumerate() {
                println!("Window #{}", i + 1);
                println!("  Title:      {}", window.title);
                println!("  Process ID: {}", window.process_id);

                // Try to get additional properties from the window element
                let element = window.element();

                match element.class_name() {
                    Ok(class) => println!("  Class:      {}", class),
                    Err(_) => println!("  Class:      <unable to read>"),
                }

                match element.is_enabled() {
                    Ok(enabled) => println!("  Enabled:    {}", enabled),
                    Err(_) => println!("  Enabled:    <unable to read>"),
                }

                match element.automation_id() {
                    Ok(id) if !id.is_empty() => println!("  Auto ID:    {}", id),
                    _ => println!("  Auto ID:    <none>"),
                }

                println!();
            }

            // Summary
            if windows.is_empty() {
                println!("⚠ No Word windows found.");
                println!("  Make sure Microsoft Word is running with at least one document open.");
            } else {
                println!("✓ Successfully discovered {} Word window(s)", windows.len());
            }
        }
        Err(e) => {
            println!("✗ Failed to find Word windows: {}", e);
            println!("\nTroubleshooting:");
            println!("  1. Make sure Microsoft Word is running");
            println!("  2. Open at least one document");
            println!("  3. Ensure you have permission to access Word's UI");
            return Err(e);
        }
    }

    Ok(())
}
