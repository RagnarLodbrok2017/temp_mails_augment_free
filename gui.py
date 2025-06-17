import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
from io import StringIO
import pyperclip
from datetime import datetime
from utils.paths import get_home_dir, get_app_data_dir, get_storage_path, get_db_path, get_machine_id_path, get_workspace_storage_path
from augutils.json_modifier import modify_telemetry_ids
from augutils.sqlite_modifier import clean_augment_data
from augutils.workspace_cleaner import clean_workspace_storage
try:
    from tempmail.real_email_service import RealTempEmailService
    REAL_EMAIL_AVAILABLE = True
except ImportError:
    from tempmail.temp_email_service import InternxtTempEmailService
    REAL_EMAIL_AVAILABLE = False
from tempmail.verification_parser import AdvancedVerificationParser


class FreeAugmentCodeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Free AugmentCode - Easy Layout with Temp Email")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f0f0f0')

        # Initialize temporary email service (use real service if available)
        if REAL_EMAIL_AVAILABLE:
            self.temp_email_service = RealTempEmailService()
            self.using_real_service = True
        else:
            self.temp_email_service = InternxtTempEmailService()
            self.using_real_service = False

        self.verification_parser = AdvancedVerificationParser()
        self.current_verification_codes = []

        # Setup email service callbacks
        self.temp_email_service.add_callback('on_email_received', self.on_email_received)
        self.temp_email_service.add_callback('on_verification_code', self.on_verification_code_found)
        self.temp_email_service.add_callback('on_error', self.on_temp_email_error)
        self.temp_email_service.add_callback('on_status_change', self.on_temp_email_status_change)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(root)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)

        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Create main cleanup tab
        cleanup_frame = ttk.Frame(notebook, padding="20")
        notebook.add(cleanup_frame, text="🧹 Cleanup Tools")
        cleanup_frame.columnconfigure(1, weight=1)

        # Create temporary email tab
        email_frame = ttk.Frame(notebook, padding="20")
        notebook.add(email_frame, text="📧 Temp Email")
        email_frame.columnconfigure(1, weight=1)

        # Setup cleanup tab
        self.setup_cleanup_tab(cleanup_frame)

        # Setup temporary email tab
        self.setup_temp_email_tab(email_frame)

        # Add footer
        self.setup_footer()

    def setup_cleanup_tab(self, main_frame):
        
        """Setup the cleanup tools tab"""
        # Title
        title_label = ttk.Label(main_frame, text="🚀 Free AugmentCode",
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Description
        desc_label = ttk.Label(main_frame,
                              text="Clean AugmentCode data to login with different accounts",
                              font=('Arial', 10))
        desc_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # System Paths Section
        paths_frame = ttk.LabelFrame(main_frame, text="📁 System Paths", padding="10")
        paths_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        paths_frame.columnconfigure(1, weight=1)
        
        # Path labels
        self.create_path_row(paths_frame, 0, "Home Directory:", get_home_dir())
        self.create_path_row(paths_frame, 1, "App Data Directory:", get_app_data_dir())
        self.create_path_row(paths_frame, 2, "Storage Path:", get_storage_path())
        self.create_path_row(paths_frame, 3, "DB Path:", get_db_path())
        self.create_path_row(paths_frame, 4, "Machine ID Path:", get_machine_id_path())
        self.create_path_row(paths_frame, 5, "Workspace Storage:", get_workspace_storage_path())
        
        # Actions Section
        actions_frame = ttk.LabelFrame(main_frame, text="⚡ Actions", padding="10")
        actions_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        actions_frame.columnconfigure(0, weight=1)
        actions_frame.columnconfigure(1, weight=1)
        
        # Action buttons
        self.clean_button = ttk.Button(actions_frame, text="🧹 Clean All Data", 
                                      command=self.clean_all_data, style='Accent.TButton')
        self.clean_button.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Individual action buttons
        ttk.Button(actions_frame, text="🔄 Modify Telemetry IDs", 
                  command=self.modify_ids_only).grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 5), pady=2)
        
        ttk.Button(actions_frame, text="🗃️ Clean Database", 
                  command=self.clean_db_only).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        ttk.Button(actions_frame, text="💾 Clean Workspace", 
                  command=self.clean_workspace_only).grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Output Section
        output_frame = ttk.LabelFrame(main_frame, text="📋 Output", padding="10")
        output_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, width=80)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear output button
        ttk.Button(output_frame, text="Clear Output", 
                  command=self.clear_output).grid(row=1, column=0, pady=(10, 0))
        
        # Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text="📖 Instructions", padding="10")
        instructions_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        instructions_text = """1. Close VS Code completely before running
2. Click 'Clean All Data' to reset everything
3. Restart VS Code
4. Login with a new email in AugmentCode plugin"""
        
        ttk.Label(instructions_frame, text=instructions_text, 
                 font=('Arial', 9), justify=tk.LEFT).grid(row=0, column=0, sticky=tk.W)
        
        # Style configuration
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
        
        # Initial message
        self.log_message("Welcome to Free AugmentCode! Ready to clean your data.")

    def setup_temp_email_tab(self, main_frame):
        """Setup the temporary email tab"""
        main_frame.rowconfigure(4, weight=1)  # Make inbox area expandable

        # Title
        title_label = ttk.Label(main_frame, text="📧 Temporary Email Manager",
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Email Generation Section
        gen_frame = ttk.LabelFrame(main_frame, text="🎯 Email Generation", padding="10")
        gen_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        gen_frame.columnconfigure(1, weight=1)
        gen_frame.columnconfigure(3, weight=1)

        # Row 0: Domain selection and Generate button
        ttk.Label(gen_frame, text="Preferred Domain:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5), pady=5)

        self.domain_var = tk.StringVar(value="Auto (Best Available)")
        self.domain_combo = ttk.Combobox(gen_frame, textvariable=self.domain_var,
                                       state='readonly', width=25)
        self.domain_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)

        # Populate domain options
        if REAL_EMAIL_AVAILABLE:
            try:
                domains = self.temp_email_service.get_available_domains()
                domain_options = ["Auto (Best Available)"] + [f"{domain}" for domain in domains]
                self.domain_combo['values'] = domain_options
            except:
                self.domain_combo['values'] = ["Auto (Best Available)"]
        else:
            self.domain_combo['values'] = ["Auto (Best Available)"]

        # Generate email button
        button_text = "🎲 Generate REAL Email" if REAL_EMAIL_AVAILABLE else "🎲 Generate Temp Email"
        self.generate_email_btn = ttk.Button(gen_frame, text=button_text,
                                           command=self.generate_temp_email, style='Accent.TButton')
        self.generate_email_btn.grid(row=0, column=2, padx=(0, 10), pady=5)

        # Service info button
        self.info_btn = ttk.Button(gen_frame, text="ℹ️ Service Info",
                                 command=self.show_service_info)
        self.info_btn.grid(row=0, column=3, padx=(5, 0), pady=5)

        # Row 1: Email display and Copy button
        ttk.Label(gen_frame, text="Email Address:", font=('Arial', 9, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 5))

        self.email_var = tk.StringVar(value="Click 'Generate Email' to start")
        self.email_entry = ttk.Entry(gen_frame, textvariable=self.email_var,
                                   font=('Arial', 10), state='readonly')
        self.email_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 5))

        # Copy email button
        self.copy_email_btn = ttk.Button(gen_frame, text="📋 Copy Email",
                                       command=self.copy_email_address, state='disabled')
        self.copy_email_btn.grid(row=1, column=3, padx=(5, 0), pady=(10, 5))

        # Row 2: Email status
        self.email_status_var = tk.StringVar(value="Ready to generate email")
        ttk.Label(gen_frame, textvariable=self.email_status_var,
                 font=('Arial', 9), foreground='blue').grid(
            row=2, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))

        # Monitoring Controls Section
        monitor_frame = ttk.LabelFrame(main_frame, text="👁️ Email Monitoring", padding="10")
        monitor_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        monitor_frame.columnconfigure(2, weight=1)

        # Monitoring buttons
        self.start_monitor_btn = ttk.Button(monitor_frame, text="▶️ Start Monitoring",
                                          command=self.start_email_monitoring, state='disabled')
        self.start_monitor_btn.grid(row=0, column=0, padx=(0, 10))

        self.stop_monitor_btn = ttk.Button(monitor_frame, text="⏹️ Stop Monitoring",
                                         command=self.stop_email_monitoring, state='disabled')
        self.stop_monitor_btn.grid(row=0, column=1, padx=(0, 10))

        self.check_now_btn = ttk.Button(monitor_frame, text="🔄 Check Now",
                                      command=self.check_inbox_now, state='disabled')
        self.check_now_btn.grid(row=0, column=2, padx=(0, 10))

        # Monitoring status
        self.monitor_status_var = tk.StringVar(value="Monitoring stopped")
        ttk.Label(monitor_frame, textvariable=self.monitor_status_var,
                 font=('Arial', 9)).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))

        # Verification Codes Section
        codes_frame = ttk.LabelFrame(main_frame, text="🔑 Verification Codes", padding="10")
        codes_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        codes_frame.columnconfigure(1, weight=1)

        # Current verification code display
        ttk.Label(codes_frame, text="Latest Code:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.verification_code_var = tk.StringVar(value="No codes received yet")
        self.code_entry = ttk.Entry(codes_frame, textvariable=self.verification_code_var,
                                  font=('Arial', 14, 'bold'), state='readonly',
                                  foreground='green')
        self.code_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        # Copy code button
        self.copy_code_btn = ttk.Button(codes_frame, text="📋 Copy Code",
                                      command=self.copy_verification_code, state='disabled')
        self.copy_code_btn.grid(row=0, column=2)

        # Code timestamp
        self.code_timestamp_var = tk.StringVar(value="")
        ttk.Label(codes_frame, textvariable=self.code_timestamp_var,
                 font=('Arial', 8), foreground='gray').grid(
            row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))

        # Email Inbox Section
        inbox_frame = ttk.LabelFrame(main_frame, text="📬 Email Inbox", padding="10")
        inbox_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        inbox_frame.columnconfigure(0, weight=1)
        inbox_frame.rowconfigure(0, weight=1)

        # Inbox listbox with scrollbar
        inbox_container = ttk.Frame(inbox_frame)
        inbox_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        inbox_container.columnconfigure(0, weight=1)
        inbox_container.rowconfigure(0, weight=1)

        self.inbox_listbox = tk.Listbox(inbox_container, height=8, font=('Arial', 9))
        self.inbox_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        inbox_scrollbar = ttk.Scrollbar(inbox_container, orient=tk.VERTICAL, command=self.inbox_listbox.yview)
        inbox_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.inbox_listbox.configure(yscrollcommand=inbox_scrollbar.set)

        # Bind double-click to view email
        self.inbox_listbox.bind('<Double-1>', self.view_selected_email)

        # Instructions Section
        instructions_frame = ttk.LabelFrame(main_frame, text="📖 How to Use", padding="10")
        instructions_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))

        instructions_text = """1. Click 'Generate Temp Email' to create a temporary email address
2. Copy the email address and use it to sign up for AugmentCode
3. Click 'Start Monitoring' to watch for verification emails
4. When a verification code arrives, it will appear above
5. Copy the verification code to complete your AugmentCode registration
6. Use the cleanup tools to reset your VS Code data for the next account"""

        ttk.Label(instructions_frame, text=instructions_text,
                 font=('Arial', 9), justify=tk.LEFT).grid(row=0, column=0, sticky=tk.W)
        
    def create_path_row(self, parent, row, label, path):
        """Create a row showing a path with label"""
        ttk.Label(parent, text=label, font=('Arial', 9, 'bold')).grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10))
        
        path_entry = ttk.Entry(parent, font=('Arial', 8))
        path_entry.insert(0, path)
        path_entry.configure(state='readonly')
        path_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=1)
        
    def log_message(self, message):
        """Add a message to the output text area"""
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete(1.0, tk.END)
        
    def start_progress(self):
        """Start the progress bar"""
        self.progress.start(10)
        self.clean_button.configure(state='disabled')
        
    def stop_progress(self):
        """Stop the progress bar"""
        self.progress.stop()
        self.clean_button.configure(state='normal')
        
    def run_in_thread(self, func):
        """Run a function in a separate thread"""
        def wrapper():
            try:
                self.start_progress()
                func()
            except Exception as e:
                self.log_message(f"❌ Error: {str(e)}")
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
            finally:
                self.stop_progress()
        
        thread = threading.Thread(target=wrapper)
        thread.daemon = True
        thread.start()
        
    def modify_ids_only(self):
        """Modify telemetry IDs only"""
        def task():
            self.log_message("🔄 Modifying Telemetry IDs...")
            try:
                result = modify_telemetry_ids()
                self.log_message("✅ Telemetry IDs modified successfully!")
                self.log_message(f"📁 Storage backup: {result['storage_backup_path']}")
                if result['machine_id_backup_path']:
                    self.log_message(f"📁 Machine ID backup: {result['machine_id_backup_path']}")
                self.log_message(f"🔑 New Machine ID: {result['new_machine_id'][:16]}...")
                self.log_message(f"🔑 New Device ID: {result['new_device_id']}")
            except FileNotFoundError as e:
                self.log_message(f"❌ File not found: {e}")
                
        self.run_in_thread(task)
        
    def clean_db_only(self):
        """Clean database only"""
        def task():
            self.log_message("🗃️ Cleaning SQLite Database...")
            try:
                db_result = clean_augment_data()
                self.log_message("✅ Database cleaned successfully!")
                self.log_message(f"📁 Database backup: {db_result['db_backup_path']}")
                self.log_message(f"🗑️ Deleted {db_result['deleted_rows']} rows")
            except FileNotFoundError as e:
                self.log_message(f"❌ Database file not found: {e}")
                
        self.run_in_thread(task)
        
    def clean_workspace_only(self):
        """Clean workspace storage only"""
        def task():
            self.log_message("💾 Cleaning Workspace Storage...")
            try:
                ws_result = clean_workspace_storage()
                self.log_message("✅ Workspace storage cleaned successfully!")
                self.log_message(f"📁 Workspace backup: {ws_result['backup_path']}")
                self.log_message(f"🗑️ Deleted {ws_result['deleted_files_count']} files")
            except FileNotFoundError as e:
                self.log_message(f"❌ Workspace storage not found: {e}")
                
        self.run_in_thread(task)
        
    def clean_all_data(self):
        """Clean all data - main function"""
        def task():
            self.log_message("🚀 Starting complete cleanup process...")
            self.log_message("=" * 50)
            
            try:
                # Step 1: Modify Telemetry IDs
                self.log_message("🔄 Step 1: Modifying Telemetry IDs...")
                result = modify_telemetry_ids()
                self.log_message("✅ Telemetry IDs modified!")
                self.log_message(f"📁 Storage backup: {result['storage_backup_path']}")
                if result['machine_id_backup_path']:
                    self.log_message(f"📁 Machine ID backup: {result['machine_id_backup_path']}")
                
                # Step 2: Clean Database
                self.log_message("\n🗃️ Step 2: Cleaning SQLite Database...")
                db_result = clean_augment_data()
                self.log_message("✅ Database cleaned!")
                self.log_message(f"📁 Database backup: {db_result['db_backup_path']}")
                self.log_message(f"🗑️ Deleted {db_result['deleted_rows']} rows")
                
                # Step 3: Clean Workspace
                self.log_message("\n💾 Step 3: Cleaning Workspace Storage...")
                ws_result = clean_workspace_storage()
                self.log_message("✅ Workspace storage cleaned!")
                self.log_message(f"📁 Workspace backup: {ws_result['backup_path']}")
                self.log_message(f"🗑️ Deleted {ws_result['deleted_files_count']} files")
                
                self.log_message("\n" + "=" * 50)
                self.log_message("🎉 All cleanup tasks completed successfully!")
                self.log_message("📝 You can now restart VS Code and login with a new email.")
                
                messagebox.showinfo("Success", "All cleanup tasks completed successfully!\n\nYou can now restart VS Code and login with a new email.")
                
            except FileNotFoundError as e:
                self.log_message(f"❌ Error: {e}")
                messagebox.showerror("Error", f"File not found: {e}")
            except Exception as e:
                self.log_message(f"❌ Unexpected error: {e}")
                messagebox.showerror("Error", f"An unexpected error occurred: {e}")
                
        self.run_in_thread(task)

    # Temporary Email Methods
    def generate_temp_email(self):
        """Generate a new temporary email address"""
        def task():
            self.email_status_var.set("Generating REAL email...")
            self.generate_email_btn.configure(state='disabled')

            # Get preferred domain from selection
            preferred_domain = None
            domain_selection = self.domain_var.get()
            if domain_selection != "Auto (Best Available)" and self.using_real_service:
                preferred_domain = domain_selection

            if self.using_real_service:
                if preferred_domain:
                    success, message, session = self.temp_email_service.generate_email_with_domain(preferred_domain)
                else:
                    success, message, session = self.temp_email_service.generate_real_email()
            else:
                success, message, session = self.temp_email_service.generate_temp_email()

            if success and session:
                self.email_var.set(session.email_address)

                if self.using_real_service:
                    service_info = f" (via {session.service_name})" if hasattr(session, 'service_name') else ""
                    domain_info = f", domain: {session.domain}" if hasattr(session, 'domain') else ""
                    self.email_status_var.set(f"✅ REAL email generated{service_info}{domain_info}! Expires: {session.expires_at.strftime('%H:%M:%S')}")
                    self.log_message(f"✅ Generated REAL temporary email: {session.email_address}{service_info}{domain_info}")

                    # Show service statistics
                    if hasattr(self.temp_email_service, 'get_service_stats'):
                        stats = self.temp_email_service.get_service_stats()
                        self.log_message(f"📊 Available: {stats['total_services']} services, {stats['total_domains']} domains")
                else:
                    self.email_status_var.set(f"Email generated! Expires: {session.expires_at.strftime('%H:%M:%S')}")
                    self.log_message(f"✅ Generated temporary email: {session.email_address}")

                # Enable buttons
                self.copy_email_btn.configure(state='normal')
                self.start_monitor_btn.configure(state='normal')
                self.check_now_btn.configure(state='normal')

                # Clear previous inbox
                self.inbox_listbox.delete(0, tk.END)
                if self.using_real_service:
                    self.inbox_listbox.insert(0, "📧 REAL inbox ready - waiting for emails...")
                else:
                    self.inbox_listbox.insert(0, "📧 Inbox ready - waiting for emails...")

            else:
                self.email_status_var.set(f"Error: {message}")
                self.log_message(f"❌ Failed to generate email: {message}")

            self.generate_email_btn.configure(state='disabled')

            # Re-enable after a short delay to prevent spam clicking
            self.root.after(2000, lambda: self.generate_email_btn.configure(state='normal'))

        self.run_in_thread(task)

    def copy_email_address(self):
        """Copy the temporary email address to clipboard"""
        try:
            email = self.email_var.get()
            if email and email != "Click 'Generate Temp Email' to start":
                pyperclip.copy(email)
                self.email_status_var.set("📋 Email address copied to clipboard!")
                self.log_message(f"📋 Copied email to clipboard: {email}")

                # Reset status after 3 seconds
                self.root.after(3000, lambda: self.email_status_var.set("Email ready to use"))
        except Exception as e:
            messagebox.showerror("Copy Error", f"Failed to copy email: {str(e)}")

    def start_email_monitoring(self):
        """Start monitoring the temporary email inbox"""
        if self.using_real_service:
            success = self.temp_email_service.start_real_monitoring(poll_interval=10)  # Faster for real emails
        else:
            success = self.temp_email_service.start_monitoring(poll_interval=15)

        if success:
            if self.using_real_service:
                self.monitor_status_var.set("🟢 REAL monitoring active - checking every 10 seconds")
                self.log_message("👁️ Started REAL email monitoring")
            else:
                self.monitor_status_var.set("🟢 Monitoring active - checking every 15 seconds")
                self.log_message("👁️ Started email monitoring")

            self.start_monitor_btn.configure(state='disabled')
            self.stop_monitor_btn.configure(state='normal')
        else:
            messagebox.showerror("Monitor Error", "Failed to start email monitoring")

    def stop_email_monitoring(self):
        """Stop monitoring the temporary email inbox"""
        if self.using_real_service:
            self.temp_email_service.stop_real_monitoring()
        else:
            self.temp_email_service.stop_monitoring()

        self.monitor_status_var.set("🔴 Monitoring stopped")
        self.start_monitor_btn.configure(state='normal')
        self.stop_monitor_btn.configure(state='disabled')
        self.log_message("⏹️ Stopped email monitoring")

    def check_inbox_now(self):
        """Manually check inbox for new messages"""
        def task():
            if self.using_real_service:
                success, message, new_messages = self.temp_email_service.check_real_inbox_manually()
            else:
                success, message, new_messages = self.temp_email_service.check_inbox_manually()

            if success:
                if new_messages:
                    if self.using_real_service:
                        self.log_message(f"📬 Found {len(new_messages)} new REAL message(s)")
                    else:
                        self.log_message(f"📬 Found {len(new_messages)} new message(s)")
                else:
                    self.log_message("📭 No new messages found")
            else:
                self.log_message(f"❌ Error checking inbox: {message}")

        self.run_in_thread(task)

    def copy_verification_code(self):
        """Copy the verification code to clipboard"""
        try:
            code = self.verification_code_var.get()
            if code and code != "No codes received yet":
                pyperclip.copy(code)
                self.code_timestamp_var.set("📋 Code copied to clipboard!")
                self.log_message(f"📋 Copied verification code: {code}")

                # Reset timestamp after 3 seconds
                self.root.after(3000, lambda: self.code_timestamp_var.set(
                    f"Received: {datetime.now().strftime('%H:%M:%S')}"))
        except Exception as e:
            messagebox.showerror("Copy Error", f"Failed to copy code: {str(e)}")

    def view_selected_email(self, event):
        """View the selected email in detail"""
        selection = self.inbox_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if hasattr(self.temp_email_service, 'current_session') and self.temp_email_service.current_session:
            messages = self.temp_email_service.current_session.messages
            if index < len(messages):
                message = messages[index]
                self.show_email_detail(message)

    def show_email_detail(self, message):
        """Show detailed view of an email message"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Email: {message.subject}")
        detail_window.geometry("600x400")

        # Email details
        details_frame = ttk.Frame(detail_window, padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(details_frame, text=f"From: {message.sender}", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(details_frame, text=f"Subject: {message.subject}", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(details_frame, text=f"Time: {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                 font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 10))

        if message.verification_code:
            code_frame = ttk.LabelFrame(details_frame, text="🔑 Verification Code", padding="5")
            code_frame.pack(fill=tk.X, pady=(0, 10))

            code_label = ttk.Label(code_frame, text=message.verification_code,
                                 font=('Arial', 16, 'bold'), foreground='green')
            code_label.pack(side=tk.LEFT)

            ttk.Button(code_frame, text="📋 Copy",
                      command=lambda: pyperclip.copy(message.verification_code)).pack(side=tk.RIGHT)

        # Email content
        ttk.Label(details_frame, text="Content:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)

        content_text = scrolledtext.ScrolledText(details_frame, height=15, wrap=tk.WORD)
        content_text.pack(fill=tk.BOTH, expand=True)
        content_text.insert(tk.END, message.content)
        content_text.configure(state='disabled')

    # Email Service Callbacks
    def on_email_received(self, message):
        """Callback when a new email is received"""
        def update_ui():
            # Add to inbox listbox
            display_text = f"📧 {message.sender}: {message.subject} ({message.timestamp.strftime('%H:%M:%S')})"
            self.inbox_listbox.insert(0, display_text)

            # Remove "waiting for emails" message if present
            if self.inbox_listbox.size() > 1:
                last_item = self.inbox_listbox.get(self.inbox_listbox.size() - 1)
                if "waiting for emails" in last_item:
                    self.inbox_listbox.delete(self.inbox_listbox.size() - 1)

            # Log the email
            self.log_message(f"📬 New email from {message.sender}: {message.subject}")

            # Analyze for verification codes
            analysis = self.verification_parser.analyze_email_for_codes(message.content, message.sender)
            if analysis['has_verification_code']:
                self.log_message(f"🔍 Found verification code with {analysis['best_confidence']:.0%} confidence")

        # Update UI in main thread
        self.root.after(0, update_ui)

    def on_verification_code_found(self, code, message):
        """Callback when a verification code is found"""
        def update_ui():
            self.verification_code_var.set(code)
            self.code_timestamp_var.set(f"Received: {datetime.now().strftime('%H:%M:%S')}")
            self.copy_code_btn.configure(state='normal')

            # Show notification
            self.log_message(f"🎉 Verification code received: {code}")
            messagebox.showinfo("Verification Code",
                              f"New verification code received!\n\nCode: {code}\n\nFrom: {message.sender}")

        self.root.after(0, update_ui)

    def on_temp_email_error(self, error_message):
        """Callback when an error occurs in the email service"""
        def update_ui():
            self.log_message(f"❌ Email service error: {error_message}")

        self.root.after(0, update_ui)

    def on_temp_email_status_change(self, status):
        """Callback when email service status changes"""
        def update_ui():
            self.log_message(f"ℹ️ {status}")

        self.root.after(0, update_ui)

    def show_service_info(self):
        """Show information about available email services and domains"""
        info_window = tk.Toplevel(self.root)
        info_window.title("📊 Email Service Information")
        info_window.geometry("700x500")

        # Main frame
        main_frame = ttk.Frame(info_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="📊 Available Email Services & Domains",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 15))

        if self.using_real_service and hasattr(self.temp_email_service, 'get_service_stats'):
            try:
                stats = self.temp_email_service.get_service_stats()

                # Summary
                summary_frame = ttk.LabelFrame(main_frame, text="📈 Summary", padding="10")
                summary_frame.pack(fill=tk.X, pady=(0, 15))

                summary_text = f"""Total Services: {stats['total_services']}
