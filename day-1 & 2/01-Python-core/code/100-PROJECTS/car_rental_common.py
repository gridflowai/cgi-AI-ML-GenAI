import random
from datetime import datetime, timedelta
from tabulate import tabulate

car_types = {
    'COMPACT': {'hourly': 10, 'daily': 50, 'weekly': 125},
    'SDN': {'hourly': 15, 'daily': 75, 'weekly': 150},
    'MUV': {'hourly': 25, 'daily': 100, 'weekly': 150},
    'TRUCKS': {'hourly': 30, 'daily': 120, 'weekly': 200}
}

# generate car stock (inventory)
def generate_car_stock(num_cars):

    car_stock = {}

    for _ in range(num_cars):
        reg_no    = random.randint(10000, 50000)
        car_type  = random.choice(list(car_types.keys()))
        available = 'Yes'
        
        rented_by_customer = None
        rented_date        = None
        return_date        = None

        car_stock[reg_no] = {
            'car_type': car_type,
            'available': available,
            'rented_by_customer': rented_by_customer,
            'rented_date': rented_date,
            'return_date': return_date,
            'rates': car_types[car_type]
        }

    return car_stock

# display car stock
def display_stock(car_stock):

    car_type_count = {}
    total_stock = {}

    # Count total and available cars for each car type
    for reg_no, details in car_stock.items():
        car_type = details['car_type']
        
        if car_type in total_stock:
            total_stock[car_type] += 1
        else:
            total_stock[car_type] = 1

        if details['available'] == 'Yes':
            if car_type in car_type_count:
                car_type_count[car_type] += 1
            else:
                car_type_count[car_type] = 1

    if not car_type_count:
        return "No cars available"

    # Prepare data for tabulation
    available_cars = []
    for car_type, count in car_type_count.items():
        total        = total_stock[car_type]
        rates        = car_types[car_type]
        rental_rates = f"Hourly: ${rates['hourly']}, Daily: ${rates['daily']}, Weekly: ${rates['weekly']}"
        
        available_cars.append((car_type, total, count, rental_rates))
        
    headers = ["Car Type", "Total Stock", "Number of Available Cars", "Rental Rates"]
    table   = tabulate(available_cars, headers, tablefmt="pretty")
    
    return table

# book (rent) a car(s)
def book_car(car_stock, customer_bookings, customer_name, car_type, qty, rental_basis):
    if car_type not in car_types:
        return "Invalid car type entered."

    if rental_basis not in ['hourly', 'daily', 'weekly']:
        return "Invalid rental basis entered."

    if qty <= 0:
        return "Quantity must be a positive integer."

    available_cars = [reg_no for reg_no, details in car_stock.items() if details['available'] == 'Yes' and details['car_type'] == car_type]

    if not available_cars:
        return f"No available cars of {car_type} type."

    if qty > len(available_cars):
        return f"Not enough {car_type} cars available. Available: {len(available_cars)}"

    # Generate a unique booking reference
    booking_ref = f"{customer_name}_{car_type}_{rental_basis}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

    booking_details = []

    for reg_no in random.sample(available_cars, qty):  # Using random.sample to ensure unique cars are booked
        
        # Generate a random previous rental date
        some_prev_days_count = random.randint(3, 15)
        rental_date          = datetime.now() - timedelta(days=some_prev_days_count)
        
        car_stock[reg_no]['available'] = 'No'
        car_stock[reg_no]['rented_by_customer'] = customer_name
        car_stock[reg_no]['rented_date'] = datetime.now()
        car_stock[reg_no]['return_date'] = None

        # Add booking details to booking_details list
        booking_details.append({
            'customer_name': customer_name,
            'car_type': car_type,
            'rental_basis': rental_basis,
            'rental_date': rental_date,
            'return_date': None,
            'reg_no': reg_no
        })

    # Store booking details in customer_bookings using booking_ref as the key
    customer_bookings[booking_ref] = booking_details

    return f"Booking Successful! Booking Reference: {booking_ref}", car_stock

# Display customer bookings using tabulate
def display_customer_bookings(customer_bookings):
    booking_data = []
    headers      = ["Booking Ref", "Customer Name", "Car Type", "Reg No", "Rental Basis", "Rental Date", "Return Date"]
    
    for booking_ref, bookings in customer_bookings.items():
        for booking in bookings:
            booking_data.append([
                booking_ref,
                booking['customer_name'],
                booking['car_type'],
                booking['reg_no'],
                booking['rental_basis'],
                booking['rental_date'].strftime('%Y-%m-%d %H:%M:%S'),
                booking['return_date']
            ])
    
    table = tabulate(booking_data, headers, tablefmt="pretty")
    return table

# return the car(s)
def return_car(customer_bookings, car_stock):
    customer_name = input("Enter customer name: ")
    
    # Find active bookings for the customer
    active_bookings = []
    for booking_ref, bookings in customer_bookings.items():
        for booking in bookings:
            if booking['customer_name'] == customer_name and booking['return_date'] is None:
                active_bookings.append((booking_ref, booking))
    
    if not active_bookings:
        return "No active bookings found for the customer."
    
    # Display active bookings
    print(f"\nActive bookings for {customer_name}:")
    headers = ["Booking Ref", "Car Type", "Reg No", "Rental Basis", "Rental Date"]
    active_bookings_table = [(ref, b['car_type'], b['reg_no'], b['rental_basis'], b['rental_date'].strftime('%Y-%m-%d %H:%M:%S')) for ref, b in active_bookings]
    print(tabulate(active_bookings_table, headers, tablefmt="pretty"))
    
    reg_no = int(input("\nEnter the registration number of the car being returned: "))
    
    # Find the booking details for the given reg_no
    booking_details = None
    for booking_ref, booking in active_bookings:
        if booking['reg_no'] == reg_no:
            booking_details = booking
            break
    
    if not booking_details:
        return "Invalid registration number or the car is not currently rented by the customer."
    
    # Calculate the bill
    rental_date = booking_details['rental_date']
    return_date = datetime.now()
    rental_basis = booking_details['rental_basis']
    car_type = booking_details['car_type']
    rental_rate = car_types[car_type][rental_basis]
    
    rental_duration = return_date - rental_date
    if rental_basis == 'hourly':
        rental_hours = rental_duration.total_seconds() / 3600
        bill_amount = rental_hours * rental_rate
    elif rental_basis == 'daily':
        rental_days = rental_duration.days
        bill_amount = rental_days * rental_rate
    elif rental_basis == 'weekly':
        rental_weeks = rental_duration.days / 7
        bill_amount = rental_weeks * rental_rate
    
    bill_amount = round(bill_amount, 2)
    print(f"\nBill Amount: ${bill_amount}")
    
    # Capture if the bill is paid
    bill_paid = input("Is the bill paid? (yes/no): ").strip().lower()
    
    if bill_paid == 'yes':
        booking_details['return_date'] = return_date
        car_stock[reg_no]['available'] = 'Yes'
        car_stock[reg_no]['rented_by_customer'] = None
        car_stock[reg_no]['rented_date'] = None
        car_stock[reg_no]['return_date'] = None
        return f"Car returned successfully. Bill of ${bill_amount} has been paid."
    else:
        return "Car return not completed. Bill not paid."