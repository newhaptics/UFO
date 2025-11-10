# ScreenBridge Query Protocol Specification

**Version**: 1.0.0
**Format**: JSON over line-delimited transport
**Style**: JSON-RPC inspired request/response

---

## Overview

This document defines the JSON protocol for querying Windows UI Automation data via ScreenBridge. The protocol is designed for assistive devices (braille displays, screen readers, etc.) to access structured UI information.

### Design Goals

- **Simple**: Easy to implement in any language
- **Efficient**: Minimal overhead, request only what you need
- **Extensible**: Easy to add new query types
- **Stateful**: Server maintains element cache for efficient queries
- **Type-Safe**: Well-defined schemas for all messages

---

## Transport Layer

### Supported Transports

1. **Named Pipe** (Windows IPC): `\\.\pipe\screenbridge`
2. **TCP Socket**: `localhost:7878` (or configurable port)
3. **Stdin/Stdout**: For subprocess communication
4. **UCP Proxy.exe**: Custom device communication channel

### Message Format

**Encoding**: UTF-8 JSON
**Delimiter**: Newline (`\n`)
**Each message**: Single JSON object on one line

```
{"request_id": "1", "query": "list_windows", "params": {}}\n
{"request_id": "2", "query": "get_element_properties", "params": {...}}\n
```

---

## Base Message Structures

### Request Schema

```json
{
  "request_id": "string (required, unique per request)",
  "query": "string (required, query type)",
  "params": {
    /* object (optional, query-specific parameters) */
  }
}
```

