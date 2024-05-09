import streamlit as st
import cv2
import asyncio
import gphoto2 as gp
import time
import subprocess
import os
from pathlib import Path
import json
import datetime


def load_config():
    if Path("config.json").exists():
        with open("config.json", "r") as file:
            config = json.load(file)
    else:
        config = {"chosen_overlay": "overlay/monsters_neu.png"}  # default value
    return config


def save_config(config):
    with open("config.json", "w") as file:
        json.dump(config, file)


async def list_cameras():
    context = gp.Context()
    camera_list = gp.Camera.autodetect(context)
    cameras = []
    for index, (name, addr) in enumerate(camera_list):
        camera = gp.Camera()
        try:
            camera.init(context)
            cameras.append(name)
        except gp.GPhoto2Error as e:
            if e.code == gp.GP_ERROR_CAMERA_BUSY:
                st.write(f"Camera {name} is currently in use by another process.")
            else:
                st.write(f"An error occurred with camera {name}: {str(e)}")
        finally:
            camera.exit(context)
    return cameras


def resize_and_crop(image, desired_width, desired_height):
    # Calculate the ratio to resize the height
    ratio = desired_height / image.shape[0]

    # Resize the image based on the calculated ratio
    new_width = int(image.shape[1] * ratio)
    resized_image = cv2.resize(image, (new_width, desired_height))

    # Crop the width if necessary
    start_x = (new_width - desired_width) // 2
    cropped_image = resized_image[:, start_x : start_x + desired_width]

    return cropped_image


async def capture_photo(output_filename="captured_image.jpg"):
    cmd = [
        "gphoto2",
        "--debug",
        "--capture-image-and-download",
        "--debug-logfile=my-logfile.txt",
        "--keep",
        "--filename",
        output_filename,
        "--force-overwrite",
    ]
    await asyncio.create_subprocess_exec(*cmd)


def overlay_image(background, overlay, x=0, y=0):
    h, w, _ = overlay.shape
    background[y : y + h, x : x + w] = cv2.addWeighted(
        background[y : y + h, x : x + w], 1, overlay, 1, 0
    )
    return background


def st_display_image(filename, overlay_filename):
    # Load the captured image
    image = cv2.imread(filename)

    # Resize the image (let's say you want to resize it to 800x600)

    # image = cv2.resize(image, (800, 600))
    image = resize_and_crop(image, 4998, 3376)

    # Load the overlay image (assuming it has transparency)
    overlay = cv2.imread(overlay_filename, cv2.IMREAD_UNCHANGED)

    # Make sure overlay is a 4-channel PNG (has transparency)
    if overlay.shape[2] == 4:
        # Extract the alpha channel and use it to determine where to overlay
        alpha = overlay[:, :, 3] / 255.0
        for channel in range(0, 3):
            image[:, :, channel] = (
                image[:, :, channel] * (1 - alpha) + alpha * overlay[:, :, channel]
            )

    # Save the resultant image
    cv2.imwrite("resultant_image.jpg", image)

    # Convert the image from BGR to RGB format for Streamlit display
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    st.image(image, caption="Captured Image", use_column_width=True)


def list_printers():
    """
    Return a list of available and ready printers on the system.
    """
    cmd = ["lpstat", "-p", "-d"]
    completed_process = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    if completed_process.returncode != 0:
        print("Error occurred while fetching the list of printers:", completed_process.stderr)
        return []

    printers = []
    for line in completed_process.stdout.splitlines():
        if "printer" in line:
            parts = line.split()
            if len(parts) >= 4 and parts[3] == "idle":
                printer_name = parts[1]
                printers.append(printer_name)

    return printers


def check_printer_exists(printer_name):
    """
    Check if the specified printer exists in the list of available printers.
    """
    printers = list_printers()
    print(f'Printers {printers}')
    return printer_name in printers


def save_image():
    # Load the captured image
    image = cv2.imread("resultant_image.jpg")

    # Get current datetime and format it
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%d_%m_%Y_%H_%M_%S")
    filename = f"{formatted_time}.jpg"

    # Save the resultant image
    cv2.imwrite("saved_images/" + filename, image)


async def print_image_async(image_path):
    print("Printing Image!")
    cmd = f"lpr -P Canon_SELPHY_CP1500 -o fit-to-page -o media=A6 -o landscape -o color=true  {image_path}"

    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        print(f"Error occurred while printing. {stderr.decode()}")


def st_display_overlay(overlay_filename):
    """Display the chosen overlay."""
    overlay = cv2.imread(overlay_filename, cv2.IMREAD_UNCHANGED)
    overlay = cv2.cvtColor(overlay, cv2.COLOR_BGRA2RGBA)
    st.image(overlay, caption="Selected Overlay", use_column_width=True)


async def main():
    config = load_config()
    # Layout for title, subheader, and logo
    st.title("👹 Monsters Booth")
    st.subheader("Verewige deine Visage für immer")

    # Check if camera and printer are available
    cameras = await list_cameras()
    is_printer_available = check_printer_exists("Canon_SELPHY_CP1500")

    stat1, stat2 = st.columns(2)

    # Display status metrics
    if cameras:
        stat1.success("Kamera ist verfügbar!")
    else:
        stat1.error("Kamera nicht verfügbar!")

    if is_printer_available:
        stat2.success("Drucker ist verfügbar!")
    else:
        stat2.error("Drucker ist nicht verfügbar!")

    st.divider()

    overlay_files = [f for f in os.listdir("overlay") if f.endswith(".png")]

    but1, but2, but3 = st.columns(3)

    # Create a button in Streamlit
    if but1.button("📷 Mache ein Foto!"):
        for i in range(3, 0, -1):
            st.write(f"Foto in... {i}")
            time.sleep(1)
        st.write("Cheesee...")

        await capture_photo()
        time.sleep(3)  # Wait a bit for the image to be fully saved

    if Path("resultant_image.jpg").exists():
        if but2.button("🖨️ Foto Drucken"):
            await print_image_async(
                "resultant_image.jpg",
            )
        if but3.button("💾 Foto Speichern"):
            save_image()

    if Path("captured_image.jpg").exists():
        chosen_overlay = st.selectbox(
            "🖼️ Wähle deinen Rahmen",
            overlay_files,
            index=overlay_files.index(Path(config["chosen_overlay"]).name),
        )
        config["chosen_overlay"] = chosen_overlay
        save_config(config)
        st_display_image(
            "captured_image.jpg",
            overlay_filename=os.path.join("overlay", chosen_overlay),
        )


# Instead of __main__, in Streamlit, you just call main() directly
asyncio.run(main())
