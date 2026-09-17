# Constants for data consistency 
SST_RATE = 0.08
CLASSES_FILE = "classes.txt"
TRAINERS_FILE = "trainers.txt"
MEMBERS_FILE = "members.txt"
PAYMENTS_FILE = "payments.txt"
BOOKINGS_FILE = "bookings.txt"
STAFF_FILE = "staff.txt"
LOG_FILE = "log.txt"
DELIMITER = "|"

# --- UTILITY FUNCTIONS ---

def read_file(filename):
    # Reads file and returns a list of lines, handling missing files by printing error lines .
    try:
        with open(filename, "r") as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        # Create file if it doesn't exist
        open(filename, "a").close()
        return []

def write_file(filename, data_list):
    """Writes a list of strings to the specified file."""
    try:
        with open(filename, "w") as f:
            for item in data_list:
                f.write(item + "\n")
    except IOError:
        print(f"Error: Could not write to {filename}")


def generate_id(file_name, prefix):
    try:
        f = open(file_name, "r")
        lines = f.readlines()
        f.close()
        return prefix + str(len(lines) + 1001)
    except FileNotFoundError:
        return prefix + "1001"

def save_to_file(file_name, data_list):
    try:
        f = open(file_name, "a")
        line = ""
        for i in range(len(data_list)):
            line += str(data_list[i])
            if i < len(data_list) - 1:
                line += DELIMITER
        f.write(line + "\n")
        f.close()
    except Exception as e:
        print(" Error saving to file.")

def get_member_name(member_id):
    try:
        f = open(MEMBERS_FILE, "r")
        for line in f:
            data = line.strip().split(DELIMITER)
            if data and data[0] == member_id:
                f.close()
                return data[1]
        f.close()
    except FileNotFoundError:
        pass
    return None

def display_all_member_ids():
    print("\n--- Registered Member List ---")
    try:
        f = open(MEMBERS_FILE, "r")
        lines = f.readlines()
        f.close()
        
        if not lines:
            print("No members found in the system.")
            return

        print(format("ID", "10s"), "Name")
        print("-" * 30)
        for line in lines:
            data = line.strip().split(DELIMITER)
            if len(data) >= 2:
                print(format(data[0], "10s"), data[1])
        print("-" * 30)
    except FileNotFoundError:
        print(" Error: Member file not found.")


def verify_login(required_role):
    """
    Prompts for email/password and checks in staff.txt
    """
    print(f"\n--- {required_role.upper()} LOGIN ---")
    email_input = input("Enter Email: ").strip().lower()
    password_input = input("Enter Password: ").strip()

    try:
        # Load credentials
        credentials = read_file("staff.txt")
        
        for entry in credentials:
            try:
                # split and unpack the line
                role, email, password = entry.split(DELIMITER)
                
                if role.lower() == required_role.lower():
                    if email.lower() == email_input and password == password_input:
                        print("Login successful!")
                        return True
            except ValueError:
                # Handles cases where a line doesn't have exactly 3 parts
                # Log malformed lines for admin review
                log = read_file(LOG_FILE)
                log.append(f"Log (ADMIN): Malformed staff.txt line skipped: '{entry}'")
                write_file(LOG_FILE, log)
                continue

    except FileNotFoundError:
        print("Error: The credentials file 'staff.txt' could not be found.")
    except Exception as e:
        print("An unexpected error occurred during login. Please contact support.")
        # Log the exception details for debugging
        log = read_file(LOG_FILE)
        log.append(f"Log (LOGIN ERROR): {str(e)}")
        write_file(LOG_FILE, log)
        
    if not credentials:
        print("No staff credentials found or the file is empty/corrupted.")
    else:
        print("Invalid email or password.")
    return False

# Accountant section

def update_member_status(member_id, new_status="Paid"):
    try:
        # Read all current members
        lines = read_file(MEMBERS_FILE)
        updated_lines = []
        found = False

        for line in lines:
            data = line.strip().split(DELIMITER)
            # Check if this is the member we are looking for
            if data and data[0] == member_id:
                # Update status ( format: ID|Name|Status)
                if len(data) >= 3:
                    data[2] = new_status
                else:
                    # If status didn't exist, append it
                    data.append(new_status)
                
                updated_lines.append(DELIMITER.join(data))
                found = True
            else:
                updated_lines.append(line)

        if found:
            write_file(MEMBERS_FILE, updated_lines)
                # Logging
            log = read_file(LOG_FILE)
            log.append(f"Log (ACCOUNTANT): updated payment status for {member_id} from unpaid to {new_status}")
            write_file(LOG_FILE, log)
            return True
        return False
    except Exception as e:
        print(f" Error updating member status: {e}")
        return False