**Fields:**
- `request_id`: Unique identifier for this request (echoed in response)
- `query`: Query type (see [Query Types](#query-types))
- `params`: Query-specific parameters (optional, defaults to empty object)

### Response Schema (Success)

```json
{
  "request_id": "string (matches request)",
  "status": "success",
  "data": {
    /* object (response data, query-specific) */
  }
}
```

### Response Schema (Error)

```json
{
  "request_id": "string (matches request)",
  "status": "error",
  "error": {
    "code": "string (error code)",
    "message": "string (human-readable error)",
    "details": { /* object (optional, additional context) */ }
  }
}
```

**Error Codes:**
- `INVALID_REQUEST`: Malformed JSON or missing required fields
- `UNKNOWN_QUERY`: Query type not recognized
- `INVALID_PARAMS`: Invalid parameters for query
- `ELEMENT_NOT_FOUND`: Element ID not in cache
- `WINDOW_NOT_FOUND`: Window ID not in cache
- `UIA_ERROR`: Windows UI Automation error
- `INTERNAL_ERROR`: Server internal error

---

## Query Types

### 1. `list_windows`

List all available windows with optional filtering.

#### Request

```json
{
  "request_id": "req_001",
  "query": "list_windows",
  "params": {
    "filters": {
      "process_name": "string (optional, e.g., 'winword.exe')",
      "title_contains": "string (optional, substring match)",
      "visible_only": "boolean (optional, default: false)",
      "focusable_only": "boolean (optional, default: false)",
      "main_windows_only": "boolean (optional, exclude dialogs, default: false)"
    }
  }
}
```

#### Response

```json
{
  "request_id": "req_001",
  "status": "success",
  "data": {
    "windows": [
      {
        "window_id": "string (unique window identifier)",
        "title": "string (window title)",
        "process_name": "string (e.g., 'winword.exe')",
        "process_id": "integer (process ID)",
        "class_name": "string (window class)",
        "control_type": "string ('window' or 'pane')",
        "visible": "boolean",
        "focusable": "boolean",
        "offscreen": "boolean",
        "enabled": "boolean",
        "bounds": {
          "x": "integer (left)",
          "y": "integer (top)",
          "width": "integer",
          "height": "integer"
        },
        "framework": "string (e.g., 'Win32', 'WPF', 'Electron')"
      }
    ],
    "count": "integer (number of windows returned)"
  }
}
```

#### Example

**Request:**
```json
{
  "request_id": "1",
  "query": "list_windows",
  "params": {
    "filters": {
      "visible_only": true,
      "focusable_only": true
    }
  }
}
```

**Response:**
```json
{
  "request_id": "1",
  "status": "success",
  "data": {
    "windows": [
      {
        "window_id": "win_107084_abc123",
        "title": "Introduction - Word",
        "process_name": "winword.exe",
        "process_id": 107084,
        "class_name": "OpusApp",
        "control_type": "window",
        "visible": true,
        "focusable": true,
        "offscreen": false,
        "enabled": true,
        "bounds": {"x": 0, "y": 0, "width": 1920, "height": 1080},
        "framework": "Win32"
      },
      {
        "window_id": "win_28984_def456",
        "title": "Slack",
        "process_name": "slack.exe",
        "process_id": 28984,
        "class_name": "Chrome_WidgetWin_1",
        "control_type": "pane",
        "visible": true,
        "focusable": true,
        "offscreen": false,
        "enabled": true,
        "bounds": {"x": 1920, "y": 0, "width": 1920, "height": 1080},
        "framework": "Electron"
      }
    ],
    "count": 2
  }
}
```

---

### 2. `get_window_elements`

Get UI elements within a specific window.

#### Request

```json
{
  "request_id": "req_002",
  "query": "get_window_elements",
  "params": {
    "window_id": "string (required, from list_windows)",
    "max_depth": "integer (optional, default: 1, max: 10)",
    "element_types": ["array of strings (optional, e.g., ['pane', 'button', 'text'])"],
    "visible_only": "boolean (optional, default: false)"
  }
}
```

#### Response

```json
{
  "request_id": "req_002",
  "status": "success",
  "data": {
    "window_id": "string",
    "elements": [
      {
        "element_id": "string (unique element identifier)",
        "name": "string (element name/title)",
        "control_type": "string (UIA control type)",
        "class_name": "string",
        "automation_id": "string (optional)",
        "visible": "boolean",
        "enabled": "boolean",
        "focusable": "boolean",
        "offscreen": "boolean",
        "bounds": {
          "x": "integer",
          "y": "integer",
          "width": "integer",
          "height": "integer"
        },
        "depth": "integer (depth from window root)",
        "children_count": "integer",
        "framework": "string"
      }
    ],
    "count": "integer"
  }
}
```

#### Example

**Request:**
```json
{
  "request_id": "2",
  "query": "get_window_elements",
  "params": {
    "window_id": "win_107084_abc123",
    "max_depth": 2,
    "element_types": ["pane", "button"]
  }
}
```

**Response:**
```json
{
  "request_id": "2",
  "status": "success",
  "data": {
    "window_id": "win_107084_abc123",
    "elements": [
      {
        "element_id": "elem_status_bar_001",
        "name": "Status Bar",
        "control_type": "pane",
        "class_name": "MsoDockBottom",
        "automation_id": "",
        "visible": true,
        "enabled": true,
        "focusable": false,
        "offscreen": false,
        "bounds": {"x": 0, "y": 1050, "width": 1920, "height": 30},
        "depth": 1,
        "children_count": 5,
        "framework": "Win32"
      },
      {
        "element_id": "elem_ribbon_001",
        "name": "Ribbon",
        "control_type": "pane",
        "class_name": "MsoDockTop",
        "automation_id": "",
        "visible": true,
        "enabled": true,
        "focusable": false,
        "offscreen": false,
        "bounds": {"x": 0, "y": 0, "width": 1920, "height": 150},
        "depth": 1,
        "children_count": 20,
        "framework": "Win32"
      }
    ],
    "count": 2
  }
}
```

---

### 3. `get_element_properties`

Get detailed properties of a specific element.

#### Request

```json
{
  "request_id": "req_003",
  "query": "get_element_properties",
  "params": {
    "element_id": "string (required, from get_window_elements)",
    "properties": [
      "array of strings (optional, specific properties to query)",
      "Available: name, control_type, class_name, automation_id, visible, enabled, focusable, offscreen, bounds, framework, children_count, value, description"
    ]
  }
}
```

**Note**: If `properties` is omitted, returns all available properties.

#### Response

```json
{
  "request_id": "req_003",
  "status": "success",
  "data": {
    "element_id": "string",
    "properties": {
      "name": "string",
      "control_type": "string",
      "class_name": "string",
      "automation_id": "string",
      "visible": "boolean",
      "enabled": "boolean",
      "focusable": "boolean",
      "offscreen": "boolean",
      "bounds": {
        "x": "integer",
        "y": "integer",
        "width": "integer",
        "height": "integer"
      },
      "framework": "string",
      "children_count": "integer",
      "value": "string (optional, if Value pattern available)",
      "description": "string (optional)"
    }
  }
}
```

#### Example

**Request:**
```json
{
  "request_id": "3",
  "query": "get_element_properties",
  "params": {
    "element_id": "elem_status_bar_001",
    "properties": ["name", "visible", "bounds", "children_count"]
  }
}
```

**Response:**
```json
{
  "request_id": "3",
  "status": "success",
  "data": {
    "element_id": "elem_status_bar_001",
    "properties": {
      "name": "Status Bar",
      "visible": true,
      "bounds": {"x": 0, "y": 1050, "width": 1920, "height": 30},
      "children_count": 5
    }
  }
}
```

---

### 4. `get_element_children`

Get immediate children of a specific element.

#### Request

```json
{
  "request_id": "req_004",
  "query": "get_element_children",
  "params": {
    "element_id": "string (required)",
    "element_types": ["array of strings (optional, filter by control type)"],
    "visible_only": "boolean (optional, default: false)"
  }
}
```

#### Response

Same format as `get_window_elements` response, but scoped to children of the specified element.

---

### 5. `ping`

Health check / keepalive.

#### Request

```json
{
  "request_id": "req_005",
  "query": "ping",
  "params": {}
}
```

#### Response

```json
{
  "request_id": "req_005",
  "status": "success",
  "data": {
    "pong": true,
    "server_version": "1.0.0",
    "timestamp": "2025-01-09T12:34:56Z"
  }
}
```

---

### 6. `clear_cache`

Clear element cache (useful if elements become stale).

#### Request

```json
{
  "request_id": "req_006",
  "query": "clear_cache",
  "params": {}
}
```

#### Response

```json
{
  "request_id": "req_006",
  "status": "success",
  "data": {
    "cleared": true,
    "elements_removed": "integer"
  }
}
```

---

## Element ID Format

Element IDs are opaque strings generated by the server. Format:

```
elem_<type>_<hash>
```

Examples:
- `elem_window_abc123`
- `elem_pane_def456`
- `elem_button_ghi789`

**Important**: Element IDs are only valid for the current session. If the server restarts or cache is cleared, element IDs change.

---

## UIA Control Types

Common control types you'll encounter:

| Control Type | Description | Example |
|--------------|-------------|---------|
| `window` | Top-level window | Application window |
| `pane` | Container/panel | Status bar, ribbon, sidebar |
| `button` | Clickable button | OK, Cancel, Submit |
| `text` | Text element | Labels, static text |
| `edit` | Editable text field | Input box, textarea |
| `document` | Document area | Word document, web page |
| `list` | List container | Dropdown, listbox |
| `listitem` | Item in a list | Menu item, option |
| `menubar` | Menu bar | File, Edit, View menus |
| `menuitem` | Menu item | File → Open |
| `tab` | Tab in tab control | Browser tab, ribbon tab |
| `tabitem` | Individual tab | Home, Insert, Design tabs |
| `toolbar` | Toolbar container | Formatting toolbar |
| `statusbar` | Status bar | Bottom status bar |
| `tree` | Tree view | File explorer tree |
| `treeitem` | Tree node | Folder, file in tree |

For complete list, see [Microsoft UIA Control Types](https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-controltype-ids).

---

## Example Session

### Full conversation between device and ScreenBridge:

```json
// Device: Get all visible windows
→ {"request_id": "1", "query": "list_windows", "params": {"filters": {"visible_only": true}}}

← {"request_id": "1", "status": "success", "data": {"windows": [{"window_id": "win_001", "title": "Word", ...}], "count": 1}}

// Device: Get elements in Word window
→ {"request_id": "2", "query": "get_window_elements", "params": {"window_id": "win_001", "max_depth": 2}}

← {"request_id": "2", "status": "success", "data": {"elements": [{"element_id": "elem_001", "name": "Status Bar", ...}], "count": 10}}

// Device: Get details of status bar
→ {"request_id": "3", "query": "get_element_properties", "params": {"element_id": "elem_001"}}

← {"request_id": "3", "status": "success", "data": {"element_id": "elem_001", "properties": {"name": "Status Bar", ...}}}

// Device: Get status bar's children
→ {"request_id": "4", "query": "get_element_children", "params": {"element_id": "elem_001"}}

← {"request_id": "4", "status": "success", "data": {"elements": [{"element_id": "elem_page_num", "name": "Page 1 of 5", ...}], "count": 5}}
```

---

## Implementation Notes

### Server Responsibilities

1. **Element Caching**: Maintain mapping of element_id → UIElement
2. **Window Caching**: Maintain mapping of window_id → WindowHandle
3. **Stale Detection**: Detect when cached elements become invalid
4. **Error Handling**: Return meaningful errors with context
5. **Performance**: Minimize UIA queries, cache results

### Client Responsibilities

1. **Request IDs**: Generate unique request_id for each query
2. **Error Handling**: Handle error responses gracefully
3. **Cache Management**: Track element/window IDs locally
4. **Reconnection**: Handle server restart (cache cleared)

### Performance Considerations

- **Minimize depth**: Use `max_depth` wisely (higher = slower)
- **Filter early**: Use `element_types` and `visible_only` to reduce data
- **Cache locally**: Don't re-query the same data repeatedly
- **Batch when possible**: Consider adding batch query support in future

---

## Future Extensions

Potential future query types:

- `subscribe_events`: Subscribe to UIA events (window open/close, focus change)
- `batch_query`: Execute multiple queries in one request
- `get_element_text`: Get text content of text elements
- `invoke_element`: Trigger click/invoke on elements
- `set_element_value`: Set value of editable elements
- `get_selection`: Get currently selected text/elements
- `find_elements`: Search for elements by criteria

---

## OpenAPI 3.0 Schema

See `openapi.yaml` for formal OpenAPI specification that can be used to generate client libraries.

---

## Versioning

**Current Version**: 1.0.0

**Versioning Scheme**: Semantic Versioning (MAJOR.MINOR.PATCH)

- **MAJOR**: Breaking changes to protocol
- **MINOR**: New query types or parameters (backwards compatible)
- **PATCH**: Bug fixes, clarifications

**Version Negotiation**: Use `ping` query to check server version.

---

## Questions?

See [README.md](README.md) for general information or [ARCHITECTURE.md](ARCHITECTURE.md) for system design.

For protocol clarifications or extensions, open an issue on GitHub.
