//! Generic application window discovery
//!
//! This example demonstrates the GENERIC window discovery API that works
//! with ANY Windows application - not just Microsoft Word!
//!
//! What this shows:
//! - Finding windows from multiple applications
//! - Using filters to narrow down results
//! - Generic API that's extensible to any app
//!
//! Try running this with different applications open:
//! - Microsoft Word (winword.exe)
//! - Microsoft Excel (excel.exe)
//! - Google Chrome (chrome.exe)
//! - Visual Studio Code (code.exe)
//! - Notepad (notepad.exe)
//! - Any Windows application!
//!
//! Run with:
//! ```
//! cargo run --example discover_any_app
//! ```

use screenbridge_core::{AutomationContext, Result, WindowDiscovery, WindowFilter};

fn main() -> Result<()> {
    println!("ScreenBridge - Generic Application Discovery");
    println!("============================================\n");

    // Initialize the automation context
    let context = AutomationContext::new()?;
    let discovery = WindowDiscovery::new(&context);

    println!("🔍 Searching for applications...\n");

    // List of common applications to check
    let applications = vec![
        ("Word", "winword.exe"),
        ("Excel", "excel.exe"),
        ("PowerPoint", "powerpnt.exe"),
        ("Chrome", "chrome.exe"),
        ("Edge", "msedge.exe"),
        ("VS Code", "code.exe"),
        ("Notepad", "notepad.exe"),
        ("File Explorer", "explorer.exe"),
    ];

    let mut total_windows = 0;

    for (app_name, process_name) in applications {
        match discovery.find_by_process(process_name) {
            Ok(windows) if !windows.is_empty() => {
                println!("✓ {} - Found {} window(s)", app_name, windows.len());
                total_windows += windows.len();

                // Show details for each window
                for (i, window) in windows.iter().enumerate() {
                    println!("  Window #{}: {}", i + 1, window.title);
                }
                println!();
            }
            Ok(_) => {
                // No windows found, skip silently
            }
            Err(e) => {
                println!("  ⚠ Error checking {}: {}", app_name, e);
            }
        }
    }

    // Summary
    println!("─────────────────────────────────────────");
    println!("Total: Found {} window(s) across all applications", total_windows);

    if total_windows == 0 {
        println!("\n💡 Tip: Open some applications to see them detected!");
        println!("   Try: Word, Excel, Chrome, Notepad, etc.");
    }

    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("Advanced Usage Examples");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

    // Example 1: Find all windows (no filter)
    println!("Example 1: Find ALL windows");
    match discovery.find_all_windows() {
        Ok(all_windows) => {
            println!("  Found {} total windows on desktop", all_windows.len());
        }
        Err(e) => println!("  Error: {}", e),
    }

    // Example 2: Find windows by title
    println!("\nExample 2: Find windows with 'Document' in title");
    match discovery.find_by_title("Document") {
        Ok(doc_windows) => {
            println!("  Found {} windows", doc_windows.len());
            for window in doc_windows {
                println!("    - {}", window.title);
            }
        }
        Err(e) => println!("  Error: {}", e),
    }

    // Example 3: Custom filter
    println!("\nExample 3: Custom filter (Word main windows only)");
    let custom_filter = WindowFilter::for_process("winword.exe")
        .only_main_windows()
        .with_title("Word");

    match discovery.find_windows_with_filter(&custom_filter) {
        Ok(filtered_windows) => {
            println!("  Found {} Word main windows", filtered_windows.len());
        }
        Err(e) => println!("  Error: {}", e),
    }

    println!("\n✅ Generic window discovery working!");
    println!("   This same API can be used for ANY Windows application.");

    Ok(())
}
