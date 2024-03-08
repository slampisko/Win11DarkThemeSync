# Windows 11 Dark Theme Sync Utility

This is a utility for Windows 11 Night Light and Dark Theme synchronization.
When run, it checks whether or not the Night Light is on, and whether the Dark Theme is activated. If these aren't
synchronized, it turns the Dark Theme on or off depending on the Night Light state, and then exits.
The current version also restarts explorer.exe -- I might decide to scrap that feature if it turns out to be intrusive.
I am using it with the Windows Task Scheduler to run the check periodically.

**Author**: slampisko  
**Original implementation date**: 2024-08-03
