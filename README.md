# robot

APIs, pacakges, programs used:
Uses tweepy for Twitter OAuth 1.0 and status object processing, speech processing (PyAudio) for ASR, gTTS and pydub for audio playback.

Functions:
- authenticate a Twitter user (3-step log-in); re-log in based on stored access key
- prompts user for voice command (using audio)
- ASR to acquire voice command
- get the latest status of an arbitrary Twitter user or the authenticated user's wall feed
