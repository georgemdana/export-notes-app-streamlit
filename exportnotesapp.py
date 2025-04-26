import streamlit as st
import subprocess
import os
from pathlib import Path
import re
from datetime import datetime

# Default export directory
DEFAULT_EXPORT_DIR = "~/NotesExport"

def run_applescript(script):
    """Execute an AppleScript and return the result or error."""
    try:
        process = subprocess.run(['osascript', '-'], input=script, text=True, capture_output=True, check=True)
        return True, process.stdout.strip(), None
    except subprocess.CalledProcessError as e:
        return False, None, f"AppleScript error: {e.stderr}"
    except Exception as e:
        return False, None, f"Error running AppleScript: {str(e)}"

def get_notes_folders():
    """Get list of top-level folders from Notes.app."""
    applescript = """
    tell application "Notes"
        set folderNames to name of every folder
        return folderNames
    end tell
    """
    success, output, error = run_applescript(applescript)
    if success:
        folders = output.split(", ") if output else []
        return folders, None
    return [], error

def get_subfolders(parent_folder):
    """Get subfolders within a parent folder in Notes.app."""
    applescript = f"""
    tell application "Notes"
        set parentFolder to folder "{parent_folder}"
        set subfolderNames to {{}}
        try
            set subfolders to every folder of parentFolder
            repeat with sub in subfolders
                set end of subfolderNames to name of sub
            end repeat
        end try
        return subfolderNames
    end tell
    """
    success, output, error = run_applescript(applescript)
    if success:
        subfolders = output.split(", ") if output else []
        return subfolders, None
    return [], error

def export_notes(folder, subfolder, export_dir):
    """Export notes from the specified folder/subfolder to export_dir without modifying Notes.app."""
    export_dir = Path(export_dir).expanduser()
    # Sanitize folder and subfolder names to prevent AppleScript injection
    folder = folder.replace('"', '\\"')
    subfolder = subfolder.replace('"', '\\"') if subfolder else ""
    # Handle subfolder selection safely
    subfolder_line = f'set targetFolder to folder "{subfolder}" of targetFolder' if subfolder else ''
    applescript = f"""
    tell application "Notes"
        set exportFolder to POSIX path of "{export_dir}"
        do shell script "mkdir -p " & quoted form of exportFolder
        
        try
            set targetFolder to folder "{folder}"
            {subfolder_line}
            
            set allNotes to notes in targetFolder
            set exportInfo to {{}}
            repeat with aNote in allNotes
                try
                    set noteName to name of aNote
                    set noteBody to body of aNote
                    set creationDate to creation date of aNote
                    set dateStr to my formatDate(creationDate)
                    set firstTwoWords to my getFirstTwoWords(noteName) -- Use noteName instead of noteBody
                    set safeFileName to dateStr & "_" & firstTwoWords
                    set filePath to exportFolder & "/" & safeFileName & ".txt"
                    do shell script "echo " & quoted form of noteBody & " > " & quoted form of filePath
                    set end of exportInfo to "Exported: " & safeFileName
                on error errMsg
                    set end of exportInfo to "Failed: " & noteName & " (" & errMsg & ")"
                end try
            end repeat
            return exportInfo
        on error errMsg
            return "Error: " & errMsg
        end try
    end tell

    on formatDate(theDate)
        set y to year of theDate
        set m to text -2 thru -1 of ("0" & (month of theDate as number))
        set d to text -2 thru -1 of ("0" & day of theDate)
        return y & "-" & m & "-" & d
    end formatDate

    on getFirstTwoWords(theText)
        try
            set wordList to words of theText
            if (count of wordList) = 0 then
                return "Untitled-Note"
            else if (count of wordList) = 1 then
                return (item 1 of wordList) & "-Note"
            else
                return (item 1 of wordList) & "-" & (item 2 of wordList)
            end if
        on error
            return "Untitled-Note"
        end try
    end getFirstTwoWords
    """
    success, output, error = run_applescript(applescript)
    if success:
        if output.startswith("Error:"):
            return False, [], output
        return True, output.split(", ") if output else [], None
    return False, [], error

# Streamlit app layout
st.title("Apple Notes Exporter")
st.write("Select a folder and subfolder from Apple Notes, choose an export directory, and export notes as .txt files. Notes will remain unchanged in Notes.app.")

# Get folders
folders, folder_error = get_notes_folders()
if folder_error:
    st.error(f"Error fetching folders: {folder_error}")
    st.write("Ensure Notes.app is running and Python has permission to control it.")
    folders = []

# Folder selection
selected_folder = st.selectbox("Select Notes Folder", [""] + folders, format_func=lambda x: "Select a folder" if x == "" else x)

# Subfolder selection
subfolders = []
subfolder_error = None
if selected_folder:
    subfolders, subfolder_error = get_subfolders(selected_folder)
    if subfolder_error:
        st.error(f"Error fetching subfolders: {subfolder_error}")

selected_subfolder = st.selectbox(
    "Select Subfolder (Optional)",
    [""] + subfolders,
    format_func=lambda x: "No subfolder" if x == "" else x
)

# Export directory selection
export_dir = st.text_input("Export Directory", value=DEFAULT_EXPORT_DIR, help="Enter a directory path (e.g., ~/NotesExport)")

# Export button
if st.button("Export Notes"):
    if not selected_folder:
        st.error("Please select a folder.")
    elif not export_dir:
        st.error("Please specify an export directory.")
    else:
        try:
            export_path = Path(export_dir).expanduser()
            if not export_path.parent.exists():
                st.error("Parent directory of the export path does not exist.")
            else:
                success, exported_files, error = export_notes(
                    selected_folder,
                    selected_subfolder if selected_subfolder else "",
                    export_dir
                )
                if success:
                    st.success("Notes exported successfully! No notes were modified or deleted in Notes.app.")
                    st.write("Exported files:")
                    for file in exported_files:
                        st.write(f"- {file}")
                else:
                    st.error(f"Export failed: {error}")
                    st.write("Check if Notes.app is open and permissions are granted.")
        except Exception as e:
            st.error(f"Invalid export directory: {str(e)}")

# Debug information
with st.expander("Debug: Export Details"):
    st.write(f"**Selected Folder**: {selected_folder or 'None'}")
    st.write(f"**Selected Subfolder**: {selected_subfolder or 'None'}")
    st.write(f"**Export Directory**: {export_dir}")
    st.write(f"**Available Folders**: {folders}")
    st.write(f"**Available Subfolders**: {subfolders}")
