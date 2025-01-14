import requests
from xml.etree import ElementTree as ET
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
from gtts import gTTS
from pydub import AudioSegment
import subprocess
from google.cloud import texttospeech
import os
from dotenv import load_dotenv
import time
import io
from google.cloud import speech
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

load_dotenv()


def transcribe_audio_with_timestamps(file_path):
    client = speech.SpeechClient()

    with io.open(file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=16000,
        language_code="en-US",
        enable_word_time_offsets=True
    )

    response = client.recognize(config=config, audio=audio)

    word_timestamps = []
    for result in response.results:
        alternative = result.alternatives[0]
        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time.total_seconds()
            end_time = word_info.end_time.total_seconds()
            word_timestamps.append((word, start_time, end_time))
    return word_timestamps

def fetch_image_from_url(url):
    """Fetch image from URL and return it as a numpy array."""
    response = requests.get(url)
    if response.status_code == 200:
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return img  # Returns an OpenCV (BGR) image
    else:
        raise Exception(f"Failed to fetch image from {url}")

def parse_xml(xml_string):
    """Parse the XML string and extract scene details."""
    xml_string = xml_string.replace('&apos;', "'")
    root = ET.fromstring(xml_string)
    scenes = []

    for scene in root.findall("Scene"):
        text_parts = [part.text for part in scene.findall("TextPart")]

        image_url = scene.find("ImageUrl").text
        duration = scene.find("Duration").text
        start, end = duration.split("-")
        start_seconds = int(start.split(":")[0]) * 60 + int(start.split(":")[1])
        end_seconds = int(end.split(":")[0]) * 60 + int(end.split(":")[1])

        scenes.append({
            "text_parts": text_parts,
            "image_url": image_url,
            "start": start_seconds,
            "end": end_seconds
        })
    
    return scenes

def add_subtitles_to_image(image, text, current_word, alpha=255):
    """Add animated subtitles to an OpenCV image with outline and bold effect."""
    # Convert OpenCV image (BGR) to PIL (RGB)
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    # Initialize drawing context
    draw = ImageDraw.Draw(image_pil)
    # Define the path to the font file
    font_path = os.path.join(os.path.dirname(__file__), "test.otf")

    # Check if the font file exists
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font file not found: {font_path}")

    # Load the font
    font = ImageFont.truetype(font_path, 60)  # Bold font for better visibility
    
    # Get image dimensions
    width, height = image_pil.size
    
    # Split the text into words
    words = text.split()
    
    # Prepare to split text into lines
    lines = []
    current_line = []
    current_line_width = 0
    max_line_width = width * 0.8  # Use 80% of the image width for text

    # Split words into lines
    for word in words:
        word_width = draw.textbbox((0, 0), word, font=font)[2]
        if current_line_width + word_width + 10 > max_line_width:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_line_width = word_width
        else:
            current_line.append(word)
            current_line_width += word_width + 10
    if current_line:
        lines.append(" ".join(current_line))
    
    # Calculate total height of the text
    total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in lines)
    
    # Calculate starting y position for centered text
    y = (height - total_text_height) // 2
    
    # Draw each line of text
    for line in lines:
        # Calculate total width of the line
        line_width = draw.textbbox((0, 0), line, font=font)[2]
        x = (width - line_width) // 2  # Center the line horizontally
        
        # Draw each word in the line
        for word in line.split():
            # Measure the size of the word using textbbox
            bbox = draw.textbbox((0, 0), word, font=font)
            word_width, word_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            
            # Draw outline by drawing text multiple times with a slight offset
            outline_color = (0, 0, 0, alpha)  # Black outline
            for dx in [-2, 2]:
                for dy in [-2, 2]:
                    draw.text((x + dx, y + dy), word, font=font, fill=outline_color)
            
            # Draw the word with the specified alpha for fade-in effect
            # Highlight the current word with a different color
            fill_color = (255, 0, 0, alpha) if word == current_word else (255, 255, 255, alpha)
            draw.text((x, y), word, font=font, fill=fill_color)
            
            # Move x position for the next word
            x += word_width + 10  # Add some space between words
        
        # Move y position for the next line
        y += word_height
    
    # Convert back to OpenCV (BGR)
    image_with_text = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    return image_with_text