def process_payment():
    print("\n--- Record Membership Payment ---")
    
    show_list = input("Do you want to see the list of Member IDs first? (y/n): ").strip().lower()
    if show_list == 'y':
        display_all_member_ids()

    member_id = input("\nEnter Member ID (e.g., MB101): ").strip().upper()
    member_name = get_member_name(member_id)
    
    if member_name is None:
        print(" Error: Member ID [" + member_id + "] does not exist.")
        return

    print("Found Member: " + member_name)
    print("\nSelect Membership Plan:")
    print("1. Basic    (RM130)")
    print("2. Standard (RM150)")
    print("3. Premium  (RM195)")
    plan_choice = input("Choice (1-3): ")
    
    plan_name = ""
    amount = 0.0
    
    if plan_choice == "1":
        plan_name, amount = "Basic", 130.0
    elif plan_choice == "2":
        plan_name, amount = "Standard", 150.0
    elif plan_choice == "3":
        plan_name, amount = "Premium", 195.0
    else:
        print(" Invalid plan selection.")
        return

    print("\nEnter Payment Date")
    day = input("Day (DD): ")
    month = input("Month (MM): ")
    year = input("Year (YYYY): ")
    date_str = day + "/" + month + "/" + year
    
    tax = amount * SST_RATE
    total = amount + tax
    
    payment_id = generate_id(PAYMENTS_FILE, "PAY")
    payment_data = [payment_id, member_id, plan_name, total, date_str]
    save_to_file(PAYMENTS_FILE, payment_data)
    
    if update_member_status(member_id, "Paid"):
        print(f" Status for {member_id} updated to PAID.")
    
    print("\n Payment Recorded Successfully!")
    print("Receipt ID: " + payment_id)
    print("Total Amount (inc. 8% SST): RM" + format(total, ".2f"))

    # Logging
    log = read_file(LOG_FILE)
    log.append(f"Log (ACCOUNTANT): Payment {payment_id} recorded for Member {member_id}")
    write_file(LOG_FILE, log)


def generate_income_report():
    print("\n--- Revenue Summary ---")
    
    payments = read_file(PAYMENTS_FILE)
    
    if not payments:
        print("No payment records found.")
        return

    total_revenue = 0.0
    transaction_count = 0

    for record in payments:
        data = record.split(DELIMITER)
        # Payment format: PAY1001|MB101|Basic|140.40|23/04/2026
        if len(data) >= 4:
            try:
                total_revenue += float(data[3])
                transaction_count += 1
            except ValueError:
                continue # Skip lines with corrupted numerical data


    net_income = total_revenue / (1 + SST_RATE)
    total_tax = total_revenue - net_income

    print(f"Total Transactions : {transaction_count}")
    print(f"Net Income         : RM{format(net_income, '.2f')}")
    print(f"Total SST (8%)     : RM{format(total_tax, '.2f')}")
    print(f"GRAND TOTAL        : RM{format(total_revenue, '.2f')}")

    # Logging
    new_log = f"Log (ACCOUNTANT): Revenue calculated. Total: RM{total_revenue:.2f}"
    log = read_file(LOG_FILE)
    log.append(new_log)
    write_file(LOG_FILE, log)

def generate_unpaid_report():
    print("\n--- Unpaid Memberships Report ---")
    all_members = []
    try:
        with open(MEMBERS_FILE, "r") as f:
            for line in f:
                data = line.strip().split(DELIMITER)
                if len(data) >= 2:
                    all_members.append((data[0], data[1]))
    except FileNotFoundError:
        print(" Error: Member file not found.")
        return

    paid_ids = []
    try:
        with open(PAYMENTS_FILE, "r") as f:
            for line in f:
                data = line.strip().split(DELIMITER)
                if len(data) >= 2:
                    paid_ids.append(data[1])
    except FileNotFoundError:
        pass

    unpaid_count = 0
    for m_id, m_name in all_members:
        if m_id not in paid_ids:
            print("Member ID: " + m_id + " | Name: " + m_name)
            unpaid_count += 1

    print("\nTotal Unpaid Members: " + str(unpaid_count))

    # Logging
    log = read_file(LOG_FILE)
    log.append("Log (ACCOUNTANT): Unpaid memberships report generated")
    write_file(LOG_FILE, log)


