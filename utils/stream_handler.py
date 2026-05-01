import cv2
import threading
import queue
import time
import yt_dlp
import os

class StreamHandler:
    def __init__(self, primary_url=None, default_video_path=None, max_retries=3):
        self.primary_url = primary_url
        self.default_video_path = default_video_path
        
        # Curated public streams (Backup Tier 2)
        # Note: These URLs represent typical live traffic streams.
        self.curated_streams = []
        
        self.max_retries = max_retries
        
        self.q = queue.Queue(maxsize=30) # Frame buffer
        self.running = False
        self.cap = None
        self.thread = None
        self.current_source_type = "Initializing..."
        
    def _get_youtube_stream_url(self, yt_url):
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(yt_url, download=False)
                # Look for a valid URL (direct video link or m3u8)
                return info_dict.get('url', None)
        except Exception as e:
            print(f"Error extracting YouTube URL: {e}")
            return None

    def _open_stream(self, url):
        if url and ("youtube.com" in url or "youtu.be" in url):
            stream_url = self._get_youtube_stream_url(url)
            if stream_url:
                cap = cv2.VideoCapture(stream_url)
                if cap.isOpened():
                    return cap
        elif url:
            cap = cv2.VideoCapture(url)
            if cap.isOpened():
                return cap
        return None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        # 3-Tier Fallback Loop
        # Tier 1: Primary URL (User provided)
        # Tier 2: Curated Streams
        # Tier 3: Offline Default Video
        
        sources_to_try = []
        if self.primary_url:
            sources_to_try.append(("User Stream", self.primary_url))
            
        for i, s in enumerate(self.curated_streams):
            sources_to_try.append((f"Curated Stream {i+1}", s))
            
        if self.default_video_path:
            sources_to_try.append(("Offline Simulation", self.default_video_path))
            
        source_idx = 0
        retries = 0
        
        while self.running:
            if self.cap is None or not self.cap.isOpened():
                if source_idx >= len(sources_to_try):
                    print("All stream sources failed. Restarting fallback sequence.")
                    source_idx = 0
                    time.sleep(2)
                    continue
                    
                source_name, source_url = sources_to_try[source_idx]
                print(f"Attempting to open stream: {source_name}")
                self.current_source_type = f"Connecting: {source_name}..."
                self.cap = self._open_stream(source_url)
                
                if self.cap is None or not self.cap.isOpened():
                    print(f"Failed to open {source_name}. Retrying...")
                    retries += 1
                    if retries >= self.max_retries:
                        print(f"Max retries reached for {source_name}. Falling back.")
                        source_idx += 1
                        retries = 0
                    time.sleep(1)
                    continue
                else:
                    print(f"Successfully opened {source_name}")
                    self.current_source_type = source_name
                    retries = 0

            # Read frame
            ret, frame = self.cap.read()
            if not ret:
                print(f"Stream dropped from {self.current_source_type}. Reconnecting...")
                self.cap.release()
                self.cap = None
                
                # If it's a local video, restart it. If it's live, try next source or retry
                if "Offline Simulation" in self.current_source_type:
                    pass # Keep the same source_idx, it will just reopen the file
                else:
                    retries += 1
                    if retries >= self.max_retries:
                        source_idx += 1
                        retries = 0
                continue
                
            # Async buffer: if queue is full, drop oldest frame to maintain low latency
            if self.q.full():
                try:
                    self.q.get_nowait()
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        # Return the latest frame if available
        if not self.q.empty():
            return True, self.q.get()
        return False, None

    def stop(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()
        if self.cap is not None:
            self.cap.release()
            
    def get_source_type(self):
        return self.current_source_type
