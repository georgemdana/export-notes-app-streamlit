### Apple Notes Exporter
A Streamlit-based application to export notes from Apple Notes to text files without modifying or deleting any notes in Notes.app. The application allows users to select a folder and optional subfolder from Notes, specify an export directory, and save notes as .txt files with filenames based on the note's creation date and first two words of the title.

### Features
Folder and Subfolder Selection: Choose top-level folders or subfolders from Apple Notes.
Custom Export Directory: Specify where to save exported .txt files (defaults to ~/NotesExport).
Safe Export: Notes are exported without any changes to Notes.app.
Filename Generation: Files are named with the format YYYY-MM-DD_First-Word_Second-Word.txt (or Untitled-Note if no words are available).
Error Handling: Displays clear error messages for issues like missing permissions or invalid directories.
Debug Information: View selected folder, subfolder, and available options for troubleshooting.

### Prerequisites
Python 3.8+
macOS (since the app interacts with Apple Notes via AppleScript)
Apple Notes application running
Required Python packages:
streamlit
pathlib

### Permissions
Python must have Automation permissions to control Notes.app and Terminal (for AppleScript execution). You may be prompted to grant these permissions on first run.

### Installation
Clone or download this repository:git clone <repository-url>
cd apple-notes-exporter

Install dependencies:
pip install streamlit

Ensure Notes.app is open and you have granted necessary permissions in System Settings > Privacy & Security > Automation for Python and Terminal to control Notes.

### Usage
Run the Streamlit app:streamlit run app.py

Open the displayed URL (usually http://localhost:8501) in your browser.
Select a folder from Notes.app using the dropdown.
Optionally select a subfolder (if available).
Specify an export directory (e.g., ~/NotesExport).
Click Export Notes to save notes as .txt files in the specified directory.
Check the debug section for details or errors if the export fails.

### File Structure
app.py: Main application script containing the Streamlit interface and AppleScript logic.
README.md: This documentation file.

### Notes
Filename Logic: Each exported file is named using the note’s creation date (YYYY-MM-DD) followed by the first two words of the note’s title (e.g., 2025-04-26_My_Note.txt). If the title has fewer than two words, it uses Untitled-Note.
Export Directory: The directory must have a valid parent path. For example, ~/NotesExport will work if ~ exists, but /invalid/path will fail.
Permissions: If you encounter errors, ensure Python and Terminal have Automation permissions for Notes.app in System Settings.
No Modifications: The app only reads notes and does not alter Notes.app in any way.

### Troubleshooting
"Error fetching folders": Ensure Notes.app is open and Python has Automation permissions.
"Invalid export directory": Verify the parent directory exists and is writable.
No subfolders shown: Some folders may not have subfolders, or there may be a permissions issue.
Export fails with AppleScript error: Check the debug section for details and ensure Notes.app is accessible.

### Limitations
Only exports notes as plain text (.txt).
Subfolder selection is optional; if none is selected, all notes in the top-level folder are exported.
AppleScript may fail if folder/subfolder names contain special characters (though the app sanitizes inputs to mitigate this).
Requires macOS and Notes.app; not compatible with other platforms.
