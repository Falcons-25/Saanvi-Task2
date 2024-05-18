import serial

try:
    file = open(r"Ultrasonic.csv", "w", newline="")
    ser = serial.Serial('COM6', 9600)

    while True:
        # Read data from serial port
        data1 = ser.readline().decode().strip()
        millis, dist = data1.split(',')

        # Print and write data to CSV file
        print(f"Millis: {millis}, Distance: {dist}\n")
        file.write(f"Millis: {millis}, Distance: {dist}\n")


except ValueError as e:
    print(e)
    file.write("COM disconnected \n")

except KeyboardInterrupt as e:
    print(e)
    file.write("User intended break \n")
finally:
    # Close the CSV file
    file.close()
