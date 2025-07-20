// src/App.js - EbookVoice AI Landing Page - HONEST STATISTICS VERSION
import React, { useState, useEffect, useRef } from 'react';
import './App.css';

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
      
      const handleEnded = () => {
        // Automatically move to next chapter when current one ends
        if (currentChapterIndex < realChapters.length - 1) {
          setCurrentChapterIndex(prev => prev + 1);
        } else {
          setIsPlaying(false);
          setCurrentTime(0);
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
        <button 
          className="chapters-btn"
          onClick={() => setShowChapters(!showChapters)}
        >
          📑 ({chapters.length})
        </button>
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
      
      {/* Progress Section - Real audio progress */}
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
            >
              <div className="seek-handle" style={{ right: 0 }}></div>
            </div>
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
                  {chapter.estimated_duration_minutes 
                    ? `${chapter.estimated_duration_minutes.toFixed(1)} min`
                    : formatTime(chapter.duration || 30)
                  }
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

function App() {
  const [showTrial, setShowTrial] = useState(false);
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
// Replace your existing checkServerHealth function with this:
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

// Replace your simulateConversion function with this EXACT version from ConversionPage.js:

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
    const response = await fetch('api/fullconvert', {
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
      setCurrentStage('🎉 Your audiobook is ready!');

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
      userMessage += 'The AI processing server encountered an error. Please try again in a moment.';
    } else if (error.message.includes('413')) {
      userMessage += 'Your file is too large. Please try a file smaller than 50MB.';
    } else if (error.message.includes('400')) {
      userMessage += 'Invalid file format. Please upload a PDF, EPUB, or TXT file.';
    } else if (error.message.includes('Failed to fetch')) {
      userMessage += 'Cannot connect to the server. Please check your internet connection and try again.';
    } else {
      userMessage += error.message;
    }
    
    alert(userMessage);
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
        <p>PDF, EPUB, TXT • 2-min preview • 5MB max</p>
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
          <span>5 minutes</span>
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
          <p>{(file.size / 1024 / 1024).toFixed(2)} MB • Ready for AI conversion</p>
        </div>
      </div>
      <button className="convert-btn" onClick={simulateConversion}>
        🎙️ Convert with AI
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
          <h3>AI Converting Your Book</h3>
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
          <h3>Professional Audiobook Created!</h3>
          <p>Your book has been converted using advanced neural AI synthesis</p>
        </div>

        {/* Show detailed conversion statistics */}
        <div className="conversion-summary">
          <div className="summary-stats">
            <div className="stat-item">
              <span className="stat-number">{conversionResult.audiobook.chapter_count}</span>
              <span className="stat-label">Chapters</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{Math.round(conversionResult.audiobook.total_duration_minutes)}</span>
              <span className="stat-label">Minutes</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{conversionResult.audiobook.total_size_mb}</span>
              <span className="stat-label">MB</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{Math.round(conversionResult.conversion_stats.conversion_success_rate)}%</span>
              <span className="stat-label">Success</span>
            </div>
          </div>
          
          <div className="quality-indicators">
            <div className="quality-badge">🧠 Neural AI</div>
            <div className="quality-badge">🎭 {conversionResult.chapters[0]?.speaker_used}</div>
            <div className="quality-badge">⚡ {conversionResult.processing_details.device_used.toUpperCase()}</div>
          </div>
        </div>

        {/* Enhanced audio player with real chapter information */}
        <CustomAudioPlayer 
          fileName={conversionResult.source_file.original_filename}
          realChapters={conversionResult.chapters}
          totalDuration={conversionResult.audiobook.total_duration_minutes}
        />

        {/* Show actual chapters from the conversion */}
        <div className="chapters-overview">
          <h4>📚 Your Audiobook Chapters</h4>
          <div className="chapters-list-summary">
            {conversionResult.chapters.slice(0, 4).map((chapter, index) => (
              <div key={index} className="chapter-summary-item">
                <span className="chapter-number">Ch {chapter.chapter_number}</span>
                <span className="chapter-title">{chapter.title.substring(0, 30)}...</span>
                <span className="chapter-duration">{chapter.estimated_duration_minutes.toFixed(1)}min</span>
              </div>
            ))}
            {conversionResult.chapters.length > 4 && (
              <div className="more-chapters">
                + {conversionResult.chapters.length - 4} more chapters
              </div>
            )}
          </div>
        </div>

        {/* Enhanced upgrade prompt with real data */}
        <div className="upgrade-prompt enhanced">
          <h4>🚀 Your Professional Audiobook is Ready!</h4>
          <div className="upgrade-features">
            <span>✓ {conversionResult.audiobook.chapter_count} chapters professionally converted</span>
            <span>✓ {Math.round(conversionResult.audiobook.total_duration_minutes)} minutes of neural-quality audio</span>
            <span>✓ AI voice: {conversionResult.chapters[0]?.speaker_used}</span>
            <span>✓ Smart chapter detection and navigation</span>
          </div>
          
          <div className="conversion-quality-info">
            <p>🎧 <strong>Audio Quality:</strong> {conversionResult.audiobook.quality}</p>
            <p>⚡ <strong>Processing:</strong> Completed in {conversionResult.conversion_stats.total_processing_time_seconds}s</p>
            <p>📊 <strong>Efficiency:</strong> {Math.round(conversionResult.conversion_stats.processing_efficiency_words_per_second)} words/second</p>
          </div>
          
          <div className="upgrade-buttons">
            <button className="upgrade-btn">
              📥 Download Complete Audiobook - £19/month
            </button>
            <button className="try-another-btn" onClick={resetDemo}>
              🔄 Convert Another Book
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
              <p><strong>Words Processed:</strong> {conversionResult.conversion_stats.total_words_processed.toLocaleString()}</p>
              <p><strong>Sample Rate:</strong> {conversionResult.audiobook.sample_rate}</p>
              <p><strong>File Format:</strong> {conversionResult.audiobook.format}</p>
              <p><strong>Audio Files Location:</strong> {conversionResult.audiobook.chapters_folder}</p>
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
        <h3>Conversion Successful!</h3>
        <p>Your audiobook demo is ready to play</p>
      </div>
      
      <CustomAudioPlayer fileName={file?.name} />
      
      <div className="upgrade-prompt">
        <h4>🚀 Unlock Full Features</h4>
        <div className="upgrade-features">
          <span>✓ Full book conversion</span>
          <span>✓ Premium voices</span>
          <span>✓ Unlimited downloads</span>
          <span>✓ Batch processing</span>
        </div>
        <div className="upgrade-buttons">
          <button className="upgrade-btn">Upgrade to Pro - £19/month</button>
          <button className="try-another-btn" onClick={resetDemo}>Try Another Book</button>
        </div>
      </div>
    </div>
  );
};

  return (
    <div className="app">
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
            <button className="nav-btn login-btn">Sign In</button>
            <button className="nav-btn trial-btn" onClick={() => setShowTrial(true)}>
              Try Free
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section - Mobile Optimized - HONEST STATS */}
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
              Upload your PDF, EPUB, or text file and our AI converts it to natural-sounding audiobooks with smart chapter detection. Full book conversion typically takes 5 minutes.
            </p>
            
            <div className="hero-stats">
              <div className="stat">
                <span className="stat-number">Beta</span>
                <span className="stat-label">Early Access</span>
              </div>
              <div className="stat">
                <span className="stat-number">5 min</span>
                <span className="stat-label">Full Book</span>
              </div>
              <div className="stat">
                <span className="stat-number">AI</span>
                <span className="stat-label">Powered</span>
              </div>
            </div>
            
            <div className="cta-buttons">
              <button className="cta-primary" onClick={() => setShowTrial(true)}>
                🎙️ Try Free Demo
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

      {/* Live Conversion Demo - iPhone Optimized */}
      <section className="conversion-demo">
        <div className="container">
          <div className="section-header">
            <h2>🎧 Try Live Demo</h2>
            <p>Experience AI audiobook conversion - 2 minute preview</p>
          </div>
          
          <div className="conversion-interface">
            {!file && !isConverting && !audioUrl && renderUploadSection()}
            {file && !isConverting && !audioUrl && renderFileReady()}
            {isConverting && renderConversionProgress()}
            {(audioUrl || conversionError) && renderConversionComplete()}
          </div>
        </div>
      </section>

      {/* Features Section - Mobile Compact */}
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
              <p>Advanced AI automatically detects chapters, skips front matter, and creates structured navigation for professional audiobooks.</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🎭</div>
              <h3>Natural AI Voices</h3>
              <p>Choose from AI voices designed for audiobook narration with natural pacing and clear pronunciation.</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Efficient Processing</h3>
              <p>Convert full books in approximately 5 minutes. Our AI infrastructure processes your content efficiently and accurately.</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">📚</div>
              <h3>Smart Chapter Detection</h3>
              <p>AI automatically identifies chapters and creates navigation, making your audiobooks professionally structured and easy to navigate.</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🎧</div>
              <h3>Quality Audio Output</h3>
              <p>Generate clear, consistent audio with customizable speed and natural-sounding narration for an enhanced listening experience.</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">☁️</div>
              <h3>Cloud-Powered</h3>
              <p>Access your converted audiobooks from any device with secure cloud storage and easy download management.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section - Mobile Optimized */}
      <section className="pricing">
        <div className="container">
          <div className="section-header">
            <h2>Simple, Transparent Pricing</h2>
            <p>Start your audiobook journey today</p>
          </div>
          
          <div className="pricing-cards">
            <div className="pricing-card">
              <h3>Free Trial</h3>
              <div className="price">
                <span className="amount">£0</span>
              </div>
              <ul>
                <li>2-minute preview</li>
                <li>Basic AI voice</li>
                <li>Experience the technology</li>
                <li>No payment required</li>
              </ul>
              <button className="pricing-btn trial">
                Try Free
              </button>
            </div>
            
            <div className="pricing-card featured">
              <div className="popular-badge">Most Popular</div>
              <h3>Pro Unlimited</h3>
              <div className="price">
                <span className="amount">£19.99</span>
                <span className="period">/month</span>
              </div>
              <ul>
                <li>Unlimited conversions</li>
                <li>Multiple AI voices</li>
                <li>Chapter navigation</li>
                <li>Cloud storage & sync</li>
                <li>Priority processing</li>
              </ul>
              <button className="pricing-btn primary">
                Start Free Trial
              </button>
            </div>
            
            <div className="pricing-card">
              <h3>Enterprise</h3>
              <div className="price">
                <span className="amount">Custom</span>
              </div>
              <ul>
                <li>Everything in Pro</li>
                <li>Custom voice training</li>
                <li>API access</li>
                <li>Team management</li>
                <li>Dedicated support</li>
              </ul>
              <button className="pricing-btn secondary">
                Contact Sales
              </button>
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
              <p>Transform any ebook into professional audiobooks with advanced AI technology.</p>
              <p className="domain">ebookvoice.ai</p>
            </div>
            <div className="footer-section">
              <h4>Product</h4>
              <ul>
                <li><a href="#features">AI Technology</a></li>
                <li><a href="#pricing">Pricing</a></li>
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

      {/* Trial Modal - iPhone Optimized */}
      {showTrial && (
        <div className="trial-section">
          <div className="trial-overlay" onClick={() => setShowTrial(false)}></div>
          <div className="trial-modal">
            <button className="close-trial" onClick={() => setShowTrial(false)}>×</button>
            <h2>🎙️ Try EbookVoice AI Free</h2>
            <p>Upload any ebook and experience our AI technology with a 2-minute preview</p>
            
            <div className="trial-upload-area" onClick={() => document.getElementById('trial-file-input').click()}>
              <div className="upload-icon">📄</div>
              <h3>Upload Your Ebook</h3>
              <p>PDF, EPUB, TXT • 5MB max • 2-minute preview</p>
              <button className="upload-btn">Choose File</button>
              <input
                id="trial-file-input"
                type="file"
                accept=".pdf,.epub,.txt"
                onChange={(e) => {
                  handleFileUpload(e);
                  setShowTrial(false);
                }}
                style={{ display: 'none' }}
              />
            </div>
            
            <div className="trial-features">
              <div className="trial-feature">
                <span>⚡</span>
                <span>2-min preview</span>
              </div>
              <div className="trial-feature">
                <span>🎯</span>
                <span>AI processing</span>
              </div>
              <div className="trial-feature">
                <span>🔒</span>
                <span>Secure & private</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;