import asyncio
import gphoto2 as gp
import cv2
import time


async def list_cameras():
    context = gp.Context()
    camera_list = gp.Camera.autodetect(context)

    for index, (name, addr) in enumerate(camera_list):
        camera = gp.Camera()
        camera.init(context)
        print("Camera found:", name)
        camera.exit(context)


async def capture_photo(output_filename="captured_image.jpg"):
    cmd = ["gphoto2", "--capture-image-and-download", "--filename", output_filename]
    await asyncio.create_subprocess_exec(*cmd)

    cmd_download = [
        "gphoto2",
        "--filename",
        output_filename,
        "--get-file",
        "capt0000.jpg",
    ]
    await asyncio.create_subprocess_exec(*cmd_download)


def display_image(filename):
    image = cv2.imread(filename)
    cv2.imshow("Captured Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


async def main():
    await list_cameras()
    await capture_photo()
    time.sleep(1)
    display_image("captured_image.jpg")


if __name__ == "__main__":
    asyncio.run(main())
