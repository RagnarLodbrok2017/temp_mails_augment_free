import sys
import os
from utils.paths import get_home_dir, get_app_data_dir, get_storage_path, get_db_path, get_machine_id_path,get_workspace_storage_path
from augutils.json_modifier import modify_telemetry_ids
from augutils.sqlite_modifier import clean_augment_data
from augutils.workspace_cleaner import clean_workspace_storage


def run_console_mode():
    """Run the original console-based interface"""
    print("🚀 Free AugmentCode - Console Mode")
    print("=" * 50)
    print("System Paths:")
    print(f"Home Directory: {get_home_dir()}")
    print(f"App Data Directory: {get_app_data_dir()}")
    print(f"Storage Path: {get_storage_path()}")
    print(f"DB Path: {get_db_path()}")
    print(f"Machine ID Path: {get_machine_id_path()}")
    print(f"Workspace Storage Path: {get_workspace_storage_path()}")

    print("\nModifying Telemetry IDs:")
    try:
        result = modify_telemetry_ids()
        print("\nBackup created at:")
        print(f"Storage backup path: {result['storage_backup_path']}")
        if result['machine_id_backup_path']:
            print(f"Machine ID backup path: {result['machine_id_backup_path']}")

        print("\nOld IDs:")
        print(f"Machine ID: {result['old_machine_id']}")
        print(f"Device ID: {result['old_device_id']}")

        print("\nNew IDs:")
        print(f"Machine ID: {result['new_machine_id']}")
        print(f"Device ID: {result['new_device_id']}")

        print("\nCleaning SQLite Database:")
        db_result = clean_augment_data()
        print(f"Database backup created at: {db_result['db_backup_path']}")
        print(f"Deleted {db_result['deleted_rows']} rows containing 'augment' in their keys")

        print("\nCleaning Workspace Storage:")
        ws_result = clean_workspace_storage()
        print(f"Workspace backup created at: {ws_result['backup_path']}")
        print(f"Deleted {ws_result['deleted_files_count']} files from workspace storage")

        print("\n🎉 All tasks completed successfully!")
        print("Now you can run VS Code and login with the new email.")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")


def run_gui_mode():
    """Run the GUI interface"""
    try:
        import tkinter as tk
        from gui import FreeAugmentCodeGUI

        root = tk.Tk()
        app = FreeAugmentCodeGUI(root)
        root.mainloop()
    except ImportError as e:
        missing_module = str(e).split("'")[1] if "'" in str(e) else "unknown"
        print(f"❌ GUI mode requires additional dependencies. Missing: {missing_module}")
        print("💡 Install dependencies with: pip install -r requirements.txt")
        print("Falling back to console mode...")
        run_console_mode()
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        print("💡 You can try the demo mode: python demo_temp_email.py")
        print("Falling back to console mode...")
        run_console_mode()


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--console', '-c']:
            run_console_mode()
        elif sys.argv[1] in ['--gui', '-g']:
            run_gui_mode()
        elif sys.argv[1] in ['--help', '-h']:
            print("🚀 Free AugmentCode")
            print("Usage:")
            print("  python index.py          # Auto-detect best interface")
            print("  python index.py --gui    # Force GUI mode")
            print("  python index.py --console # Force console mode")
            print("  python index.py --help   # Show this help")
        else:
            print(f"❌ Unknown argument: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        # Auto-detect: try GUI first, fall back to console
        try:
            import tkinter as tk
            # Test if we can create a Tk instance (GUI available)
            test_root = tk.Tk()
            test_root.withdraw()  # Hide the test window
            test_root.destroy()

            print("🖥️  GUI available - starting easy layout mode...")
            print("💡 Use 'python index.py --console' for console mode")
            run_gui_mode()
        except (ImportError, tk.TclError):
            print("📟 GUI not available - starting console mode...")
            print("💡 Install tkinter for GUI mode")
            run_console_mode()