Total Domains: {stats['total_domains']}
High Reliability Services: {stats['high_reliability_services']}"""

                ttk.Label(summary_frame, text=summary_text, font=('Arial', 10)).pack(anchor=tk.W)

                # Services details
                services_frame = ttk.LabelFrame(main_frame, text="🌐 Available Services", padding="10")
                services_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

                # Create treeview for services
                columns = ('Service', 'Domains', 'Reliability', 'Description')
                tree = ttk.Treeview(services_frame, columns=columns, show='headings', height=10)

                # Define headings
                tree.heading('Service', text='Service')
                tree.heading('Domains', text='Domains')
                tree.heading('Reliability', text='Reliability')
                tree.heading('Description', text='Description')

                # Configure column widths
                tree.column('Service', width=120)
                tree.column('Domains', width=180)
                tree.column('Reliability', width=80)
                tree.column('Description', width=250)

                # Add services data
                for service in stats['services']:
                    domains_str = ', '.join(service['domains'])
                    tree.insert('', tk.END, values=(
                        service['name'],
                        domains_str,
                        service['reliability'].title(),
                        service['description']
                    ))

                tree.pack(fill=tk.BOTH, expand=True)

                # Scrollbar for treeview
                scrollbar = ttk.Scrollbar(services_frame, orient=tk.VERTICAL, command=tree.yview)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                tree.configure(yscrollcommand=scrollbar.set)

                # Domains list
                domains_frame = ttk.LabelFrame(main_frame, text="📧 Available Domains", padding="10")
                domains_frame.pack(fill=tk.X)

                domains_text = ', '.join(stats['available_domains'])
                ttk.Label(domains_frame, text=domains_text, font=('Arial', 9),
                         wraplength=650).pack(anchor=tk.W)

            except Exception as e:
                ttk.Label(main_frame, text=f"Error loading service info: {str(e)}",
                         foreground='red').pack(pady=20)
        else:
            ttk.Label(main_frame, text="Service information not available.\nReal email service may not be loaded.",
                     font=('Arial', 10)).pack(pady=20)

        # Close button
        ttk.Button(main_frame, text="Close", command=info_window.destroy).pack(pady=(15, 0))

    def setup_footer(self):
        """Setup footer with developer information"""
        import webbrowser

        # Create footer frame at the bottom of the main window
        footer_frame = ttk.Frame(self.root)
        footer_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 5))
        footer_frame.columnconfigure(0, weight=1)

        # Developer info with clickable link
        footer_text = "Developed by "
        dev_name = "AhmedElnakieb"

        # Create a frame to hold the footer content
        content_frame = ttk.Frame(footer_frame)
        content_frame.pack()

        # Add the "Developed by" text
        ttk.Label(content_frame, text=footer_text,
                 font=('Arial', 9), foreground='gray').pack(side=tk.LEFT)

        # Add clickable developer name
        dev_label = ttk.Label(content_frame, text=dev_name,
                             font=('Arial', 9, 'underline'),
                             foreground='blue', cursor='hand2')
        dev_label.pack(side=tk.LEFT)

        # Bind click event to open GitHub
        def open_github(event):
            webbrowser.open('https://github.com/RagnarLodbrok2017')

        dev_label.bind('<Button-1>', open_github)

        # Update grid configuration to accommodate footer
        self.root.rowconfigure(1, weight=0)


def main():
    root = tk.Tk()
    app = FreeAugmentCodeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
