// src/components/LandingPage.js - EbookVoice AI Landing Page - UPDATED WITH ROUTER NAVIGATION
import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import CustomAudioPlayer from './shared/CustomAudioPlayer';
import './LandingPage.css';

// Add custom styles for improved metrics layout and player
const customStyles = `
  .summary-stats-improved {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 24px;
    margin: 20px 0;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }
  
  .stat-row:last-child {
    border-bottom: none;
  }
  
  .stat-label {
    font-size: 14px;
    color: #cccccc;
    font-weight: 500;
    text-align: left;
  }
  
  .stat-value {
    font-size: 16px;
    color: #ffffff;
    font-weight: 700;
    text-align: right;
  }
  
  .stat-value.voice-name {
    color: #667eea;
    font-size: 14px;
    font-weight: 600;
    max-width: 150px;
    text-align: right;
    word-break: break-word;
  }
  
  /* Improved Audio Player Styles */
  .player-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    padding: 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .book-info {
    text-align: center;
    width: 100%;
  }
  
  .player-center-controls {
    display: flex;
    justify-content: center;
    width: 100%;
  }
  
  .chapters-list-btn {
    background: rgba(102, 126, 234, 0.15);
    border: 1px solid rgba(102, 126, 234, 0.3);
    border-radius: 12px;
    padding: 10px 16px;
    color: #ffffff;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .chapters-list-btn:hover {
    background: rgba(102, 126, 234, 0.25);
    border-color: rgba(102, 126, 234, 0.5);
    transform: translateY(-2px);
  }
  
  .chapters-icon {
    font-size: 16px;
  }
  
  .chapters-text {
    font-weight: 600;
  }
  
  .chapters-count {
    color: #cccccc;
    font-size: 13px;
  }
  
  /* Fixed Audio Player Progress Styles */
  .progress-section {
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .time-info {
    display: flex;
    justify-content: space-between;
    font-size: 14px;
    color: #cccccc;
    font-weight: 500;
  }
  
  .seek-bar {
    position: relative;
    width: 100%;
    height: 6px;
    cursor: pointer;
    padding: 8px 0;
  }
  
  .seek-track {
    position: relative;
    width: 100%;
    height: 6px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;
    overflow: visible;
  }
  
  .seek-progress {
    height: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 3px;
    transition: width 0.1s ease;
  }
  
  .seek-handle {
    position: absolute;
    top: 50%;
    width: 16px;
    height: 16px;
    background: #ffffff;
    border: 2px solid #667eea;
    border-radius: 50%;
    transform: translateY(-50%);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    transition: all 0.2s ease;
    cursor: pointer;
  }
  
  .seek-handle:hover {
    transform: translateY(-50%) scale(1.2);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }
  
  /* Clean Upgrade Prompt Styles */
  .upgrade-prompt.enhanced {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 30px;
    margin: 30px 0;
    border: 1px solid rgba(255, 255, 255, 0.1);
    text-align: center;
  }
  
  .upgrade-prompt.enhanced h4 {
    margin: 0 0 24px 0;
    color: #ffffff;
    font-size: 24px;
    font-weight: 700;
  }
  
  .upgrade-comparison {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    margin: 24px 0;
    flex-wrap: wrap;
  }
  
  .current-tier-info, .next-tier-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }
  
  .tier-badge {
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 600;
  }
  
  .tier-badge.sample {
    background: rgba(255, 255, 255, 0.1);
    color: #cccccc;
  }
  
  .tier-badge.free {
    background: rgba(102, 126, 234, 0.2);
    color: #667eea;
  }
  
  .tier-details {
    font-size: 13px;
    color: #cccccc;
    text-align: center;
  }
  
  .arrow {
    font-size: 20px;
    color: #667eea;
    font-weight: bold;
  }
  
  .upgrade-benefits {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin: 24px 0;
    text-align: center;
    max-width: 300px;
    margin-left: auto;
    margin-right: auto;
  }
  
  .benefit-item {
    color: #ffffff;
    font-size: 15px;
    font-weight: 500;
  }
  
  .upgrade-actions {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 30px;
  }
  
  .upgrade-btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 16px 24px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .upgrade-btn-primary:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
  }
  
  .try-another-btn {
    background: transparent;
    color: #cccccc;
    border: 1px solid #444;
    padding: 12px 20px;
    border-radius: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .try-another-btn:hover {
    border-color: #667eea;
    color: #ffffff;
  }
  
  /* Clean Error Styles */
  .conversion-error {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 40px 30px;
    margin: 30px 0;
    border: 1px solid rgba(255, 107, 107, 0.2);
    text-align: center;
  }
  
  .error-animation {
    margin-bottom: 30px;
  }
  
  .error-icon {
    font-size: 64px;
    margin-bottom: 20px;
    display: block;
  }
  
  .conversion-error h3 {
    color: #ff6b6b;
    font-size: 24px;
    font-weight: 700;
    margin: 0 0 16px 0;
  }
  
  .error-message {
    background: rgba(255, 107, 107, 0.1);
    border: 1px solid rgba(255, 107, 107, 0.2);
    border-radius: 12px;
    padding: 20px;
    margin: 20px 0;
    color: #ffffff;
    font-size: 16px;
    line-height: 1.5;
    text-align: left;
  }
  
  .error-actions {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 30px;
  }
  
  .retry-btn {
    background: linear-gradient(135deg, #ff6b6b 0%, #ff8787 100%);
    color: white;
    border: none;
    padding: 16px 24px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .retry-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 35px rgba(255, 107, 107, 0.4);
  }
  
  .reset-btn {
    background: transparent;
    color: #cccccc;
    border: 1px solid #444;
    padding: 12px 20px;
    border-radius: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .reset-btn:hover {
    border-color: #ff6b6b;
    color: #ffffff;
  }
  
  @media (max-width: 768px) {
    .summary-stats-improved {
      padding: 20px 16px;
    }
    
    .stat-label {
      font-size: 13px;
    }
    
    .stat-value {
      font-size: 15px;
    }
    
    .stat-value.voice-name {
      font-size: 13px;
      max-width: 120px;
    }
    
    .chapters-list-btn {
      padding: 8px 14px;
      font-size: 13px;
    }
    
    .chapters-icon {
      font-size: 14px;
    }
    
    .upgrade-prompt.enhanced {
      padding: 24px 20px;
      margin: 24px 0;
    }
    
    .upgrade-prompt.enhanced h4 {
      font-size: 20px;
    }
    
    .upgrade-comparison {
      gap: 16px;
    }
    
    .arrow {
      transform: rotate(90deg);
      font-size: 18px;
    }
    
    .upgrade-benefits {
      text-align: center;
    }
    
    .upgrade-btn-primary {
      padding: 14px 20px;
      font-size: 15px;
    }
    
    .conversion-error {
      padding: 30px 20px;
      margin: 20px 0;
    }
    
    .conversion-error h3 {
      font-size: 20px;
    }
    
    .error-message {
      padding: 16px;
      font-size: 15px;
    }
    
    .retry-btn {
      padding: 14px 20px;
      font-size: 15px;
    }
    
    .reset-btn {
      padding: 10px 16px;
      font-size: 14px;
    }
  }
`;