def create_audio_from_text(text, language='en-US', index=0, voice_name='en-US-Casual-K', use_simple_voice="eleven"):
    """Create an audio file from text using Google Cloud Text-to-Speech, gTTS, or ElevenLabs."""
    try:
        if use_simple_voice == 'simple':
            # Use gTTS for simple voice
            tts = gTTS(text=text, lang=language.split('-')[0])
            audio_path = f"temp_audio_{index}.mp3"
            tts.save(audio_path)
            print(f"Simple audio file created: {audio_path}")
        elif use_simple_voice == 'eleven':

            # Use ElevenLabs for voice generation
            audio_path = generate_voice_with_elevenlabs(text, index)
            print(f"ElevenLabs audio file created: {audio_path}")
        else:
            # Use Google Cloud Text-to-Speech for AI voice
            client = texttospeech.TextToSpeechClient()

            synthesis_input = texttospeech.SynthesisInput(text=text)

            voice = texttospeech.VoiceSelectionParams(
                language_code=language,
                name=voice_name,
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            audio_path = f"temp_audio_{index}.mp3"
            with open(audio_path, "wb") as out:
                out.write(response.audio_content)
                print(f"AI audio file created: {audio_path}")

        return audio_path
    except Exception as e:
        print(f"Error creating audio file: {e}")
        return None

def generate_voice_with_elevenlabs(text, index):
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    """Generate voice using ElevenLabs and return the path to the audio file."""
    try:
        # Convert text to speech using ElevenLabs
        audio_path = f"temp_files/elevenlabs_audio_{index}.mp3"  # Save ElevenLabs audio in temp_files folder
        response = client.text_to_speech.convert(
            voice_id="nPczCjzI2devNBz1zQrb",  # Example voice ID
            output_format="mp3_22050_32",
            text=text,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.0,
                similarity_boost=1.0,
                style=0.0,
                # use_speaker_boost=True,
            )
        )
        
        # Save the audio to a file
        with open(audio_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)
        
        print(f"ElevenLabs audio file created: {audio_path}")
        return audio_path
    except Exception as e:
        print(f"Error generating voice with ElevenLabs: {e}")
        return None

def correct_word_timestamps(word_timestamps, full_text):
    """Correct words in word_timestamps based on the full text without changing timestamps."""
    # Split the full text into words and convert to lowercase
    expected_words = full_text.split()
    expected_words_lower = [word.lower() for word in expected_words]
    
    # Extract words from word_timestamps and convert to lowercase
    transcribed_words = [word for word, _, _ in word_timestamps]
    transcribed_words_lower = [word.lower() for word in transcribed_words]
    
    # Check for discrepancies
    if transcribed_words_lower != expected_words_lower:
        print("Discrepancy found between transcribed words and expected words.")
        print(f"Transcribed: {transcribed_words}")
        print(f"Expected: {expected_words}")
        
        # Attempt to correct the words without changing timestamps
        corrected_timestamps = []
        expected_index = 0
        transcribed_index = 0
        
        while expected_index < len(expected_words) and transcribed_index < len(transcribed_words):
            if transcribed_words_lower[transcribed_index] == expected_words_lower[expected_index]:
                # If words match (ignoring case), add the original timestamp
                corrected_timestamps.append(word_timestamps[transcribed_index])
                expected_index += 1
                transcribed_index += 1
            else:
                # If words don't match, correct the word but keep the original timestamp
                print(f"Correcting word: {transcribed_words[transcribed_index]} to {expected_words[expected_index]}")
                corrected_timestamps.append((expected_words[expected_index], word_timestamps[transcribed_index][1], word_timestamps[transcribed_index][2]))
                expected_index += 1
                transcribed_index += 1
        
        # If there are remaining expected words, append them with a placeholder timestamp
        while expected_index < len(expected_words):
            print(f"Adding missing word: {expected_words[expected_index]}")
            # Use a placeholder timestamp (e.g., None) to indicate missing timestamps
            corrected_timestamps.append((expected_words[expected_index], None, None))
            expected_index += 1
        
        return corrected_timestamps
    else:
        return word_timestamps

