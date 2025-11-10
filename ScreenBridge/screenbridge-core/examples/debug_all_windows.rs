//! Debug tool - See EXACTLY what UI Automation finds
//!
//! This will help us understand why some windows aren't being detected.

use screenbridge_core::{AutomationContext, Result};
use windows::Win32::UI::Accessibility::TreeScope_Children;

fn main() -> Result<()> {
    println!("🔍 UI Automation Debug - What Can We Actually See?");
    println!("===================================================\n");

    let context = AutomationContext::new()?;
    let root = context.get_root_element()?;

    unsafe {
        let automation = context.automation();

        // Find ALL elements, no filtering
        let true_condition = automation.CreateTrueCondition()?;

        println!("Searching for ALL immediate children of desktop...\n");

        match root.FindAll(TreeScope_Children, &true_condition) {
            Ok(elements) => {
                let count = elements.Length()?;
                println!("✓ Found {} elements total\n", count);
                println!("Listing all elements:\n");

                for i in 0..count {
                    if let Ok(element) = elements.GetElement(i) {
                        let name = element.CurrentName()
                            .map(|s| s.to_string())
                            .unwrap_or_else(|_| "<no name>".to_string());

                        let control_type = element.CurrentLocalizedControlType()
                            .map(|s| s.to_string())
                            .unwrap_or_else(|_| "<unknown>".to_string());

                        let class = element.CurrentClassName()
                            .map(|s| s.to_string())
                            .unwrap_or_else(|_| "<no class>".to_string());

                        let process_id = element.CurrentProcessId()
                            .unwrap_or(-1);

                        // Only show elements with names or window control type
                        if !name.is_empty() || control_type.to_lowercase().contains("window") {
                            println!("Element #{}", i + 1);
                            println!("  Name:    {}", name);
                            println!("  Type:    {}", control_type);
                            println!("  Class:   {}", class);
                            println!("  PID:     {}", process_id);
                            println!();
                        }
                    }
                }
            }
            Err(e) => {
                println!("✗ Failed to enumerate elements: {}", e);
            }
        }
    }

    println!("\n💡 Analysis:");
    println!("  - If you see many 'window' types, enumeration works");
    println!("  - If you see your apps listed, the problem is in our filtering");
    println!("  - If apps are missing, they might be using different window structures");

    Ok(())
}