def analyze_package():
    print("\n" + "="*50)
    print("      FIT ZONE GYM: PACKAGE SELECTION ANALYSIS")
    print("="*50)

    counts = {"Basic": 0, "Standard": 0, "Premium": 0}
    total_sales = 0

    try:
        f = open(PAYMENTS_FILE, "r")
        for line in f:
            data = line.strip().split(DELIMITER)
            if len(data) >= 4: # Adjusted to match your save_to_file format
                plan_name = data[2]
                if plan_name in counts:
                    counts[plan_name] += 1
                    total_sales += 1
        f.close()
    
        if total_sales == 0:
            print("No sales data found to analyze.")
            return
        
        print(format("Package", "15s"), format("Count", "10s"), "Percentage")
        print("-" * 50)
        
        most_popular, highest_count = "", -1
        for package, count in counts.items():
            percentage = (count / total_sales) * 100
            print(format(package, "15s"), format(str(count), "10s"), format(percentage, ".2f") + "%")
            if count > highest_count:
                highest_count, most_popular = count, package

        print("-" * 50)
        print("Total Subscriptions: " + str(total_sales))
        print("Most Popular Package: " + most_popular)
        print("="*50)

        # Logging
        log = read_file(LOG_FILE)
        log.append("Log (ACCOUNTANT): Package selection analysis generated")
        write_file(LOG_FILE, log)

    except FileNotFoundError:
        print(" Error: Payment file not found.")


# --- BOOKING SECTION --- 

def add_new_member():
    print("\n--- Register New Member ---")
    members = read_file(MEMBERS_FILE)
    new_id = "MB" + str(100 + len(members) + 1)
    name = ""
    while name == "":
        name = input("Enter member's full name: ").strip()
        if name == "":
            print("Name cannot be empty. Please try again.")
    new_member = new_id + DELIMITER + name + DELIMITER + "Unpaid"
    members.append(new_member)
    write_file(MEMBERS_FILE, members)
    print("Member registered successfully!")
    print("Member ID is: " + new_id)

    # Logging
    log = read_file(LOG_FILE)
    log.append("Log (USER): New member registered: " + new_id)
    write_file(LOG_FILE, log)

def show_gym_classes():
    print("\n--- Available Gym Classes ---")
    classes = read_file(CLASSES_FILE)
    if len(classes) == 0:
        print("No classes available at the moment.")
    else:
        for gym_class in classes:
            print(gym_class.replace(DELIMITER, " | "))
    
    # Logging
    log = read_file(LOG_FILE)
    log.append("Log (USER): Available gym classes viewed")
    write_file(LOG_FILE, log)

def book_a_class():
    print("\n--- Book a Class ---")

    member_id = input("Enter your Member ID: ").strip().upper()
    class_id = input("Enter the Class ID: ").strip().upper()
    day = input("Enter the day (Mon - Fri): ").strip().capitalize()

    print("Available shifts:")
    print("  S1 = 10:30am to 12:30pm")
    print("  S2 =  2:30pm to  4:30pm")
    shift = input("Choose a shift (S1 or S2): ").strip().upper()

    if shift == "S1":
        time_slot = "10:30-12:30"
    else:
        time_slot = "14:30-16:30"
    bookings = read_file(BOOKINGS_FILE)
    new_booking = (member_id + DELIMITER + class_id + DELIMITER + day + DELIMITER + shift + DELIMITER + time_slot )
    bookings.append(new_booking)
    write_file(BOOKINGS_FILE, bookings)

    print("Booking saved successfully!")

    # Logging
    log = read_file(LOG_FILE)
    log.append("Log (USER): Class " + class_id + " booked for Member " + member_id)
    write_file(LOG_FILE, log)

