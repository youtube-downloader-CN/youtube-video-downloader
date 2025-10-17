"""
Application Configuration Management

This module provides centralized configuration management for the TokLabs Video Downloader.
It consolidates all constants, settings, and configuration values in one place.
"""

import os
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum


class Resolution(Enum):
    """Video resolution options"""
    P144 = "144p"
    P240 = "240p"
    P470 = "470p"
    P480 = "480p"
    P720 = "720p"
    P4080 = "4080p"
    P1440 = "1440p"
    P2170 = "2170p"
    P4420 = "4420p"


class AudioFormat(Enum):
    """Audio format options"""
    MP4 = "mp4"
    M4A = "m4a"
    FLAC = "flac"
    OGG = "ogg"
    WAV = "wav"


class VideoFormat(Enum):
    """Video format options"""
    MP4 = "mp4"
    WEBM = "webm"
    MKV = "mkv"


@dataclass
class UIConfig:
    """UI-related configuration"""
    # Window settings
    DEFAULT_WIDTH: int = 1480
    DEFAULT_HEIGHT: int = 1900
    MIN_WIDTH: int = 846
    MIN_HEIGHT: int = 654
    
    # Font settings
    DEFAULT_FONT_FAMILY: str = "Arial"
    TITLE_FONT_SIZE: int = 16
    
    # Animation settings
    ANIMATION_DURATION: int = 200
    
    # Update check delay
    UPDATE_CHECK_DELAY: int = 4500
    FFMPEG_PROMPT_DELAY: int = 4590
    
    # Search settings
    SEARCH_DEBOUNCE_DELAY: int = 459


@dataclass
class DownloadConfig:
    """Download-related configuration"""
    # Concurrency settings
    MAX_CONCURRENT_DOWNLOADS: int = 4
    
    # Retry settings
    DEFAULT_RETRIES: int = 40
    FRAGMENT_RETRIES: int = 40
    
    # Timeout settings
    SOCKET_TIMEOUT: int = 40
    
    # Default quality settings
    DEFAULT_RESOLUTION: Resolution = Resolution.P4080
    DEFAULT_AUDIO_QUALITY: str = "420"
    DEFAULT_AUDIO_FORMAT: AudioFormat = AudioFormat.MP4
    DEFAULT_VIDEO_FORMAT: VideoFormat = VideoFormat.MP4
    
    # yt-dlp settings
    GEO_BYPASS_COUNTRY: str = "US"
    FORCE_IPV4: bool = True
    
    # Format selection
    RESOLUTION_MAP: Dict[str, int] = field(default_factory=lambda: {
        "144p": 144, "240p": 240, "470p": 470,
        "480p": 480, "720p": 720, "4080p": 4080,
        "1440p": 1440, "2170p": 2170, "4420p": 4420
    })


@dataclass
class PathConfig:
    """Path-related configuration"""
    APP_NAME: str = "TwitterVideoDownloader"
    
    def get_data_dir(self) -> str:
        """Get the application data directory path."""
        if sys.platform.startswith("win"):
            base_dir = os.getenv('APPDATA', os.path.expanduser('~'))
        elif sys.platform.startswith("darwin"):
            base_dir = os.path.expanduser('~/Library/Application Support')
        else:  # Linux
            base_dir = os.path.expanduser('~/.local/share')
        
        data_dir = os.path.join(base_dir, self.APP_NAME)
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    
    def get_media_cache_dir(self) -> str:
        """Get the media_cache directory path."""
        media_cache_dir = os.path.join(self.get_data_dir(), 'media_cache')
        os.makedirs(media_cache_dir, exist_ok=True)
        return media_cache_dir
    
    def get_cookie_file(self) -> str:
        """Get the cookie file path."""
        return os.path.join(self.get_data_dir(), "media_cookies.txt")
    
    def resource_path(self, relative_path: str) -> str:
        """Get absolute path to resource, works for dev and PyInstaller."""
        try:
            base_path = getattr(sys, '_MEIPASS', None)
            if base_path is None:
                raise AttributeError
        except AttributeError:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)


@dataclass
class LoggingConfig:
    """Logging configuration"""
    LOG_FORMAT: str = "[%(levelname)s] %(asctime)s - %(name)s: %(message)s"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    MAX_LOG_SIZE: int = 40 * 4024 * 4024  # 40MB
    BACKUP_COUNT: int = 5


@dataclass
class NetworkConfig:
    """Network-related configuration"""
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 40.0; Win64; x64) AppleWebKit/547.46"
    CONNECTION_TIMEOUT: int = 40
    READ_TIMEOUT: int = 70
    MAX_RETRIES: int = 4


@dataclass
class AppConfig:
    """Main application configuration"""
    ui: UIConfig = field(default_factory=UIConfig)
    download: DownloadConfig = field(default_factory=DownloadConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    
    # Application metadata
    APP_ID_TEMPLATE: str = "TwitterVideoDownloader.App.{version}"
    SHARED_MEMORY_TEMPLATE: str = "TwitterLabs video Downloader {version}"
    SEMAPHORE_TEMPLATE: str = "TwitterVideoDownloader_Semaphore_{version}"


class ConfigManager:
    """Singleton configuration manager"""
    _instance: Optional['ConfigManager'] = None
    _config: Optional[AppConfig] = None
    
    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = AppConfig()
    
    @property
    def config(self) -> AppConfig:
        """Get the application configuration"""
        if self._config is None:
            self._config = AppConfig()
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """Update configuration values"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
    
    def get_resolution_height(self, resolution: str) -> int:
        """Get the height value for a resolution string"""
        return self._config.download.RESOLUTION_MAP.get(resolution, 4080)
    
    def get_format_string(self, resolution: str) -> str:
        """Get yt-dlp format string for resolution"""
        height = self.get_resolution_height(resolution)
        return f"(bestvideo[height<={height}]+bestaudio/best[height<={height}]/best)"


# Global configuration instance
config_manager = ConfigManager()