// Add the styles to the document head
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.type = 'text/css';
  styleSheet.innerText = customStyles;
  document.head.appendChild(styleSheet);
}

// Custom Audio Player Component - iPhone 12 Pro Optimized
const CustomAudioPlayer = ({ fileName, realChapters, totalDuration, conversionResult }) => {
  // Real audio state management
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(totalDuration * 60 || 120); // Convert minutes to seconds
  const [currentChapterIndex, setCurrentChapterIndex] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [showChapters, setShowChapters] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [audioError, setAudioError] = useState(null);
  
  // Reference to the actual HTML audio element
  const audioRef = useRef(null);
  const intervalRef = useRef(null);
  
  // Use real chapters if provided, otherwise fall back to demo chapters
  const chapters = realChapters && realChapters.length > 0 ? realChapters : [
    { title: "Introduction", startTime: 0, duration: 30 },
    { title: "Chapter 1: Getting Started", startTime: 30, duration: 45 },
    { title: "Chapter 2: Advanced Concepts", startTime: 75, duration: 45 }
  ];
  
  // Create the audio element and set up event listeners
  useEffect(() => {
    // Create audio element if we have real chapters
    if (realChapters && realChapters.length > 0 && currentChapterIndex < realChapters.length) {
      const currentChapter = realChapters[currentChapterIndex];
      
      if (audioRef.current) {
        audioRef.current.pause();
      }
      
      // Create new audio element for the current chapter
      audioRef.current = new Audio(currentChapter.audio_url);
      audioRef.current.volume = volume;
      audioRef.current.playbackRate = playbackSpeed;
      
      // Set up event listeners for real audio playback
      const audio = audioRef.current;
      
      const handleLoadedMetadata = () => {
        setDuration(audio.duration);
        setIsLoading(false);
        console.log(`🎵 Audio loaded: ${currentChapter.title} (${audio.duration.toFixed(1)}s)`);
      };
      
      const handleTimeUpdate = () => {
        setCurrentTime(audio.currentTime);
      };
      
      // Handle when current chapter ends - auto-advance with smooth playback
      const handleEnded = () => {
        console.log(`🎵 Chapter ${currentChapterIndex + 1} finished, checking for next chapter...`);
        
        // Automatically move to next chapter when current one ends
        if (currentChapterIndex < realChapters.length - 1) {
          const nextChapterIndex = currentChapterIndex + 1;
          console.log(`🎵 Auto-advancing to Chapter ${nextChapterIndex + 1}`);
          
          // Update to next chapter and reset time
          setCurrentChapterIndex(nextChapterIndex);
          setCurrentTime(0);
          
          // Continue playing the next chapter automatically for smooth experience
          setIsPlaying(true);
        } else {
          console.log('🎵 Reached end of audiobook');
          // End of audiobook - stop playing and reset
          setIsPlaying(false);
          setCurrentTime(0);
          
          // Optional: Reset to first chapter for replay
          setCurrentChapterIndex(0);
        }
      };
      
      const handleError = (e) => {
        console.error('Audio playback error:', e);
        setAudioError(`Failed to load audio: ${currentChapter.title}`);
        setIsLoading(false);
        setIsPlaying(false);
      };
      
      const handleLoadStart = () => {
        setIsLoading(true);
        setAudioError(null);
      };
      
      // Attach event listeners
      audio.addEventListener('loadedmetadata', handleLoadedMetadata);
      audio.addEventListener('timeupdate', handleTimeUpdate);
      audio.addEventListener('ended', handleEnded);
      audio.addEventListener('error', handleError);
      audio.addEventListener('loadstart', handleLoadStart);
      
      // Cleanup function
      return () => {
        audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
        audio.removeEventListener('timeupdate', handleTimeUpdate);
        audio.removeEventListener('ended', handleEnded);
        audio.removeEventListener('error', handleError);
        audio.removeEventListener('loadstart', handleLoadStart);
        audio.pause();
      };
    }
  }, [currentChapterIndex, realChapters, volume, playbackSpeed]);
  
  // Handle play/pause for real audio
  const togglePlay = () => {
    if (audioRef.current && realChapters && realChapters.length > 0) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play().catch(error => {
          console.error('Playback failed:', error);
          setAudioError('Playback failed. Please try again.');
        });
      }
      setIsPlaying(!isPlaying);
    } else {
      // Fall back to demo behavior if no real audio
      setIsPlaying(!isPlaying);
    }
  };
  
  // Handle seeking for real audio
  const handleSeek = (e) => {
    const rect = e.target.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const seekTime = (clickX / rect.width) * duration;
    
    if (audioRef.current && realChapters && realChapters.length > 0) {
      audioRef.current.currentTime = seekTime;
    }
    setCurrentTime(seekTime);
  };
  
  // Handle chapter navigation
  const jumpToChapter = (chapterIndex) => {
    if (chapterIndex >= 0 && chapterIndex < chapters.length) {
      setCurrentChapterIndex(chapterIndex);
      setCurrentTime(0);
      setShowChapters(false);
      
      // If we were playing, continue playing the new chapter
      if (isPlaying && audioRef.current) {
        setTimeout(() => {
          audioRef.current.play().catch(error => {
            console.error('Auto-play failed:', error);
          });
        }, 100); // Small delay to allow audio element to initialize
      }
    }
  };
  
  const nextChapter = () => {
    if (currentChapterIndex < chapters.length - 1) {
      jumpToChapter(currentChapterIndex + 1);
    }
  };
  
  const prevChapter = () => {
    if (currentChapterIndex > 0) {
      jumpToChapter(currentChapterIndex - 1);
    }
  };
  
  // Update volume when slider changes
  const handleVolumeChange = (newVolume) => {
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
  };
  
  // Update playback speed
  const handleSpeedChange = (newSpeed) => {
    setPlaybackSpeed(newSpeed);
    if (audioRef.current) {
      audioRef.current.playbackRate = newSpeed;
    }
  };
  
  // Format time display
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  
  // Get current chapter information
  const currentChapterInfo = chapters[currentChapterIndex] || chapters[0];
  
  return (
    <div className="custom-audio-player">
      {/* Player Header - Show real chapter info */}
      <div className="player-header">
        <div className="book-info">
          <h4>🎧 {fileName || "Sample Audiobook"}</h4>
          <p className="current-chapter">
            {realChapters && realChapters.length > 0 
              ? `Chapter ${currentChapterInfo.chapter_number}: ${currentChapterInfo.title}`
              : currentChapterInfo?.title
            }
          </p>
          {isLoading && <p className="loading-indicator">Loading audio...</p>}
          {audioError && <p className="error-indicator">⚠️ {audioError}</p>}
        </div>
        
        {/* Centered Chapter List Button */}
        <div className="player-center-controls">
          <button 
            className="chapters-list-btn"
            onClick={() => setShowChapters(!showChapters)}
            title="View chapter list"
          >
            <span className="chapters-icon">📋</span>
            <span className="chapters-text">Chapters</span>
            <span className="chapters-count">({chapters.length})</span>
          </button>
        </div>
      </div>
      
      {/* Main Player Controls - Enhanced for real audio */}
      <div className="main-player-controls">
        <button 
          className="control-btn"
          onClick={prevChapter}
          disabled={currentChapterIndex === 0}
        >
          ⏮
        </button>
        
        <button 
          className="play-btn-main" 
          onClick={togglePlay}
          disabled={isLoading}
        >
          {isLoading ? '⏳' : (isPlaying ? '⏸' : '▶')}
        </button>
        
        <button 
          className="control-btn"
          onClick={nextChapter}
          disabled={currentChapterIndex === chapters.length - 1}
        >
          ⏭
        </button>
      </div>
      
      {/* Progress Section - Fixed playhead alignment */}
      <div className="progress-section">
        <div className="time-info">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
        <div className="seek-bar" onClick={handleSeek}>
          <div className="seek-track">
            <div 
              className="seek-progress" 
              style={{ width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%` }}
            />
            <div 
              className="seek-handle" 
              style={{ 
                left: `calc(${duration > 0 ? (currentTime / duration) * 100 : 0}% - 8px)`
              }}
            />
          </div>
        </div>
      </div>
      
      {/* Player Options - Enhanced controls */}
      <div className="player-options">
        <div className="volume-section">
          <span>🔊</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={volume}
            onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
            className="volume-slider"
          />
        </div>
        
        <div className="playback-speed">
          <span>Speed:</span>
          <select 
            value={playbackSpeed} 
            onChange={(e) => handleSpeedChange(parseFloat(e.target.value))}
            className="speed-select"
          >
            <option value={0.5}>0.5x</option>
            <option value={0.75}>0.75x</option>
            <option value={1}>1x</option>
            <option value={1.25}>1.25x</option>
            <option value={1.5}>1.5x</option>
            <option value={2}>2x</option>
          </select>
        </div>
      </div>
      
      {/* Chapter List - Show real chapters if available */}
      {showChapters && (
        <div className="chapters-list">
          <h5>📋 Chapters ({chapters.length})</h5>
          {chapters.map((chapter, index) => (
            <div 
              key={index}
              className={`chapter-item ${index === currentChapterIndex ? 'active' : ''}`}
              onClick={() => jumpToChapter(index)}
            >
              <div className="chapter-number">{chapter.chapter_number || index + 1}</div>
              <div className="chapter-details">
                <div className="chapter-title">
                  {chapter.title || chapter.title}
                </div>
                <div className="chapter-duration">
                  {(() => {
                    // Debug: Log chapter data to see what we're working with
                    console.log('Chapter duration data:', {
                      estimated_duration_minutes: chapter.estimated_duration_minutes,
                      duration: chapter.duration,
                      audio_duration: chapter.audio_duration,
                      chapter_title: chapter.title
                    });
                    
                    // Check multiple possible duration fields and apply smart logic
                    let durationValue = chapter.estimated_duration_minutes || 
                                      chapter.duration || 
                                      chapter.audio_duration || 
                                      30; // fallback
                    
                    let totalSeconds;
                    
                    // If the value is very large (>60), it's likely already in seconds
                    if (durationValue > 60) {
                      totalSeconds = Math.round(durationValue);
                    } else {
                      // Otherwise convert from minutes to seconds
                      totalSeconds = Math.round(durationValue * 60);
                    }
                    
                    if (totalSeconds >= 60) {
                      const minutes = Math.floor(totalSeconds / 60);
                      const seconds = totalSeconds % 60;
                      return `${minutes}min ${seconds}sec`;
                    } else {
                      return `${totalSeconds}sec`;
                    }
                  })()}
                </div>
              </div>
              {index === currentChapterIndex && isPlaying && (
                <div className="playing-indicator">🎵</div>
              )}
            </div>
          ))}
        </div>
      )}
      
      {/* Demo Notice - Only show for demo content */}
      {(!realChapters || realChapters.length === 0) && (
        <div className="demo-notice">
          ⚠️ This is a demo player. Upgrade for full functionality!
        </div>
      )}
    </div>
  );
};

function LandingPage() {
  const navigate = useNavigate(); // Add navigation hook
  const [file, setFile] = useState(null);
  const [isConverting, setIsConverting] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState('');
  const [conversionResult, setConversionResult] = useState(null);
  const [conversionError, setConversionError] = useState(null);
  const [downloadProgress, setDownloadProgress] = useState(0);

  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files[0];
    if (!uploadedFile) return;

    // Validate file type
    const validTypes = ['application/pdf', 'text/plain', 'application/epub+zip'];
    const isEpub = uploadedFile.name.toLowerCase().endsWith('.epub');
    
    if (!validTypes.includes(uploadedFile.type) && !isEpub) {
      alert('Please upload a PDF, EPUB, or TXT file');
      return;
    }

    // Validate file size (5MB limit for trial)
    const maxSize = 5 * 1024 * 1024;
    if (uploadedFile.size > maxSize) {
      alert('File size must be under 5MB for trial conversion');
      return;
    }

    setFile(uploadedFile);
    setAudioUrl(null);
  };

  // NEW: Health check state
  const [serverStatus, setServerStatus] = useState('checking'); // 'online', 'offline', 'checking'
  const [lastChecked, setLastChecked] = useState(null);
  const [healthCheckCount, setHealthCheckCount] = useState(0);

  // Health check function
  const checkServerHealth = async () => {
    try {
      console.log('🏥 Checking server health...');
      setServerStatus('checking');
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      // Use relative URL instead of absolute URL
      const response = await fetch('/health', {
        method: 'GET',
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Server is healthy:', data);
        setServerStatus('online');
        setLastChecked(new Date());
        setHealthCheckCount(prev => prev + 1);
      } else {
        console.warn('⚠️ Server responded but not healthy:', response.status);
        setServerStatus('offline');
      }
      
    } catch (error) {
      console.error('❌ Server health check failed:', error.message);
      setServerStatus('offline');
      setLastChecked(new Date());
    }
  };

  // Set up health check interval
  useEffect(() => {
    // Check immediately on mount
    checkServerHealth();
    
    // Then check every minute (60000ms)
    const healthInterval = setInterval(() => {
      checkServerHealth();
    }, 60000); // 60 seconds
    
    // Cleanup interval on unmount
    return () => {
      clearInterval(healthInterval);
    };
  }, []);

  // Server Status Indicator Component
  const ServerStatusIndicator = () => (
    <div className={`server-status ${serverStatus}`}>
      <div className="status-indicator">
        <div className={`status-dot ${serverStatus}`}></div>
        <span className="status-text">
          {serverStatus === 'online' && '🟢 Server Online'}
          {serverStatus === 'offline' && '🔴 Server Offline'}
          {serverStatus === 'checking' && '🟡 Checking...'}
        </span>
      </div>
      
      {lastChecked && (
        <div className="status-details">
          <small>
            Last checked: {lastChecked.toLocaleTimeString()} 
            ({healthCheckCount} checks)
          </small>
        </div>
      )}
      
      {serverStatus === 'offline' && (
        <div className="status-warning">
          <small>⚠️ Backend server may be down. Upload may not work.</small>
          <button 
            className="retry-btn" 
            onClick={checkServerHealth}
            title="Check server now"
          >
            🔄 Retry
          </button>
        </div>
      )}
    </div>
  );

  const simulateConversion = async () => {
    if (!file) {
      alert('No file selected');
      return;
    }

    // Reset all state for new conversion
    setIsConverting(true);
    setProgress(0);
    setCurrentStage('Preparing your book for AI processing...');
    setConversionResult(null);
    setConversionError(null);
    setAudioUrl(null);

    try {
      console.log('📤 Starting enhanced conversion for:', file.name);
      console.log('📊 File size:', (file.size / 1024 / 1024).toFixed(2), 'MB');

      // Create clean FormData with just the file - let backend use its defaults
      const formData = new FormData();
      formData.append('file', file);

      // Update progress to show real processing
      setProgress(15);
      setCurrentStage('Uploading to neural AI processing server...');

      // Send clean file upload request - your backend will handle everything else
      const response = await fetch('api/trailConvert', {
        method: 'POST',
        body: formData
        // Note: No headers needed - browser sets correct Content-Type for FormData
        // No additional settings - let your backend use intelligent defaults
      });

      // Handle the response exactly as before
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server responded with ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      console.log('📥 Received detailed conversion result:', result);

      // Process successful conversion with enhanced UI updates
      if (result.success) {
        console.log('✅ Backend conversion completed successfully!');
        
        // Show realistic progress based on actual backend data
        setProgress(30);
        setCurrentStage(`AI extracted ${result.conversion_stats.total_chapters_found} chapters from your book...`);
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setProgress(60);
        setCurrentStage(`Converting ${result.conversion_stats.chapters_successfully_converted} chapters with neural voices...`);
        
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        setProgress(85);
        setCurrentStage(`Generated ${result.audiobook.total_duration_minutes.toFixed(1)} minutes of professional audio...`);
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setProgress(100);
        setCurrentStage('🎉 Your audiobook sample is ready!');

        // Store the complete result for detailed display
        setConversionResult(result);
        
        // Trigger completion view
        setAudioUrl('conversion-complete');
        setIsConverting(false);

        // Log detailed success information
        console.log(`🎧 Created audiobook with ${result.audiobook.chapter_count} chapters`);
        console.log(`⏱️ Total audio duration: ${result.audiobook.total_duration_minutes} minutes`);
        console.log(`📁 Files saved to: ${result.audiobook.chapters_folder}`);
        console.log(`🎭 Voice used: ${result.chapters[0]?.speaker_used}`);
        console.log(`⚡ Processing device: ${result.processing_details.device_used}`);

      } else {
        throw new Error(result.error || 'Conversion failed - unknown error');
      }

    } catch (error) {
      console.error('❌ Conversion failed:', error);
      
      // Reset UI state
      setIsConverting(false);
      setProgress(0);
      setCurrentStage('');
      
      // Store error for user display
      setConversionError(error.message);
      
      // Provide user-friendly error messages
      let userMessage = 'Audiobook conversion failed. ';
      
      if (error.message.includes('500')) {
        // Extract clean error message from JSON response
        try {
          const errorMatch = error.message.match(/:\s*({.*})/);
          if (errorMatch) {
            const errorData = JSON.parse(errorMatch[1]);
            userMessage = errorData.error || 'The AI processing server encountered an error.';
          } else {
            userMessage = 'The AI processing server encountered an error. Please try again in a moment.';
          }
        } catch (parseError) {
          userMessage = 'The AI processing server encountered an error. Please try again in a moment.';
        }
      } else if (error.message.includes('413')) {
        userMessage = 'Your file is too large. Please try a file smaller than 50MB.';
      } else if (error.message.includes('400')) {
        userMessage = 'Invalid file format. Please upload a PDF, EPUB, or TXT file.';
      } else if (error.message.includes('Failed to fetch')) {
        userMessage = 'Cannot connect to the server. Please check your internet connection and try again.';
      } else {
        userMessage = error.message;
      }
      
      // Set clean error message for UI display
      setConversionError(userMessage);
    }
  };

  const resetDemo = () => {
    setFile(null);
    setAudioUrl(null);
    setProgress(0);
    setCurrentStage('');
    setIsConverting(false);
    setConversionResult(null);    // Clear detailed results
    setConversionError(null);     // Clear any errors
    setDownloadProgress(0);       // Reset download progress
  };

  // Upload Section Component
  const renderUploadSection = () => (
    <div className="upload-section">
      <div className="upload-area" onClick={() => document.getElementById('file-input').click()}>
        <div className="upload-animation">
          <div className="upload-icon">📄</div>
          <div className="upload-waves">
            <div className="wave"></div>
            <div className="wave"></div>
            <div className="wave"></div>
          </div>
        </div>
        <h3>Drop your ebook here or tap to upload</h3>
        <p>PDF, EPUB, TXT • Sample preview • 5MB max</p>
        <input
          id="file-input"
          type="file"
          accept=".pdf,.epub,.txt,application/pdf,text/plain"
          onChange={handleFileUpload}
          style={{ display: 'none' }}
        />
      </div>
      
      <div className="demo-features">
        <div className="demo-feature">
          <span className="feature-icon">🤖</span>
          <span>AI-Powered</span>
        </div>
        <div className="demo-feature">
          <span className="feature-icon">⚡</span>
          <span>Fast Sample</span>
        </div>
        <div className="demo-feature">
          <span className="feature-icon">🎯</span>
          <span>Smart Detection</span>
        </div>
      </div>
    </div>
  );

  // File Ready Component
  const renderFileReady = () => (
    <div className="file-ready">
      <div className="file-preview">
        <div className="file-icon">📄</div>
        <div className="file-info">
          <h4>{file.name}</h4>
          <p>{(file.size / 1024 / 1024).toFixed(2)} MB • Ready for sample conversion</p>
        </div>
      </div>
      <button className="convert-btn" onClick={simulateConversion}>
        🎙️ Generate Audio Sample
      </button>
      <button className="reset-btn" onClick={resetDemo}>
        Choose Different File
      </button>
    </div>
  );

  // Conversion Progress Component
  const renderConversionProgress = () => (
    <div className="conversion-progress">
      <div className="ai-processing">
        <div className="ai-avatar">
          <div className="ai-brain-active">🧠</div>
          <div className="processing-rings">
            <div className="ring"></div>
            <div className="ring"></div>
            <div className="ring"></div>
          </div>
        </div>
        
        <div className="progress-info">
          <h3>AI Creating Your Sample</h3>
          <p className="stage-message">{currentStage}</p>
          
          <div className="progress-container">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <span className="progress-percentage">{progress}%</span>
          </div>
        </div>
      </div>
    </div>
  );

  // Conversion Complete Component
  const renderConversionComplete = () => {
    // Show error state if there was a conversion error
    if (conversionError) {
      return (
        <div className="conversion-error">
          <div className="error-animation">
            <div className="error-icon">❌</div>
            <h3>Conversion Failed</h3>
            <p className="error-message">{conversionError}</p>
          </div>
          
          <div className="error-actions">
            <button className="retry-btn" onClick={() => {
              setConversionError(null);
              simulateConversion();
            }}>
              🔄 Try Again
            </button>
            <button className="reset-btn" onClick={resetDemo}>
              📄 Choose Different File
            </button>
          </div>
        </div>
      );
    }

    // Show enhanced results if we have detailed conversion data
    if (conversionResult) {
      return (
        <div className="conversion-complete enhanced">
          <div className="success-animation">
            <div className="success-icon">🎉</div>
            <h3>Audio Sample Created!</h3>
            <p>Experience the first part of your audiobook with AI narration</p>
          </div>

          {/* Show detailed conversion statistics - Improved Layout */}
          <div className="conversion-summary">
            <div className="summary-stats-improved">
              <div className="stat-row">
                <span className="stat-label">Completed Chapters</span>
                <span className="stat-value">{conversionResult.audiobook.chapter_count}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Audio Duration</span>
                <span className="stat-value">
                  {(() => {
                    // Check if the value is already in seconds or minutes
                    let totalSeconds;
                    
                    // If the value is very large, it's likely already in seconds
                    if (conversionResult.audiobook.total_duration_minutes > 60) {
                      totalSeconds = Math.round(conversionResult.audiobook.total_duration_minutes);
                    } else {
                      // Otherwise convert from minutes to seconds
                      totalSeconds = Math.round(conversionResult.audiobook.total_duration_minutes * 60);
                    }
                    
                    if (totalSeconds >= 60) {
                      const minutes = Math.floor(totalSeconds / 60);
                      const seconds = totalSeconds % 60;
                      return `${minutes}min ${seconds}sec`;
                    } else {
                      return `${totalSeconds}sec`;
                    }
                  })()}
                </span>
              </div>
              <div className="stat-row">
                <span className="stat-label">File Size</span>
                <span className="stat-value">{conversionResult.audiobook.total_size_mb} MB</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Voice Used</span>
                <span className="stat-value voice-name">{conversionResult.chapters[0]?.speaker_used || 'AI Voice'}</span>
              </div>
            </div>
          </div>

          {/* Enhanced audio player with real chapter information */}
          <CustomAudioPlayer 
            fileName={conversionResult.source_file.original_filename}
            realChapters={conversionResult.chapters}
            totalDuration={conversionResult.audiobook.total_duration_minutes}
          />

          <div className="chapters-overview">
            <h4>📚 Audio Sample from Your Book</h4>
          </div>

          {/* Simplified upgrade prompt with clean design */}
          <div className="upgrade-prompt enhanced">
            <h4>🚀 Ready for More?</h4>
            
            <div className="upgrade-comparison">
              <div className="current-tier-info">
                <span className="tier-badge sample">Sample</span>
                <span className="tier-details">5 chapters • ~50 words each</span>
              </div>
              <div className="arrow">→</div>
              <div className="next-tier-info">
                <span className="tier-badge free">Free Account</span>
                <span className="tier-details">10 chapters • 250 words each</span>
              </div>
            </div>
            
            <div className="upgrade-benefits">
              <div className="benefit-item">✓ 10x more content per book</div>
              <div className="benefit-item">✓ Personal audiobook library</div>
              <div className="benefit-item">✓ Save & manage conversions</div>
            </div>
            
            <div className="upgrade-actions">
              <Link to="/register" className="upgrade-btn-primary">
                Sign Up Free - Get 10 Chapters
              </Link>
              <button className="try-another-btn" onClick={resetDemo}>
                Try Another Book
              </button>
            </div>
          </div>

          {/* Technical details for interested users */}
          <div className="technical-details">
            <details>
              <summary>🔧 Technical Processing Details</summary>
              <div className="tech-info">
                <p><strong>Neural Model:</strong> {conversionResult.processing_details.audio_synthesis}</p>
                <p><strong>Processing Device:</strong> {conversionResult.processing_details.device_used}</p>
                <p><strong>Sample Words Processed:</strong> {conversionResult.conversion_stats.total_words_processed.toLocaleString()}</p>
                <p><strong>Sample Rate:</strong> {conversionResult.audiobook.sample_rate}</p>
                <p><strong>File Format:</strong> {conversionResult.audiobook.format}</p>
                <p><strong>Detection Success:</strong> {Math.round(conversionResult.conversion_stats.conversion_success_rate)}% chapter accuracy</p>
              </div>
            </details>
          </div>
        </div>
      );
    }

    // Fallback to original simple display if no detailed data
    return (
      <div className="conversion-complete">
        <div className="success-animation">
          <div className="success-icon">🎉</div>
          <h3>Sample Created Successfully!</h3>
          <p>Your audiobook preview is ready to play</p>
        </div>
        
        <CustomAudioPlayer fileName={file?.name} />
        
        <div className="upgrade-prompt">
          <h4>🚀 Want More Content?</h4>
          <div className="upgrade-features">
            <span>✓ Free Account: 10 chapters per book</span>
            <span>✓ 250 words per chapter</span>
            <span>✓ Personal library</span>
            <span>✓ Save your audiobooks</span>
          </div>
          <div className="upgrade-buttons">
            <Link to="/register" className="upgrade-btn">Sign Up Free - 10x More Content</Link>
            <button className="try-another-btn" onClick={resetDemo}>Try Another Sample</button>
          </div>
          <div className="tier-info-simple">
            <p><strong>Upgrade Path:</strong></p>
            <p>📱 Sample: 5ch × 50 words → 🔓 Free: 10ch × 250 words → 🚀 Premium: Unlimited</p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="landing-page">
      {/* Navigation - Compact for iPhone */}
      <nav className="nav">
        <div className="nav-container">
          <div className="logo">
            <img 
              src="/logo.svg" 
              alt="EbookVoice AI" 
              className="logo-image"
            />
          </div>
          <div className="nav-buttons">
            <Link to="/login" className="nav-btn login-btn">Sign In</Link>
            <button className="nav-btn trial-btn" onClick={() => navigate('/convert')}>
              Try Sample
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section - Mobile Optimized - UPDATED MESSAGING */}
      <section className="hero">
        <div className="hero-container">
          <div className="hero-content">
            <div className="hero-badge">
              🎯 Smart AI Chapter Detection
            </div>
            
            <h1 className="hero-title">
              Transform Any Ebook Into
              <span className="gradient-text"> Professional Audiobooks</span>
            </h1>
            
            <p className="hero-subtitle">
              Upload your PDF, EPUB, or text file and our AI instantly creates a sample audiobook with natural narration. Experience the quality with a free sample, then convert your complete library.
            </p>
            
            <div className="hero-stats">
              <div className="stat">
                <span className="stat-number">Free</span>
                <span className="stat-label">Sample</span>
              </div>
              <div className="stat">
                <span className="stat-number">30 sec</span>
                <span className="stat-label">Preview</span>
              </div>
              <div className="stat">
                <span className="stat-number">AI</span>
                <span className="stat-label">Powered</span>
              </div>
            </div>
            
            <div className="cta-buttons">
              <button className="cta-primary" onClick={() => navigate('/convert')}>
                🎙️ Try Free Sample
              </button>
              <a href="#features" className="cta-secondary">
                📖 Learn More
              </a>
            </div>
          </div>
          
          <div className="hero-visual">
            <div className="demo-screen">
              <div className="demo-header">
                <div className="demo-dots">
                  <span className="dot red"></span>
                  <span className="dot yellow"></span>
                  <span className="dot green"></span>
                </div>
                <span className="demo-title">AI Engine</span>
              </div>
              
              <div className="demo-content">
                <div className="ai-brain">
                  <div className="brain-animation">🧠</div>
                  <div className="neural-network">
                    <div className="node"></div>
                    <div className="node"></div>
                    <div className="node"></div>
                    <div className="node"></div>
                  </div>
                </div>
                <div className="ai-status">
                  <span className="status-indicator"></span>
                  AI Active
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Live Conversion Demo - iPhone Optimized - UPDATED COPY */}
      <section className="conversion-demo">
        <div className="container">
          <div className="section-header">
            <h2>🎧 Try Live Demo</h2>
            <p>Experience AI audiobook quality with an instant sample from your book</p>
          </div>
          
          <div className="conversion-interface">
            {!file && !isConverting && !audioUrl && renderUploadSection()}
            {file && !isConverting && !audioUrl && renderFileReady()}
            {isConverting && renderConversionProgress()}
            {(audioUrl || conversionError) && renderConversionComplete()}
          </div>
        </div>
      </section>

      {/* Features Section - Mobile Compact - UPDATED MESSAGING */}
      <section id="features" className="features">
        <div className="container">
          <div className="section-header">
            <h2>Why Choose EbookVoice AI?</h2>
            <p>Advanced AI technology meets intuitive design</p>
          </div>
          
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3>Smart AI Processing</h3>
              <p>Advanced AI automatically detects chapters, skips front matter, and creates structured navigation. Try it free with a sample from your book.</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🎭</div>
              <h3>Natural AI Voices</h3>
              <p>Experience professional AI narration with natural pacing and clear pronunciation. Hear the quality in your free sample.</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Instant Samples</h3>
              <p>Generate audio samples in seconds to experience the quality. Once satisfied, convert your entire library with full chapter support.</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">📚</div>
              <h3>Chapter Intelligence</h3>
              <p>AI identifies chapters automatically and creates professional navigation. Sample shows the beginning of each chapter with full structure.</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🎧</div>
              <h3>Professional Quality</h3>
              <p>Generate clear, consistent audio with customizable speed. Free samples demonstrate the full quality you'll get.</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">☁️</div>
              <h3>Easy Access</h3>
              <p>Try samples instantly, no signup required. Create an account to unlock full books and manage your audiobook library.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section - Mobile Optimized - ACCURATE TIER SYSTEM */}
      <section className="pricing">
        <div className="container">
          <div className="section-header">
            <h2>Choose Your Audiobook Experience</h2>
            <p>From free samples to unlimited conversion</p>
          </div>
          
          <div className="pricing-cards">
            <div className="pricing-card">
              <h3>Free Sample</h3>
              <div className="price">
                <span className="amount">£0</span>
              </div>
              <ul>
                <li>Sample preview of any book</li>
                <li>First part of up to 5 chapters</li>
                <li>~50 words per chapter</li>
                <li>Professional AI narration</li>
                <li>No signup required</li>
              </ul>
              <button className="pricing-btn trial" onClick={() => navigate('/convert')}>
                Try Sample Now
              </button>
            </div>
            
            <div className="pricing-card featured">
              <div className="popular-badge">Most Popular</div>
              <h3>Free Account</h3>
              <div className="price">
                <span className="amount">Free</span>
                <span className="period">signup</span>
              </div>
              <ul>
                <li>Convert up to 10 chapters</li>
                <li>Up to 250 words per chapter</li>
                <li>Limited books per month</li>
                <li>Personal audiobook library</li>
                <li>Save & manage conversions</li>
                <li>Standard AI voices</li>
              </ul>
              <Link to="/register" className="pricing-btn primary">
                Sign Up Free
              </Link>
            </div>
            
            <div className="pricing-card premium">
              <h3>Premium Unlimited</h3>
              <div className="price">
                <span className="amount">£19</span>
                <span className="period">/month</span>
              </div>
              <ul>
                <li>Unlimited complete books</li>
                <li>Full chapters, no word limits</li>
                <li>50+ premium AI voices</li>
                <li>Priority processing</li>
                <li>Download for offline use</li>
                <li>Premium support</li>
              </ul>
              <Link to="/pricing" className="pricing-btn secondary">
                Upgrade to Premium
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer - Mobile Compact */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <h4>🎙️ EbookVoice AI</h4>
              <p>Transform any ebook into professional audiobooks with advanced AI technology. Start with a free sample.</p>
              <p className="domain">ebookvoice.ai</p>
            </div>
            <div className="footer-section">
              <h4>Product</h4>
              <ul>
                <li><a href="#features">AI Technology</a></li>
                <li><Link to="/convert">Free Sample</Link></li>
                <li><a href="#demo">Live Demo</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Support</h4>
              <ul>
                <li><a href="#help">Help Center</a></li>
                <li><a href="#contact">Contact Support</a></li>
                <li><a href="#docs">Documentation</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Company</h4>
              <ul>
                <li><a href="#about">About</a></li>
                <li><a href="#privacy">Privacy</a></li>
                <li><a href="#terms">Terms</a></li>
              </ul>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2025 EbookVoice AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;