def manage_existing_bookings():
    print("\n--- Edit or Cancel a Booking ---")
    member_id = input("Enter your Member ID: ").strip().upper()
    all_bookings = read_file(BOOKINGS_FILE)
    updated_bookings = []
    found = False
    action_taken = "None"

    for booking in all_bookings:
        details = booking.split(DELIMITER)
        if details[0] == member_id:
            found = True
            print("\nBooking found:")
            print("  " + booking.replace(DELIMITER, " | "))
            print("\nWhat would you like to do?")
            print("  1. Reschedule")
            print("  2. Cancel booking")
            print("  3. Keep as is")
            choice = input("Your choice: ").strip()
            if choice == "1":
                new_day = input("Enter new day: ").strip().capitalize()
                new_shift = input("Enter new shift (S1 or S2): ").strip().upper()

                if new_shift == "S1":
                    new_time = "10:30-12:30"
                else:
                    new_time = "14:30-16:30"

                if len(details) > 5:
                    pay_status = details[5]
                else:
                    pay_status = "Unpaid"
                updated = (member_id + DELIMITER + details[1] + DELIMITER + new_day + DELIMITER + new_shift + DELIMITER + new_time + DELIMITER + pay_status)
                updated_bookings.append(updated)
                print("Booking rescheduled successfully!")
                action_taken = "Rescheduled"
            elif choice == "2":
                print("Booking has been cancelled.")
                action_taken = "Cancelled"
                # Record skipped, so it's removed
            else:
                updated_bookings.append(booking)
                print("No changes made.")
        else:
            updated_bookings.append(booking)
    
    if found == False:
        print("No booking found for Member ID: " + member_id)
    else:
        write_file(BOOKINGS_FILE, updated_bookings)
        
        # Logging
        log = read_file(LOG_FILE)
        log.append("Log (USER): Booking management performed by " + member_id + " - Action: " + action_taken)
        write_file(LOG_FILE, log)



#booking menu

def booking_menu():
    while True:
        print("\n==============================")
        print("     BOOKING OFFICER BACKEND SYSTEM    ")
        print("==============================")
        print("1. Register New Member")
        print("2. View Gym Classes")
        print("3. Book a Class")
        print("4. Edit or Cancel Booking")
        print("5. Logout")
        print("==============================")
        choice = input("Enter your choice (1-6): ").strip()
        if choice == "1":
            add_new_member()
        elif choice == "2":
            show_gym_classes()
        elif choice == "3":
            book_a_class()
        elif choice == "4":
            manage_existing_bookings()
        elif choice == "5":
            print("Logging out. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")


# --- MAIN ACCOUNTING MENU ---
def accountant_menu():
    while True:
        print("\n--- FITZONE GYM: ACCOUNTING DEPARTMENT ---")
        print("1. Process New Payment")
        print("2. View Registered Member IDs")
        print("3. Generate Income & SST Report")
        print("4. Unpaid Memberships Report")
        print("5. Analyze Package Selection")
        print("6. Exit System")
        
        choice = input("\nSelect an option (1-6): ")

        if choice == "1":
            process_payment()
        elif choice == "2":
            display_all_member_ids()
        elif choice == "3":
            generate_income_report()
        elif choice == "4":
            generate_unpaid_report()
        elif choice == "5":
            analyze_package()
        elif choice == "6":
            print("Exiting accounting system. Goodbye!")
            break
        else:
            print(" Invalid choice. Please select (1-6).")


# ---------- User Menu Implementation ----------
def user_menu():
    while True:
        print("\n===== User Menu =====")
        print("1. View Available Classes")
        print("2. Book a Class")
        print("3. Cancel a Class")
        print("4. View History")
        print("5. Logout")
        choice = input("Select an option: ")
        if choice == '1':
            view_classes()
        elif choice == '2':
            # This function is defined in the Booking Officer section.
            book_a_class()
        elif choice == '3':
            cancel_class()
        elif choice == '4':
            view_member_history()
        elif choice == '5':
            print("Logging out.....Bye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")
        while True:
            back = input("\nReturn to User Menu? (Y/N): ").strip().upper()
            if back == "Y":
                break
            elif back == "N":
                print("Logging out.....Bye!")
                return
            else:
                print("Invalid input. Please enter Y or N only.")


# --- Core Gym Member Functions ---
def view_classes():
    print("\n--- Available Classes ---")
    try:
        with open("classes.txt", "r") as file:
            content = file.readlines()
            if not content:
                print("No classes are currently scheduled.")
                return
            print(f"\n{'Class ID':<6} | {'Class':<15} | {'Trainer':<10}")
            print("-" * 45)
            for line in content:    # Skip any empty lines to avoid IndexErrors
                if not line.strip():
                    continue
                details = line.strip().split("|")   # Check if the line actually has 3 parts before printing
                if len(details) == 3:
                    print(f"{details[0]:<8} | {details[1]:<15} | {details[2]:<10}")
                else:
                    print(f"Error: Skipping badly formatted line: {line.strip()}")
    except FileNotFoundError:
        print("Error: classes.txt not found. Please create the file first.")


