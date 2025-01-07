import xml.etree.ElementTree as ET
import cv2
import numpy as np
import os

# Define the function to make the video from the parsed XML string
def make_video(xml_string, output_path="sources/outputs/dynamic_animations_video.mp4", sticker_directory="sources/stickers"):
    try:

        print(xml_string)
        # Parse the XML string
        root = ET.fromstring(xml_string)

        # Video properties
        video_width, video_height = 1280, 720
        fps = 30
        plot_data = []
        sticker_data = []


        # Parse the XML data from the string
        for scene in root.findall('scene'):
            item = {
                "text": scene.find('text').text,
                "start_time": float(scene.find('start_time').text),
                "duration": float(scene.find('duration').text),
                "animation_type": scene.find('animation_type').text,
                "start_position": [float(x) for x in scene.find('start_position').text.split(',')] if scene.find('start_position') is not None else [],
                "end_position": [float(x) for x in scene.find('end_position').text.split(',')] if scene.find('end_position') is not None else [],
                "start_scale": float(scene.find('start_scale').text) if scene.find('start_scale') is not None else 1.0,
                "end_scale": float(scene.find('end_scale').text) if scene.find('end_scale') is not None else 1.0,
                "intensity": float(scene.find('intensity').text) if scene.find('intensity') is not None else 5,
                "direction": scene.find('direction').text if scene.find('direction') is not None else None
            }
            plot_data.append(item)

        for sticker in root.findall('sticker'):
            sticker_data.append({
                "image_path": sticker.find('image_path').text,
                "start_time": float(sticker.find('start_time').text),
                "duration": float(sticker.find('duration').text),
                "animation_type": sticker.find('animation_type').text,
                "start_position": [float(x) for x in sticker.find('start_position').text.split(',')],
                "end_position": [float(x) for x in sticker.find('end_position').text.split(',')],
            })


        # Video output settings
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (video_width, video_height))

        # Generate video frames
        for frame_idx in range(int(sum(item["duration"] for item in plot_data) * fps)):
            # Create a blank frame
            frame = np.zeros((video_height, video_width, 3), dtype=np.uint8)
            frame[:] = (0, 0, 0)  # Black background

            # Get the current timestamp in seconds
            current_time = frame_idx / fps

            # Display appropriate text and handle animations
            for item in plot_data:
                if item["start_time"] <= current_time < item["start_time"] + item["duration"]:
                    text = item["text"]
                    animation = item.get("animation_type", "none")
                    progress = (current_time - item["start_time"]) / item["duration"]

                    # Handle fade_in animation
                    if animation == "fade_in":
                        alpha = int(255 * progress)
                        text_x = (video_width - cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][0]) // 2
                        text_y = video_height // 2
                        overlay = frame.copy()
                        cv2.putText(overlay, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                        cv2.addWeighted(overlay, alpha / 255, frame, 1 - alpha / 255, 0, frame)

                    # Handle move animation
                    elif animation == "move":
                        start_position = item.get("start_position", [0, 0])
                        end_position = item.get("end_position", [video_width // 2, video_height // 2])
                        text_x = int(start_position[0] + (end_position[0] - start_position[0]) * progress)
                        text_y = int(start_position[1] + (end_position[1] - start_position[1]) * progress)
                        cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                    # Handle scale animation
                    elif animation == "zoom":
                        start_scale = item["start_scale"]
                        end_scale = item["end_scale"]
                        scale = start_scale + (end_scale - start_scale) * progress
                        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, int(scale))[0]
                        text_x = (video_width - text_size[0]) // 2
                        text_y = (video_height + text_size[1]) // 2
                        cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), int(scale), cv2.LINE_AA)

                    # Handle shake animation
                    elif animation == "shake":
                        intensity = item["intensity"]
                        offset_x = int(intensity * np.sin(2 * np.pi * progress * fps))
                        offset_y = int(intensity * np.cos(2 * np.pi * progress * fps))
                        text_x = (video_width - cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][0]) // 2 + offset_x
                        text_y = video_height // 2 + offset_y
                        cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                    # Handle slide animation
                    elif animation == "slide":
                        if item["direction"] == "up":
                            text_x = (video_width - cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][0]) // 2
                            text_y = int(video_height - video_height * progress)
                            cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                    # No animation, just static text
                    else:
                        text_x = (video_width - cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][0]) // 2
                        text_y = video_height // 2
                        cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                    break  # We only show one scene at a time per frame

            for sticker in sticker_data:
                if sticker["start_time"] <= current_time < sticker["start_time"] + sticker["duration"]:
                    # Construct full path for the sticker image
                    image_path = os.path.join(sticker_directory, sticker["image_path"])
                    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
                    if image is None:
                        print(f"Warning: Sticker image not found at {image_path}")
                        continue

                    # Resize sticker to fit within video frame if needed
                    h, w = image.shape[:2]
                    max_width, max_height = video_width // 2, video_height // 2  # Limit sticker size
                    scale_factor = min(max_width / w, max_height / h, 1)  # Only shrink if necessary
                    new_width, new_height = int(w * scale_factor), int(h * scale_factor)
                    image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

                    # Handle transparency (alpha channel)
                    if image.shape[2] == 4:  # RGBA
                        bgr = image[:, :, :3]
                        alpha_channel = image[:, :, 3] / 255.0
                    else:  # No alpha channel
                        bgr = image
                        alpha_channel = np.ones((new_height, new_width), dtype=np.float32)

                    # Animation (e.g., move)
                    animation = sticker.get("animation_type", "none")
                    progress = (current_time - sticker["start_time"]) / sticker["duration"]
                    x, y = sticker["start_position"]

                    if animation == "move":
                        end_x, end_y = sticker["end_position"]
                        x = int(sticker["start_position"][0] + (end_x - sticker["start_position"][0]) * progress)
                        y = int(sticker["start_position"][1] + (end_y - sticker["start_position"][1]) * progress)

                    x = int(max(0, min(video_width - new_width, x)))
                    y = int(max(0, min(video_height - new_height, y)))

                    for c in range(3):
                        frame[y:y+int(new_height), x:x+int(new_width), c] = (
                            alpha_channel * bgr[:, :, c] +
                            (1 - alpha_channel) * frame[y:y+int(new_height), x:x+int(new_width), c]
                        )

                    
            # Write frame to video
            out.write(frame)

        # Release the VideoWriter
        out.release()
        return {
            "status": "success",
            "message": f"Video with animations created successfully: {output_path}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating video: {e}"
        }