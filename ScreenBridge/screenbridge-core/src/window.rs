//! Word-specific window management
//!
//! This module is deprecated in favor of the generic `discovery` module.
//! Kept for backwards compatibility.

// This module is now mostly empty as functionality moved to discovery.rs
// We keep it to avoid breaking existing code structure

#[deprecated(
    since = "0.2.0",
    note = "Use `discovery::WindowDiscovery` instead for generic window discovery"
)]
pub fn _legacy_note() {}