def cancel_class():
    print("\n--- Cancel Class Booking ---")
    member_id = input("\nEnter your Member ID: ").strip().upper()
    if member_id == "":
        print("Member ID cannot be empty.")
        return
    class_id = input("Enter the Class ID to cancel: ").strip().upper()
    if class_id == "":
        print("Class ID cannot be empty.")
        return
    remaining_bookings = []
    found = False
    try:
        with open("bookings.txt", "r") as f:
            for line in f:
                details = line.strip().split("|")
                # Check if this line matches the Member AND the Class
                if details[0] == member_id and details[1] == class_id:
                    found = True
                    # We skip adding this to remaining_bookings (effectively deleting it)
                    continue
                remaining_bookings.append(line)
        if not found:
            print(f"No booking found for {member_id} in class {class_id}.")
            return
        # Write the remaining bookings back to the file
        with open("bookings.txt", "w") as f:
            for booking in remaining_bookings:
                f.write(booking)
        print(f"Booking for {class_id} has been cancelled.")
    except FileNotFoundError:
        print("Error: bookings.txt not found. Please create the file first.")



# ----- member history menu -----
def view_member_history():
    while True:
        print("\n--- Member History ---")
        print("1. Booking History")
        print("2. Payments History")
        print("3. Return to user menu")
        choice = input("Select an option: ")
        if choice == '1':
            booking_history()
        elif choice == '2':
            payment_history()
        elif choice == '3':
            print("Returning to User Menu.....")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 3.")


def booking_history():
    member_id = input("\nEnter your Member ID: ").strip().upper()
    if member_id == "":
        print("Member ID cannot be empty.")
        return
    found = False
    try:
        with open("bookings.txt", "r") as f:
            for line in f:
                details = line.strip().split("|")
                if details[0] == member_id:
                    if not found:
                        print(f"\n--- Booking History for {member_id} ---")
                        print(f"{'Class':<8} | {'Day':<5} | {'Shift':<5} | {'Time':<12}")
                        print("-" * 45)
                        found = True
                    print(f"{details[1]:<8} | {details[2]:<5} | {details[3]:<5} | {details[4]:<12}")
        if not found:
            print(f"\nNo booking found for {member_id}.")
    except FileNotFoundError:
        print("Error: bookings.txt not found.")


def payment_history():
    member_id = input("\nEnter Member ID to check payments: ").strip().upper()
    if member_id == "":
        print("Member ID cannot be empty.")
        return
    found = False
    total_spent = 0.0
    try:
        with open("payments.txt", "r") as f:
            for line in f:
                details = line.strip().split("|")
                if len(details) == 5 and details[1] == member_id:
                    if not found:
                        print(f"\n--- Payment History for {member_id} ---")
                        print(f"{'Pay ID':<10} | {'Type':<12} | {'Amount':<10} | {'Date':<12}")
                        print("-" * 52)
                        found = True
                    print(f"{details[0]:<10} | {details[2]:<12} | {details[3]:<10} | {details[4]:<12}")
                    total_spent += float(details[3])
        if found:
            print("-" * 52)
            print(f"Total Amount Paid: RM {total_spent:.2f}")
        else:
            print(f"\nNo payment records found for {member_id}.")
    except FileNotFoundError:
        print("Error: payments.txt not found.")
    except ValueError:
        print("Error: Could not calculate total due to invalid amount format.")


#! --- ADMIN FUNCTIONS ---
 
#! --- CLASSES section ---

def add_Class():
    c_id = input("Enter Class ID: ")
    c_name = input("Enter Class Name: ")
    c_trainer = input("Enter Trainer Name: ")
    
    # Formatting the record
    new_class = f"{c_id}{DELIMITER}{c_name}{DELIMITER}{c_trainer}"
    
    # Load existing, add new, save back
    data = read_file(CLASSES_FILE)
    data.append(new_class)
    write_file(CLASSES_FILE, data)
    print("Class saved successfully!")

    # Logging
    new_log = f"Log (ADMIN) : class {c_id} was add to the classes file  "
    log = read_file(LOG_FILE)
    log.append(new_log)
    write_file(LOG_FILE,log)
    
