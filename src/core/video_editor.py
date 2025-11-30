"""Video editor module for the travel assistant application."""

import os
import tempfile
from typing import List, Optional
from moviepy import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    vfx
)


def create_video_from_images(
    image_paths: List[str],
    audio_path: Optional[str] = None,
    fps: int = 24,
    duration_per_image: float = 3.0,
    transition_duration: float = 0.5,
    animation_type: str = "none"
) -> str:
    """
    Create a video from a list of images with optional audio background.
    
    Args:
        image_paths: List of paths to images
        audio_path: Path to audio file (optional)
        fps: Frames per second for the video
        duration_per_image: Duration each image is displayed
        transition_duration: Duration of transitions between images
        animation_type: Type of animation to apply to images
        
    Returns:
        str: Path to the created video file
    """
    # Validate input
    if not image_paths:
        raise ValueError("No images provided")
    
    # Create image clips with animations
    clips = []
    for i, img_path in enumerate(image_paths):
        # Create base clip
        clip = ImageClip(img_path, duration=duration_per_image)
        
        # Apply animation
        if animation_type == "fade":
            clip = vfx.fadein(clip, transition_duration)
            clip = vfx.fadeout(clip, transition_duration)
        elif animation_type == "zoom":
            clip = clip.resize(lambda t: 1 + 0.05 * t).set_position("center")
        elif animation_type == "slide":
            # Slide from left to right
            clip = clip.set_position(lambda t: (int(-clip.w * (1 - t / duration_per_image)), "center"))
        
        # Add transition
        if i > 0:
            clip = vfx.fadein(clip, transition_duration)
        if i < len(image_paths) - 1:
            clip = vfx.fadeout(clip, transition_duration)
        
        clips.append(clip)
    
    # Concatenate clips
    final_clip = concatenate_videoclips(clips, method="compose")
    
    # Add audio if provided
    if audio_path:
        audio = AudioFileClip(audio_path)
        # Trim audio to match video duration
        if audio.duration > final_clip.duration:
            audio = audio.subclip(0, final_clip.duration)
        # Loop audio if it's shorter than video
        elif audio.duration < final_clip.duration:
            audio = audio.loop(duration=final_clip.duration)
        final_clip = final_clip.set_audio(audio)
    
    # Write video file
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        video_path = tmp.name
    
    final_clip.write_videofile(video_path, fps=fps, codec="libx264")
    
    return video_path


def validate_media_files(image_paths: List[str], audio_path: Optional[str] = None) -> bool:
    """
    Validate that all media files exist and are accessible.
    
    Args:
        image_paths: List of paths to images
        audio_path: Path to audio file (optional)
        
    Returns:
        bool: True if all files are valid, False otherwise
    """
    # Check images
    for img_path in image_paths:
        if not os.path.exists(img_path) or not os.path.isfile(img_path):
            return False
    
    # Check audio
    if audio_path and (not os.path.exists(audio_path) or not os.path.isfile(audio_path)):
        return False
    
    return True
