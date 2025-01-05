import cv2
import numpy as np
import json


def make_video(json_data):
    data = json.loads(json_data)
    plot_data = data["json_data"]["value"]["scenes"]

    # Video properties
    video_width, video_height = 1280, 720
    fps = 30
    total_duration = sum(item["duration"] for item in plot_data)
    total_frames = total_duration * fps
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    output_file = "dynamic_animations_video.mp4"
    out = cv2.VideoWriter(output_file, fourcc, fps, (video_width, video_height))

    # Generate video frames
    for frame_idx in range(total_frames):
        # Create a blank frame
        frame = np.zeros((video_height, video_width, 3), dtype=np.uint8)
        frame[:] = (0, 0, 0)  # Black background

        # Get the current timestamp in seconds
        current_time = frame_idx / fps

        # Display appropriate text and handle animations
        for item in plot_data:
            if item["start_time"] <= current_time < item["start_time"] + item["duration"]:
                text = item["text"]
                animation = item.get("animation", {})
                animation_type = animation.get("type", "none")

                # Calculate progress for animation (0 to 1)
                progress = (current_time - item["start_time"]) / item["duration"]

                # Handle fade_in animation
                if animation_type == "fade_in":
                    alpha = int(255 * progress)
                    text_x = (video_width - cv2.getTextSize(text, font, 1, 2)[0][0]) // 2
                    text_y = video_height // 2
                    overlay = frame.copy()
                    cv2.putText(overlay, text, (text_x, text_y), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.addWeighted(overlay, alpha / 255, frame, 1 - alpha / 255, 0, frame)

                # Handle move animation
                elif animation_type == "move":
                    start_position = animation.get("start_position", [0, 0])
                    end_position = animation.get("end_position", [video_width // 2, video_height // 2])
                    text_x = int(start_position[0] + (end_position[0] - start_position[0]) * progress)
                    text_y = int(start_position[1] + (end_position[1] - start_position[1]) * progress)
                    cv2.putText(frame, text, (text_x, text_y), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

                # Handle scale animation
                elif animation_type == "scale":
                    start_scale = animation.get("start_scale", 1.0)
                    end_scale = animation.get("end_scale", 1.0)
                    scale = start_scale + (end_scale - start_scale) * progress
                    text_size = cv2.getTextSize(text, font, scale, int(scale))[0]
                    text_x = (video_width - text_size[0]) // 2
                    text_y = (video_height + text_size[1]) // 2
                    cv2.putText(frame, text, (text_x, text_y), font, scale, (255, 255, 255), int(scale), cv2.LINE_AA)

                # Handle shake animation
                elif animation_type == "shake":
                    intensity = animation.get("intensity", 5)
                    offset_x = int(intensity * np.sin(2 * np.pi * progress * fps))
                    offset_y = int(intensity * np.cos(2 * np.pi * progress * fps))
                    text_x = (video_width - cv2.getTextSize(text, font, 1, 2)[0][0]) // 2 + offset_x
                    text_y = video_height // 2 + offset_y
                    cv2.putText(frame, text, (text_x, text_y), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

                # No animation, just display static text
                else:
                    text_x = (video_width - cv2.getTextSize(text, font, 1, 2)[0][0]) // 2
                    text_y = video_height // 2
                    cv2.putText(frame, text, (text_x, text_y), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

                break

        # Write frame to video
        out.write(frame)

    # Release the VideoWriter
    out.release()
    print(f"Video with animations created successfully: {output_file}")