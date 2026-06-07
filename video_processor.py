from moviepy import VideoFileClip


def extract_audio_from_video(video_path, audio_output_path):

    try:
        clip = VideoFileClip(video_path)

        if clip.audio is None:
            return False

        clip.audio.write_audiofile(
            audio_output_path,
            logger=None
        )

        clip.close()

        return True

    except Exception as e:
        print("VIDEO AUDIO ERROR:", e)
        return False