# ? delete class function 
def delete_class():
    print("\n--- Delete a Class ---")
    # 1. Ask for the ID to delete
    target_id = input("Enter the Class ID you want to remove: ").strip().upper()
    
    # 2. Load the current data into memory
    all_classes = read_file(CLASSES_FILE)
    # 3. Create a new list to hold everything EXCEPT the target
    updated_list = []
    found = False
    
    for record in all_classes:
        # Split the record into its parts
        # record will look like: "C101|Yoga|John"
        fields = record.split(DELIMITER)
        
        # Check if the ID (index 0) matches the target
        if fields[0].strip().upper() == target_id:
            found = True
            print(f"Record found: {fields[1]} with Trainer {fields[2]}")
            confirm = input("Are you sure you want to delete this? (y/n): ").lower()
            
            if confirm == 'y':
                print("Skipping this record (deleting)...")
                continue # Do NOT add this to updated_list
            else:
                print("Deletion cancelled for this record.")
                updated_list.append(record)
        else:
            # If it's not the target, keep it in the list
            updated_list.append(record)
            
    # 4. Finalize the changes
    if found:
        write_file(CLASSES_FILE, updated_list)
        print("File updated successfully.")

        # Logging
        new_log = f"Log (ADMIN) : class {target_id} was deleted from the classes file  "
        log = read_file(LOG_FILE)
        log.append(new_log)
        write_file(LOG_FILE,log)
    else:
        print(f"Error: No class found with ID '{target_id}'.")


def update_class():
    print("\n--- Update a Class ---")
    # 1. Ask for the ID to delete
    target_id = input("Enter the Class ID you want to remove: ").strip().upper()
    
    # 2. Load the current data into memory
    all_classes = read_file(CLASSES_FILE)
    # 3. Create a new list to hold everything EXCEPT the target
    updated_list = []
    found = False
    
    for record in all_classes:
        # Split the record into its parts
        # record will look like: "C101|Yoga|John"
        fields = record.split(DELIMITER)
        
        # Check if the ID (index 0) matches the target
        if fields[0].strip().upper() == target_id:
            found = True
            found_field = f"Record found: {fields[1]} with Trainer {fields[2]}"
            print(found_field)
            confirm = input("Are you sure you want to update this? (y/n): ").lower()
            
            if confirm == 'y':
                print("updating this record ...")
                updated_c_id = input("Enter new Class ID: ")
                updated_c_name = input("Enter new Class Name: ")
                updated_c_trainer = input("Enter new Trainer Name: ")

                # Formatting the record
                update_class_record = f"{updated_c_id}{DELIMITER}{updated_c_name}{DELIMITER}{updated_c_trainer}"
                print(update_class_record)
                updated_list.append(update_class_record)

            else:
                print("updating cancelled for this record.")
                updated_list.append(record)

                # Logging 
                new_log = f"Log (ADMIN) : class {target_id} was updated from the classes file from {found_field} to {update_class_record} "                
                log = read_file(LOG_FILE)
                log.append(new_log)
                write_file(LOG_FILE,log)

        else:
            # If it's not the target, keep it in the list
            updated_list.append(record)
            
    # 4. Finalize the changes
    if found:
        write_file(CLASSES_FILE, updated_list)
        print("File updated successfully.")
    else:
        print(f"Error: No class found with ID '{target_id}'.")


#! --- TRAINERS FUNCTIONS --- 

def add_trainer():
    t_id = input("Enter Trainer ID: ")
    t_name = input("Enter Trainer Name: ")
    
    # Formatting the record
    new_trainer = f"{t_id}{DELIMITER}{t_name}"
    
    # Load existing, add new, save back
    data = read_file(TRAINERS_FILE)
    data.append(new_trainer)
    print(data)
    write_file(TRAINERS_FILE, data)
    print("trainer saved successfully!")

    # Logging
    new_log = f"Log (ADMIN) : Trainer {t_id} was add to the trainers file  "
    log = read_file(LOG_FILE)
    log.append(new_log)
    write_file(LOG_FILE,log)


def delete_trainer():
    print("\n--- Delete a Trainer ---")
    # 1. Ask for the ID to delete
    target_id = input("Enter the Trainer ID you want to remove: ").strip().upper()
    
    # 2. Load the current data into memory
    all_trainer = read_file(TRAINERS_FILE)
    # 3. Create a new list to hold everything EXCEPT the target
    updated_list = []
    found = False
    
    for record in all_trainer:
        # Split the record into its parts
        # record will look like: "C101|Yoga|John"
        fields = record.split(DELIMITER)
        
        # Check if the ID (index 0) matches the target
        if fields[0].strip().upper() == target_id:
            found = True
            print(f"trainer found: {fields[1]}")
            confirm = input("Are you sure you want to delete this? (y/n): ").lower()
            
            if confirm == 'y':
                print("Skipping this record (deleting)...")
                continue # Do NOT add this to updated_list
            else:
                print("Deletion cancelled for this record.")
                updated_list.append(record)
        else:
            # If it's not the target, keep it in the list
            updated_list.append(record)
            
    # 4. Finalize the changes
    if found:
        write_file(TRAINERS_FILE, updated_list)
        print("File updated successfully.")

        # Logging
        new_log = f"Log (ADMIN) : class {target_id} was deleted from the classes file  "
        log = read_file(LOG_FILE)
        log.append(new_log)
        write_file(LOG_FILE,log)
    else:
        print(f"Error: No trainer found with ID '{target_id}'.")


