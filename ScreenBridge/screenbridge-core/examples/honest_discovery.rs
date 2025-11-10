//! Honest API - All windows with property-based filtering
//!
//! This example demonstrates the HONEST API approach:
//! - Layer 1 (Rust): Returns ALL windows/panes with ALL properties
//! - YOU decide: Filter based on UIA properties, not hardcoded lists
//!
//! This is the RIGHT architecture:
//! - No hardcoded "system window" lists that break
//! - All filtering based on queryable UIA properties
//! - Higher layers (MCP, AI) can make intelligent filtering decisions
//!
//! Run with:
//! ```
//! cargo run --example honest_discovery
//! ```

use screenbridge_core::{AutomationContext, Result, WindowDiscovery, WindowFilter};

fn main() -> Result<()> {
    println!("ScreenBridge - Honest API Discovery");
    println!("====================================\n");

    let context = AutomationContext::new()?;
    let discovery = WindowDiscovery::new(&context);

    println!("🔍 Layer 1: RAW - All Windows/Panes (NO filtering)");
    println!("───────────────────────────────────────────────────\n");

    let all = discovery.find_all_windows()?;
    println!("Found {} total windows/panes\n", all.len());

    for (i, window) in all.iter().enumerate() {
        let element = window.element();

        // Query UIA properties (honest data!)
        let visible = element.is_visible().unwrap_or(false);
        let offscreen = element.is_offscreen().unwrap_or(false);
        let focusable = element.is_keyboard_focusable().unwrap_or(false);
        let class = element.class_name().unwrap_or_default();

        println!("Window #{}", i + 1);
        println!("  Title:      {}", window.title);
        println!("  Class:      {}", class);
        println!("  Visible:    {}", visible);
        println!("  Offscreen:  {}", offscreen);
        println!("  Focusable:  {}", focusable);
        println!();
    }

    println!("\n🎯 Layer 2: FILTERED - Using UIA Properties");
    println!("───────────────────────────────────────────────────\n");

    // Example 1: Only visible windows
    println!("Example 1: Only VISIBLE windows");
    let filter = WindowFilter::default().only_visible();
    let visible_windows = discovery.find_windows_with_filter(&filter)?;
    println!("  Found {} visible windows\n", visible_windows.len());

    // Example 2: Visible + Focusable (typical app windows)
    println!("Example 2: Visible + Focusable (typical apps)");
    let filter = WindowFilter::default()
        .only_visible()
        .only_focusable();
    let app_windows = discovery.find_windows_with_filter(&filter)?;
    println!("  Found {} application windows:", app_windows.len());
    for window in app_windows.iter() {
        println!("    - {}", window.title);
    }
    println!();

    // Example 3: Specific app with properties
    println!("Example 3: Word windows (visible only)");
    let filter = WindowFilter::for_process("winword.exe")
        .only_visible()
        .only_main_windows();
    let word_windows = discovery.find_windows_with_filter(&filter)?;
    println!("  Found {} Word windows\n", word_windows.len());

    println!("\n💡 Key Insights:");
    println!("───────────────────────────────────────────────────");
    println!("✅ Layer 1 returns EVERYTHING (taskbar, desktop, apps)");
    println!("✅ No hardcoded 'system window' lists");
    println!("✅ All filtering uses UIA properties (visible, focusable, etc.)");
    println!("✅ Higher layers can apply intelligent filtering");
    println!("✅ MCP/AI can decide what matters for each use case\n");

    println!("🔬 Available Properties for Filtering:");
    println!("  - is_visible() / is_offscreen()");
    println!("  - is_keyboard_focusable()");
    println!("  - is_enabled()");
    println!("  - bounding_rectangle()");
    println!("  - framework_id()");
    println!("  - class_name()");
    println!("  - automation_id()");

    Ok(())
}
