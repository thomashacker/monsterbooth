import subprocess
import os


def list_printers():
    """
    Return a list of available printers on the system.
    """
    cmd = ["lpstat", "-p"]
    completed_process = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    if completed_process.returncode != 0:
        print("Error occurred while fetching the list of printers.")
        return []

    printers = []
    for line in completed_process.stdout.splitlines():
        if "printer" in line:
            printer_name = line.split(" ")[1]
            printers.append(printer_name)

    return printers


def check_printer_exists(printer_name):
    """
    Check if the specified printer exists in the list of available printers.
    """
    printers = list_printers()
    return printer_name in printers


def print_image(image_path):
    os.system(f"lpr -o fit-to-page -o media=A6 {image_path}")


# Specify the path to your image
image_path = (
    "captured_image.jpg"  # Modify this if your image is in a different location
)


# Usage
printer_to_check = "Canon_SELPHY_CP1500"
if check_printer_exists(printer_to_check):
    print(f"The printer '{printer_to_check}' exists on this system.")
else:
    print(f"The printer '{printer_to_check}' does not exist on this system.")

print("Printing image")

print_image(image_path)