def update_trainer():
    print("\n--- Update a Trainer ---")
    # 1. Ask for the ID to delete
    target_id = input("Enter the trainer ID you want to remove: ").strip().upper()
    
    # 2. Load the current data into memory
    all_trainers = read_file(TRAINERS_FILE)
    # 3. Create a new list to hold everything EXCEPT the target
    updated_list = []
    found = False
    
    for record in all_trainers:
        # Split the record into its parts
        # record will look like: "TR001|John"
        fields = record.split(DELIMITER)
        
        # Check if the ID (index 0) matches the target
        if fields[0].strip().upper() == target_id:
            found = True
            found_field = f"Record found:  Trainer {fields[2]}"
            print(found_field)
            confirm = input("Are you sure you want to update this? (y/n): ").lower()
            
            if confirm == 'y':
                print("updating this record ...")
                updated_t_id = input("Enter new Class ID: ")
                updated_t_name = input("Enter new Class Name: ")
                updated_t_trainer = input("Enter new Trainer Name: ")

                # Formatting the record
                update_trainer_record = f"{updated_t_id}{DELIMITER}{updated_t_name}{DELIMITER}{updated_t_trainer}"

                
                # Logging 
                new_log = f"Log (ADMIN) : class {target_id} was updated from the classes file from {found_field} to {update_trainer_record} "                
                log = read_file(LOG_FILE)
                log.append(new_log)
                write_file(LOG_FILE,log)

                updated_list.append(update_trainer_record)

            else:
                print("updating cancelled for this record.")
                updated_list.append(record)
        else:
            # If it's not the target, keep it in the list
            updated_list.append(record)
            
    # 4. Finalize the changes
    if found:
        write_file(TRAINERS_FILE, updated_list)
        print("File updated successfully.")
    else:
        print(f"Error: No trainer found with ID '{target_id}'.")


#! --- VIEW SECTION ---
def view_classes():
    with open(CLASSES_FILE, "r") as file:
        lines = file.readlines()
        for line in lines:
            out = line.split(DELIMITER)
            print(out[0] + " with name " + out[1] + " and the trainer " + out[2]) 
            
            new_log = f"Log (ADMIN) : Classes file printed to view"
            log = read_file(LOG_FILE)
            log.append(new_log)
            write_file(LOG_FILE,log)

                        
def view_members():
    with open(MEMBERS_FILE, "r") as file:
        lines = file.readlines()
        for line in lines:
            out = line.split(DELIMITER)
            print(out[0] + " with name " + out[1] + " and the payment status " + out[2]) 
            new_log = f"Log (ADMIN) : members file printed to view"
            log = read_file(LOG_FILE)
            log.append(new_log)
            write_file(LOG_FILE,log)

def view_booking():
    with open(BOOKINGS_FILE, "r") as file:
        lines = file.readlines()
        for line in lines:
            booking_out = line.split(DELIMITER)
            print(f"ID : "+ booking_out[0] + " , with class id: " + booking_out[1] + " on day "+ booking_out[2] + " ,Shift No: " + booking_out[3] + " time : " + booking_out[4]) 
            new_log = f"Log (ADMIN) : booking file printed to view"
            log = read_file(LOG_FILE)
            log.append(new_log)
            write_file(LOG_FILE,log)

def view_payments():
    with open(PAYMENTS_FILE, "r") as file:
        lines = file.readlines()
        for line in lines:
            payment_out = line.split(DELIMITER)
            print(f"Payment ID : "+ payment_out[0] + " , user id: " + payment_out[1] + " subscription type: "+ payment_out[2] + " ,price: " + payment_out[3] + " time : " + payment_out[4]) 
            # logging 
            new_log = f"Log (ADMIN) : payment file printed to view"
            log = read_file(LOG_FILE)
            log.append(new_log)
            write_file(LOG_FILE,log)

#! --- GENERATE REPORT ---


def count_members():
    member_count = len(read_file(MEMBERS_FILE))
    print(f"the total number of members is {member_count}")

    # logging
    new_log = f"Log (ADMIN) : number of members printed to view"
    log = read_file(LOG_FILE)
    log.append(new_log)
    write_file(LOG_FILE,log)

