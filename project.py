import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import datetime


# Room Class
class Room:
    def __init__(self, room_type, rate, total_rooms, booked_rooms=0):
        self.room_type = room_type
        self.rate = rate
        self.total_rooms = total_rooms
        self.booked_rooms = booked_rooms

    def is_available(self):
        return self.booked_rooms < self.total_rooms

    def book_room(self):
        if self.is_available():
            self.booked_rooms += 1
            return True
        return False

    def available_rooms(self):
        return self.total_rooms - self.booked_rooms

    def get_dynamic_rate(self):
        return self.rate * 1.2 if datetime.datetime.now().month in [12, 1] else self.rate


# Reservation Class
class Reservation:
    def __init__(self, customer_name, email, phone, room, num_nights):
        self.customer_name = customer_name
        self.email = email
        self.phone = phone
        self.room = room
        self.num_nights = num_nights

    def calculate_total(self):
        subtotal = self.num_nights * self.room.get_dynamic_rate()
        if self.room.room_type == "Presidential Suite" and self.num_nights >= 3:
            subtotal -= self.room.get_dynamic_rate()  # Fourth night free
        return subtotal * 1.1  # 10% tax


# Room Manager Class
class RoomManager:
    def __init__(self):
        self.rooms = {
            "Standard Room": Room("Standard Room", 120.0, 2),
            "Deluxe Room": Room("Deluxe Room", 200.0, 3),
            "Ocean View Room": Room("Ocean View Room", 220.0, 2),
            "Family Suite": Room("Family Suite", 250.0, 1),
            "Executive Suite": Room("Executive Suite", 350.0, 2),
            "Presidential Suite": Room("Presidential Suite", 500.0, 1),
        }

    def check_availability(self, room_type):
        return self.get_room(room_type).is_available()

    def book_room(self, room_type):
        return self.get_room(room_type).book_room()

    def get_room(self, room_type):
        return self.rooms.get(room_type)

    def get_booked_rooms(self):
        return {room_type: {"booked": room.booked_rooms, "available": room.available_rooms()} for room_type, room in self.rooms.items()}


# Global Variables
room_manager = RoomManager()
reservations = []


def resize_bg(event):
    """Resize background image to fill the window dynamically."""
    bg_label.configure(image=ImageTk.PhotoImage(bg_image.resize((event.width, event.height), Image.LANCZOS)))


def submit_reservation():
    customer_name, email, phone, room_type, num_nights = name_entry.get(), email_entry.get(), phone_entry.get(), room_type_combobox.get().split(" /")[0], nights_entry.get()

    if not num_nights.isdigit() or int(num_nights) < 1:
        messagebox.showerror("Input Error", "Invalid number of nights. Please enter a positive integer.")
        return

    if room_manager.check_availability(room_type):
        room = room_manager.get_room(room_type)
        reservation = Reservation(customer_name, email, phone, room, int(num_nights))
        room_manager.book_room(room_type)
        reservations.append(reservation)

        booked_rooms_info = room_manager.get_booked_rooms()
        booked_rooms_summary = "\n".join(f"{rt}: {info['booked']} booked, {info['available']} available" for rt, info in booked_rooms_info.items())

        messagebox.showinfo("Reservation Successful",
                            f"Reservation complete!\n\nAvailable Rooms for {room.room_type}: {room.available_rooms()}.\n"
                            f"Total Bill: ${reservation.calculate_total():.2f}\n\nCurrent Room Status:\n{booked_rooms_summary}")
        display_receipt(reservation)
    else:
        messagebox.showwarning("Room Unavailable", f"Selected room type is not available.\nCurrently available: {room_manager.get_room(room_type).available_rooms()} rooms.")
    ask_for_more_reservations()