def create_video_from_scenes(xml_string, scenes, output_path, frame_rate=30, use_simple_voice="simple"):
    """Create a video from scenes using OpenCV with text animations and synchronized audio."""
    # Set video dimensions for TikTok (e.g., 720x1280 for vertical video)
    video_width = 720
    video_height = 1280
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    temp_video_path = "temp_files/temp_video.mp4"  # Save temporary video in temp_files folder
    video_writer = cv2.VideoWriter(temp_video_path, fourcc, frame_rate, (video_width, video_height))
    
    # Define transition duration in frames
    transition_duration = int(frame_rate * 0.5)  # 0.5 second transition
    
    previous_frame = None  # Храним последний кадр предыдущей сцены
    last_offset = 0  # Храним последнее смещение

    # Extract background audio path from the first scene's AudioSource
    xml_root = ET.fromstring(xml_string)
    background_audio_file = xml_root.find("AudioSource").text.strip()
    background_audio_path = os.path.join("sources/media", background_audio_file)  # Update path to sources/media

    # Load and adjust background audio from the specified file path
    background_audio = AudioSegment.from_file(background_audio_path)
    background_audio = background_audio - 20  # Reduce volume by 20 dB (10% volume)

    # Create a silent audio segment to append voiceovers
    combined_audio = AudioSegment.silent(duration=0)

    # Fallback frame rate in case actual frame rate is zero
    fallback_frame_rate = frame_rate

    subtitle_delay = 0.75  # 1 second delay for subtitles between scenes
    speed_factor = 0.95  # Speed up subtitles by 20%

    for index, scene in enumerate(scenes):
        start_time = time.time()
        print(f"Processing scene: {scene['text_parts']}")
        
        # Fetch image from the URL
        image = fetch_image_from_url(scene["image_url"])
        print(f"Image fetched in {time.time() - start_time:.2f} seconds")
        
        # Resize image to fill video dimensions (may crop image)
        h, w, _ = image.shape
        aspect_ratio = w / h
        target_aspect_ratio = video_width / video_height
        
        if aspect_ratio > target_aspect_ratio:
            # Image is wider than target aspect ratio, crop width
            new_height = video_height
            new_width = int(new_height * aspect_ratio)
        else:
            # Image is taller than target aspect ratio, crop height
            new_width = video_width
            new_height = int(new_width / aspect_ratio)
        
        # Resize image
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        print(f"Image resized and cropped in {time.time() - start_time:.2f} seconds")
        
        # Calculate the maximum rightward movement
        max_offset = max(0, new_width - video_width)

        # If there is a previous frame, create a transition
        # if previous_frame is not None:
        #     # Create initial frame for the new scene without subtitles
        #     current_frame = image[
        #         (new_height - video_height) // 2:(new_height - video_height) // 2 + video_height,
        #         :video_width
        #     ]
            
        #     # Use the last frame of the previous scene for transition
        #     for t in range(transition_duration):
        #         alpha = t / transition_duration
        #         blended_image = cv2.addWeighted(previous_frame, 1 - alpha, current_frame, alpha, 0)
        #         video_writer.write(blended_image)

        # Generate audio for the scene
        full_text = " ".join(scene["text_parts"])
        audio_path = create_audio_from_text(full_text, index=index, use_simple_voice="eleven")
        print(f"Audio generated in {time.time() - start_time:.2f} seconds")
        if not audio_path:
            print(f"Failed to create audio for scene {index}")
            continue
        
        # Load the audio file to get its duration
        try:
            print(f"Loading audio file: {audio_path}")
            audio = AudioSegment.from_file(audio_path)
            audio_duration = len(audio) / 1000.0  # Convert to seconds
            print(f"Audio duration: {audio_duration} seconds")
        except Exception as e:
            print(f"Error loading audio file {audio_path}: {e}")
            continue
        print(f"Audio loaded in {time.time() - start_time:.2f} seconds")

        # Initialize word_timestamps to an empty list
        word_timestamps = []

        # Skip transcription if using simple voice
        if use_simple_voice != "simple1":
            word_timestamps = transcribe_audio_with_timestamps(audio_path)
            word_timestamps = correct_word_timestamps(word_timestamps, full_text)
        else:
            # Add a delay to the start of the subtitles to match the audio delay
            audio_delay = 0.5  # Adjust this value as needed
            word_timestamps = [(word, start + audio_delay, end + audio_delay) for word, start, end in word_timestamps]

        # Add subtitle delay between scenes
        if index > 0:
            word_timestamps = [(word, start + subtitle_delay, end + subtitle_delay) for word, start, end in word_timestamps]

        # Adjust word timestamps to speed up subtitles
        word_timestamps = [(word, start * speed_factor, end * speed_factor) for word, start, end in word_timestamps]

        # Calculate the correct frame rate for subtitles
        actual_frame_rate = video_writer.get(cv2.CAP_PROP_FPS)
        if actual_frame_rate == 0:
            print("Warning: Actual frame rate is zero, using fallback frame rate.")
            actual_frame_rate = fallback_frame_rate

        # If word_timestamps is empty, add the entire text as a single block
        if not word_timestamps:
            full_text = " ".join(scene["text_parts"])
            word_timestamps = [(full_text, scene['start'], scene['end'])]

        # Group words into blocks of 3-4 words
        word_blocks = []
        current_block = []
        for word, start_time, end_time in word_timestamps:
            current_block.append((word, start_time, end_time))
            if len(current_block) >= 4:
                word_blocks.append(current_block)
                current_block = []

        # If the last block has only one word, merge it with the previous block
        if len(current_block) == 1 and word_blocks:
            word_blocks[-1].extend(current_block)
        elif current_block:
            word_blocks.append(current_block)

        # Write frames to the video with animation based on word timestamps
        total_scene_frames = int((scene['end'] - scene['start']) * actual_frame_rate)
        
        # Calculate y_start to center the image vertically
        y_start = (new_height - video_height) // 2

        # Initialize frame index for the entire scene
        scene_frame_idx = 0

        # Write initial frames with TextPart as a single block without highlighting
        delay_frames = int(subtitle_delay * actual_frame_rate)
        text_part = " ".join(scene["text_parts"])
        for _ in range(delay_frames):
            # Calculate the current offset for smooth movement
            move_offset = int(scene_frame_idx / total_scene_frames * max_offset)
            move_offset = min(move_offset, max_offset)

            # Adjust the cropping to include the offset
            x_start = move_offset
            cropped_image = image[y_start:y_start + video_height, 
                                  x_start:x_start + video_width]
            for block in word_blocks:
                block_start_time = block[0][1]
                block_end_time = block[-1][2]
                start_frame = int(block_start_time * actual_frame_rate)
                end_frame = int(block_end_time * actual_frame_rate)
                block_text = " ".join(word for word, _, _ in block)

            # Get the text of the first block
            first_block_text = " ".join(word for word, _, _ in word_blocks[0])

            # Add TextPart as a single block without highlighting
            frame_with_text = add_subtitles_to_image(cropped_image, first_block_text, current_word="", alpha=255)
            video_writer.write(frame_with_text)

        for block in word_blocks:
            block_start_time = block[0][1]
            block_end_time = block[-1][2]
            start_frame = int(block_start_time * actual_frame_rate)
            end_frame = int(block_end_time * actual_frame_rate)
            block_text = " ".join(word for word, _, _ in block)

            for frame_idx in range(start_frame, end_frame):
                # Calculate the current offset for smooth movement
                move_offset = int(scene_frame_idx / total_scene_frames * max_offset)
                move_offset = min(move_offset, max_offset)

                # Adjust the cropping to include the offset
                x_start = move_offset
                cropped_image = image[y_start:y_start + video_height, 
                                      x_start:x_start + video_width]

                # Determine the current word to highlight
                current_word_index = (frame_idx - start_frame) / (end_frame - start_frame)
                current_word = block[int(current_word_index * len(block)) % len(block)][0] if len(block) > 1 else ""

                # Fade-in effect
                alpha = min(255, int(255 * ((frame_idx - start_frame) / (end_frame - start_frame))))

                # Add subtitles and effects
                frame_with_text = add_subtitles_to_image(cropped_image, block_text, current_word, alpha=alpha)
                
                # Store the last frame for transition
                if frame_idx == end_frame - 1:
                    previous_frame = frame_with_text.copy()
                    last_offset = move_offset
                
                video_writer.write(frame_with_text)

                # Increment the scene frame index
                scene_frame_idx += 1

        # Append the voiceover audio immediately
        combined_audio += audio
        
        # Set the current image as the previous image for the next iteration
        previous_frame = frame_with_text  # Use the last frame with text and effects
    
    # Release the video writer to ensure the video file is properly finalized
    video_writer.release()

    # Overlay the combined audio with the background audio
    combined_audio = combined_audio.overlay(background_audio, loop=True)

    # Export the combined audio
    combined_audio_path = "temp_files/combined_audio.mp3"  # Save combined audio in temp_files folder
    combined_audio.export(combined_audio_path, format="mp3")
    
    # Use ffmpeg to combine video and audio
    ffmpeg_command = [
        'ffmpeg', '-i', temp_video_path, '-i', combined_audio_path, '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', output_path
    ]
    subprocess.run(ffmpeg_command)
    
    # Clean up temporary files
    os.remove(temp_video_path)
    os.remove(combined_audio_path)
    if os.path.exists(audio_path):  # Check if the file exists before removing
        os.remove(audio_path)
    else:
        print(f"Warning: {audio_path} does not exist and cannot be removed.")

def escape_xml_characters(xml_string):
    """Escape special characters in the XML string."""
    return xml_string.replace('&', '&amp;').replace("'", "&apos;")


def make_video(xml_string):


    # Parse the XML string
    scenes = parse_xml(escape_xml_characters(xml_string))
    
    # Create video
    output_path = 'svideo/video.mp4'
    create_video_from_scenes(escape_xml_characters(xml_string), scenes, output_path, use_simple_voice="eleven")

    return output_path 

