# Testing Instructions for ScreenBridge

## Quick Test Procedure

### Step 1: Prepare Word

1. **Open Microsoft Word**
2. **Create a new blank document** (or open any existing document)
3. **Keep Word running** in the background

### Step 2: Run the Basic Example

Open a terminal and run:

```bash
cd D:\Github\NHUFO\ScreenBridge\screenbridge-core
cargo run --example find_word_windows
```

**Expected Success Output:**
```
ScreenBridge - Word Window Discovery Example
=============================================

Initializing UI Automation...
✓ UI Automation initialized

Searching for Word windows...
✓ Found 1 Word window(s)

Window #1
  Title:      Document1 - Word
  Process ID: [some number]
  Class:      OpusApp
  Enabled:    true
  Auto ID:    <none>

✓ Successfully discovered 1 Word window(s)
```

**If it fails**, you might see:
```
✗ Failed to find Word windows: Window not found or invalid: No Word windows found

Troubleshooting:
  1. Make sure Microsoft Word is running
  2. Open at least one document
  3. Ensure you have permission to access Word's UI
```

### Step 3: Run the Advanced Example

```bash
cargo run --example explore_window_structure
```

This will show you the UI element tree of the Word window, which helps understand what elements are available for automation.

### Step 4: Validate the Output

You should see elements like:
- **MsoDockTop** (Ribbon)
- **MsoDockBottom** (Status Bar)
- **_WwG** (Document area)

If you see these, the foundation is working correctly! ✅

---

## Common Test Scenarios

### Scenario 1: Single Document
- Open one Word document
- Run `find_word_windows`
- Should find exactly 1 window

### Scenario 2: Multiple Documents
- Open 2-3 Word documents
- Run `find_word_windows`
- Should find multiple windows

### Scenario 3: With UI Elements Open
- Open Word
- Open Navigation Pane (View → Navigation Pane)
- Open Accessibility Checker
- Run `explore_window_structure`
- Should see **MsoDockLeft** and **MsoDockRight** in the output

---

## Troubleshooting

### Issue: "No Word windows found"
**Fix:** Make sure Word is running with a document open

### Issue: "Failed to initialize UI Automation"
**Fix:** Try running as Administrator:
```bash
# Right-click Command Prompt → Run as Administrator
cd D:\Github\NHUFO\ScreenBridge\screenbridge-core
cargo run --example find_word_windows
```

### Issue: "Access denied" or permission errors
**Fix:** Check Windows security settings, or try running both Word and the example with the same privilege level

---

## Next Steps After Successful Test

Once the examples work:

1. ✅ Foundation is validated
2. ✅ Window discovery works
3. ✅ UI element access works

Then we can proceed to:
- Implement status bar extraction
- Implement navigation pane access
- Implement accessibility features
- Add comprehensive tests

---

## Automated Testing

For CI/CD or automated testing, you can:

1. **Mock the UI Automation API** (for unit tests)
2. **Use integration tests with Word** (requires Word installed)
3. **Test against recorded UI element data** (snapshot testing)

More details on testing strategy will be added as we implement more features.