def class_usage():
    print("\n--- Class Usage Report ---")
    
    # 1. Load data once into memory
    bookings = read_file(BOOKINGS_FILE)
    classes_data = read_file(CLASSES_FILE)
    
    if not bookings:
        print("No data found in bookings.")
        return

    # 2. Build Class ID -> Name map in one pass

    class_map = {}
    for entry in classes_data:
        parts = entry.split(DELIMITER)
        if len(parts) >= 2:
            class_map[parts[0]] = parts[1]

    # 3. Count bookings in one pass
    counts = {}
    for line in bookings:
        parts = line.split(DELIMITER)
        if len(parts) >= 2:
            c_id = parts[1]
            if c_id in counts:
                counts[c_id] += 1
            else:
                counts[c_id] = 1

    # 4. Print results and log
    print(f"{'ID':<8} | {'Bookings'}")
    print("-" * 40)
    
    for c_id, total in counts.items():
        name = class_map.get(c_id)
        print(f"{c_id:<8} | {total}")

    # Logging 
    log = read_file(LOG_FILE)
    log.append(f"Log (ADMIN): Class usage report generated. Total bookings: {len(bookings)}")
    write_file(LOG_FILE, log)



def calculate_revenue():
    generate_income_report()
    generate_unpaid_report()
    

#! --- ADMIN MENU ---


def admin_menu():
    while True:
        print("\n=== System Administrator Menu ===")
        print("1. Add/Update/Remove Classes")
        print("2. Add/Update/Remove Trainers")
        print("3. View All Data (Members, Bookings, Payments)")
        print("4. Generate System Report")
        print("5. Return to Main Menu")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            manage_classes()
        elif choice == '2':
            manage_trainers()
        elif choice == '3':
            view_all_system_data()
        elif choice == '4':
            generate_report()
        elif choice == '5':
            break
        else:
            print("Invalid choice.")


def manage_classes():
    print("\n--- Manage Classes ---")
    print("1. Add Class")
    print("2. Delete Class")
    print("3. Update Classes")
    print("4. Exit")
    
    choice = input("Choice: ")
    if choice == '1':
        add_Class()
    elif choice == '2':
        delete_class()
    elif choice == '3':
        update_class() 
    elif choice == '4':
        admin_menu()
    else:
        print("Invalid choice.")


def manage_trainers():
    print("\n--- Manage Classes ---")
    print("1. Add trainer")
    print("2. Delete trainer")
    print("3. update trainers")
    print("4. exit")
    
    choice = input("Choice: ")
    if choice == '1':
        add_trainer()
    if choice == '2':
        delete_trainer()
    if choice == '3':
        update_trainer() 
    elif choice == '4':
        admin_menu()
    else:
        print("Invalid choice.")

def view_all_system_data():
    print("\n--- view system data ---")
    print("1. view bookings")
    print("2. view classes")
    print("3. view payments")
    print("5. view members")
    print("5. exit")
    
    choice = input("Choice: ")
    if choice == '1':
        view_booking()
    if choice == '2':
        view_classes()
    if choice == '3':
        view_payments()
    elif choice == '4':
        view_members()
    elif choice == '5':
        admin_menu()
    else:
        print("Invalid choice.")

def generate_report():
    print("\n--- generate report ---")
    print("1. Member count")
    print("2. class usage")
    print("3. revenue calculation")
    print("4. Exit")
    
    choice = input("Choice: ")
    if choice == '1':
        count_members()
    elif choice == '2':
        class_usage()
    elif choice == '3':
        calculate_revenue() 
    elif choice == '4':
        admin_menu()
    else:
        print("Invalid choice.")



# --- main loop --- 


def main_menu():
    while True:
        print("\n--- Main Menu ---")
        print("\nplease select the menu you want to access")
        print("1. admin menu ")
        print("2. Booking menu ")
        print("3. Accountant menu ")
        print("4. User menu ")
        print("5. Exit")
        
        choice = input("Enter choice (1-5): ")

        if choice == '1':
            if verify_login("admin"):
                admin_menu()          
        elif choice == '2':
            if verify_login("booking"):
                booking_menu()   
        elif choice == '3':
            if verify_login("accountant"):
                accountant_menu() 
        elif choice == '4' :
            if verify_login("member"):
                user_menu()
        elif choice == '5' :
            print("exiting the system")
            break
        else:
            print("Invalid choice. Please choose again.")


if __name__ == "__main__":
    main_menu()