def display_receipt(reservation):
    """Display the reservation receipt."""
    receipt_window = tk.Toplevel(root)
    receipt_window.title("Reservation Receipt")
    receipt_window.geometry("400x350")
    receipt_window.configure(bg="white")

    receipt_text = (f"--- BeachSide Gateway Resort ---\n"
                    f"Customer Name: {reservation.customer_name}\n"
                    f"Email: {reservation.email}\n"
                    f"Phone: {reservation.phone}\n"
                    f"Room Type: {reservation.room.room_type}\n"
                    f"Nights Stayed: {reservation.num_nights}\n"
                    f"Total Bill: ${reservation.calculate_total():.2f}\n\n"
                    "Thank you for choosing BeachSide Gateway Resort!"
                    )

    tk.Label(receipt_window, text=receipt_text, bg="white", font=("Courier New", 12), justify=tk.LEFT).pack(pady=20)
    tk.Button(receipt_window, text="OK", command=receipt_window.destroy, bg="#4CAF50", fg="white").pack(pady=10)


def ask_for_more_reservations():
    """Ask the user if they want to make another reservation or proceed."""
    if not messagebox.askyesno("Additional Reservations", "Would you like to make another reservation?"):
        generate_cumulative_receipt()
        root.quit()
    clear_fields()


def generate_cumulative_receipt():
    """Generate and display a cumulative receipt."""
    total_amount = sum(reservation.calculate_total() for reservation in reservations)
    receipt_text = "--- BeachSide Gateway Resort ---\n\nTotal Bill Receipt:\n\n"

    for reservation in reservations:
        receipt_text += (f"Name: {reservation.customer_name}\n"
                         f"Room Type: {reservation.room.room_type}\n"
                         f"Nights: {reservation.num_nights}\n"
                         f"Total: ${reservation.calculate_total():.2f}\n\n")
    receipt_text += f"Grand Total: ${total_amount:.2f}"

    messagebox.showinfo("Final Receipt", receipt_text)


def reset_form():
    clear_fields()
    messagebox.showinfo("Reset", "Form has been reset!")


def clear_fields():
    """Clear all input fields."""
    for entry in [name_entry, email_entry, phone_entry, nights_entry]:
        entry.delete(0, tk.END)
    room_type_combobox.set('')


# Main UI
root = tk.Tk()
root.title("BeachSide Gateway Resort Reservation System")
root.geometry("1024x600")

# Load background image
try:
    bg_image = Image.open("assets/looby.jpg").resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except FileNotFoundError:
    print("Error: Image file 'assets/looby.jpg' not found.")
    root.destroy()

# UI Frame
frame = tk.Frame(root, bg="#c8b59e", width=600, bd=5, relief=tk.RAISED)
frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Labels and Inputs
labels = ["Full Name:", "Email:", "Phone Number:", "Room Type:", "Number of Nights:"]
entries = [ttk.Entry(frame, width=30) for _ in labels[:-2]]
room_type_combobox = ttk.Combobox(frame, values=[
    "Standard Room /$120.0 per night",
    "Deluxe Room /$200.0 per night",
    "Ocean View Room /$220.0 per night",
    "Family Suite /$250.0 per night",
    "Executive Suite /$350.0 per night",
    "Presidential Suite /$500.0 per night",
], width=30)
nights_entry = ttk.Entry(frame, width=30)

# Placement
for i, label in enumerate(labels):
    tk.Label(frame, text=label, bg="#c8b59e").grid(row=i, column=0, padx=10, pady=10, sticky='e')
    (entries + [room_type_combobox, nights_entry])[i].grid(row=i, column=1, padx=10, pady=10)

name_entry, email_entry, phone_entry = entries

# Buttons
tk.Button(frame, text="Submit Reservation", command=submit_reservation, bg="#4CAF50", fg="white").grid(row=len(labels) + 1, column=0, pady=10, columnspan=2)
tk.Button(frame, text="Reset Form", command=reset_form, bg="#f44336", fg="white").grid(row=len(labels) + 2, column=0, pady=10, columnspan=2)

root.mainloop()