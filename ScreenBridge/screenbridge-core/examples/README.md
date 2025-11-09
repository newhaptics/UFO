# ScreenBridge Examples

This directory contains examples demonstrating how to use the ScreenBridge library.

## Prerequisites

- **Windows 10 or later**
- **Microsoft Word** installed and running
- **Rust 1.70+** installed

## Available Examples

### 1. `find_word_windows` - Basic Window Discovery

The simplest example showing how to find and inspect Word windows.

**What it does:**
- Initializes UI Automation
- Finds all open Word windows
- Displays window titles, process IDs, and basic properties

**Run it:**
```bash
cargo run --example find_word_windows
```

**Prerequisites:**
- Open Microsoft Word
- Have at least one document open (blank document is fine)

**Expected output:**
```
ScreenBridge - Word Window Discovery Example
=============================================

Initializing UI Automation...
✓ UI Automation initialized

Searching for Word windows...
✓ Found 1 Word window(s)

Window #1
  Title:      Document1 - Word
  Process ID: 12345
  Class:      OpusApp
  Enabled:    true
  Auto ID:    <none>

✓ Successfully discovered 1 Word window(s)
```

---

### 2. `explore_window_structure` - Advanced UI Exploration

A more advanced example that explores the UI element hierarchy of Word windows.

**What it does:**
- Finds Word windows
- Enumerates all immediate child elements
- Displays element names, types, classes, and IDs
- Helps understand Word's UI structure for implementing features

**Run it:**
```bash
cargo run --example explore_window_structure
```

**Prerequisites:**
- Open Microsoft Word
- Have at least one document open

**Expected output:**
```
ScreenBridge - Word Window Structure Explorer
=============================================

✓ UI Automation initialized

Found 1 Word window(s). Exploring first window...

Window: Document1 - Word
========================================

Top-level child elements:
------------------------
Found 5 immediate children

Child #1
  Name:         Ribbon
  Type:         pane
  Class:        MsoDockTop

Child #2
  Name:         <no name>
  Type:         pane
  Class:        _WwG

Child #3
  Name:         Status Bar
  Type:         pane
  Class:        MsoDockBottom

...

💡 Tip: Look for these elements:
  - 'MsoDockBottom' class = Status Bar
  - 'MsoDockTop' class = Ribbon
  - 'MsoDockLeft' class = Navigation Pane
  - 'MsoDockRight' class = Editor/Accessibility Pane
  - '_WwG' class = Document area
```

---

## Common Issues

### "No Word windows found"

**Solutions:**
1. Make sure Microsoft Word is running
2. Open at least one document (File → New → Blank Document)
3. Check that Word isn't minimized

### "Failed to initialize UI Automation"

**Solutions:**
1. Run as Administrator (UI Automation may require elevated privileges)
2. Check that Windows UI Automation service is running
3. Ensure no antivirus is blocking the application

### "Access denied" errors

**Solutions:**
1. Run the example as Administrator
2. Check Windows security settings for UI Automation access
3. Ensure Word isn't running with higher privileges than the example

---

## Using These Examples as a Starting Point

These examples demonstrate the basic patterns for using ScreenBridge:

```rust
use screenbridge_core::{Result, WordAutomation};

fn main() -> Result<()> {
    // 1. Initialize
    let word = WordAutomation::new()?;

    // 2. Find windows
    let windows = word.find_windows()?;

    // 3. Work with the first window
    if let Some(window) = windows.first() {
        // Access window properties
        println!("Title: {}", window.title);

        // Get the UI element
        let element = window.element();

        // Read element properties
        let name = element.name()?;
        let enabled = element.is_enabled()?;
    }

    Ok(())
}
```

---

## Next Steps

After running these examples successfully:

1. **Try with different Word configurations:**
   - Open multiple documents
   - Open different Word UI elements (Navigation Pane, Accessibility Checker, etc.)
   - Try with different Word versions

2. **Experiment with the code:**
   - Modify the examples to explore deeper in the element tree
   - Add more property reading
   - Try finding specific elements by name or type

3. **Build on the foundation:**
   - Look at the Python implementation in `../../python-legacy/`
   - Start implementing specific feature extraction (status bar, navigation, etc.)
   - Add error handling for your use cases

---

## Debugging Tips

If you need to debug UI element discovery:

1. **Use Inspect.exe** (from Windows SDK):
   - Shows the UI Automation tree
   - Displays element properties
   - Helps identify element names and types

2. **Add more logging:**
   ```rust
   println!("DEBUG: {:?}", element);
   ```

3. **Check element tree depth:**
   - Some elements are nested deeper
   - Use `TreeScope_Descendants` instead of `TreeScope_Children`

4. **Handle stale elements:**
   - UI elements can become invalid if the window changes
   - Always check for errors when accessing properties

---

## Contributing

Found a bug in an example? Have a suggestion for a new example?

Please open an issue or submit a pull request!
