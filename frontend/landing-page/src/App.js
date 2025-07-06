// src/App.js - EbookVoice AI Landing Page with Conversion
import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [showTrial, setShowTrial] = useState(false);
  const [file, setFile] = useState(null);
  const [isConverting, setIsConverting] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState('');

  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files[0];
    if (uploadedFile) {
      // Validate file type and size
      const validTypes = ['application/pdf', 'text/plain', 'application/epub+zip'];
      const maxSize = 5 * 1024 * 1024; // 5MB limit for trial

      if (!validTypes.includes(uploadedFile.type) && 
          !uploadedFile.name.toLowerCase().endsWith('.epub')) {
        alert('Please upload a PDF, EPUB, or TXT file');
        return;
      }

      if (uploadedFile.size > maxSize) {
        alert('File size must be under 5MB for trial conversion');
        return;
      }

      setFile(uploadedFile);
      setAudioUrl(null);
    }
  };

  const simulateConversion = () => {
    setIsConverting(true);
    setProgress(0);
    
    const stages = [
      { progress: 15, message: 'Analyzing document structure with AI...' },
      { progress: 30, message: 'Extracting text content intelligently...' },
      { progress: 50, message: 'Applying smart chapter detection...' },
      { progress: 70, message: 'Generating natural AI narration...' },
      { progress: 90, message: 'Optimizing audio quality...' },
      { progress: 100, message: 'Conversion complete! 🎉' }
    ];

    let currentStageIndex = 0;
    const interval = setInterval(() => {
      if (currentStageIndex < stages.length) {
        const stage = stages[currentStageIndex];
        setProgress(stage.progress);
        setCurrentStage(stage.message);
        currentStageIndex++;
      } else {
        clearInterval(interval);
        setAudioUrl('demo-audio.wav'); // Simulated audio URL
        setIsConverting(false);
      }
    }, 1000);
  };

  const resetDemo = () => {
    setFile(null);
    setAudioUrl(null);
    setProgress(0);
    setCurrentStage('');
    setIsConverting(false);
  };

  return (
    <div className="app">
      {/* Navigation */}
      <nav className="nav">
        <div className="nav-container">
          <div className="logo">
            <h2>🎙️ EbookVoice AI</h2>
          </div>
          <div className="nav-buttons">
            <button className="nav-btn login-btn">
              Sign In
            </button>
            <button className="nav-btn trial-btn">
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-container">
          <div className="hero-content">
            <div className="hero-badge">
              🚀 Powered by Advanced AI Technology
            </div>
            
            <h1 className="hero-title">
              Transform Any Ebook Into 
              <span className="gradient-text"> Professional Audiobooks</span>
            </h1>
            
            <p className="hero-subtitle">
              EbookVoice AI uses cutting-edge artificial intelligence to convert your entire 
              digital library into studio-quality audiobooks with natural-sounding narration 
              and intelligent chapter detection in seconds.
            </p>
            
            <div className="hero-stats">
              <div className="stat">
                <span className="stat-number">1K+</span>
                <span className="stat-label">Books Converted</span>
              </div>
              <div className="stat">
                <span className="stat-number">5 mins</span>
                <span className="stat-label">Average Speed</span>
              </div>
              <div className="stat">
                <span className="stat-number">85%</span>
                <span className="stat-label">AI Accuracy</span>
              </div>
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
                <span className="demo-title">EbookVoice AI Engine</span>
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
                  <span className="status-indicator active"></span>
                  AI Engine: Active
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Live Conversion Section */}
      <section className="conversion-demo">
        <div className="container">
          <div className="section-header">
            <h2>Try EbookVoice AI Live Demo</h2>
            <p>Experience our AI technology - convert any document to audiobook in real-time</p>
          </div>

          <div className="conversion-interface">
            {!file && !audioUrl && (
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
                  <h3>Drop your ebook here or click to upload</h3>
                  <p>Supports PDF, EPUB, TXT • 2-minute preview • 5MB max</p>
                  <input
                    id="file-input"
                    type="file"
                    accept=".pdf,.epub,.txt"
                    onChange={handleFileUpload}
                    style={{ display: 'none' }}
                  />
                </div>
                
                <div className="demo-features">
                  <div className="demo-feature">
                    <span className="feature-icon">🎭</span>
                    <span>AI Voice Generation</span>
                  </div>
                  <div className="demo-feature">
                    <span className="feature-icon">📖</span>
                    <span>Smart Chapter Detection</span>
                  </div>
                  <div className="demo-feature">
                    <span className="feature-icon">⚡</span>
                    <span>Lightning Fast Processing</span>
                  </div>
                </div>
              </div>
            )}

            {file && !audioUrl && !isConverting && (
              <div className="file-ready">
                <div className="file-preview">
                  <div className="file-icon">📄</div>
                  <div className="file-info">
                    <h4>{file.name}</h4>
                    <p>{(file.size / 1024 / 1024).toFixed(2)} MB • Ready for AI conversion</p>
                  </div>
                </div>
                <button className="convert-btn" onClick={simulateConversion}>
                  🎙️ Convert with EbookVoice AI
                </button>
                <button className="reset-btn" onClick={resetDemo}>
                  Choose Different File
                </button>
              </div>
            )}

            {isConverting && (
              <div className="conversion-progress">
                <div className="ai-processing">
                  <div className="ai-avatar">
                    <div className="ai-brain-active">🤖</div>
                    <div className="processing-rings">
                      <div className="ring"></div>
                      <div className="ring"></div>
                      <div className="ring"></div>
                    </div>
                  </div>
                  
                  <div className="progress-info">
                    <h3>EbookVoice AI is processing your book</h3>
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
            )}

            {audioUrl && (
              <div className="conversion-complete">
                <div className="success-animation">
                  <div className="success-icon">🎉</div>
                  <h3>Conversion Complete!</h3>
                  <p>Your audiobook is ready with EbookVoice AI</p>
                </div>
                
                <CustomAudioPlayer fileName={file.name} />
                
                <div className="upgrade-prompt">
                  <h4>🚀 Unlock Full Features</h4>
                  <div className="upgrade-features">
                    <span>✅ Complete audiobook conversion</span>
                    <span>✅ 10+ AI voice options</span>
                    <span>✅ Chapter-by-chapter navigation</span>
                    <span>✅ Cloud storage & sync</span>
                  </div>
                  <div className="upgrade-buttons">
                    <button className="upgrade-btn primary">
                      Get Full Access - $19.99/month
                    </button>
                    <button className="try-another-btn" onClick={resetDemo}>
                      Try Another File
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="container">
          <div className="section-header">
            <h2>Why Choose EbookVoice AI?</h2>
            <p>Advanced artificial intelligence meets intuitive design</p>
          </div>
          
          <div className="features-grid">
            <div className="feature-card">
                <div className="feature-icon">🤖</div>
                <h3>Advanced AI Processing</h3>
                <p>Using AI technology with natural pauses and punctuation recognition to mimic natural speech patterns for more authentic narration.</p>
            </div>
            
            <div className="feature-card">
                <div className="feature-icon">🎭</div>
                <h3>Multiple AI Voices</h3>
                <p>Choose from a range of different trained AI voices, each with unique personalities and speaking styles.</p>
            </div>
            
            <div className="feature-card">
                <div className="feature-icon">⚡</div>
                <h3>Instant Conversion</h3>
                <p>Convert entire books quickly. Our optimized AI infrastructure processes thousands of pages efficiently.</p>
            </div>
            
            <div className="feature-card">
                <div className="feature-icon">📚</div>
                <h3>Smart Chapter Detection</h3>
                <p>AI automatically identifies chapters, skips front matter, and creates perfect navigation with 85% accuracy.</p>
            </div>
            
            <div className="feature-card">
                <div className="feature-icon">🎧</div>
                <h3>Studio Quality Audio</h3>
                <p>Professional-grade output with customizable speed, tone, and emphasis for an enhanced listening experience.</p>
            </div>
            
            <div className="feature-card">
                <div className="feature-icon">☁️</div>
                <h3>Cloud-Powered Platform</h3>
                <p>Access your audiobook library from any device with secure cloud storage and instant synchronization.</p>
            </div>
            </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="pricing">
        <div className="container">
          <div className="section-header">
            <h2>Simple, Transparent Pricing</h2>
            <p>Join thousands who've transformed their reading experience</p>
          </div>
          
          <div className="pricing-cards">
            <div className="pricing-card">
              <h3>Free Trial</h3>
              <div className="price">
                <span className="amount">£0</span>
              </div>
              <ul>
                <li>2-minute Audiobook Limit</li>
                <li>Basic AI voice</li>
                <li>Experience the technology</li>
                <li>No Payment Required</li>
              </ul>
              <button className="pricing-btn trial">
                Try EbookVoice AI Free
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
                <li>Unlimited audiobook conversions</li>
                <li>10+ premium AI voices</li>
                <li>Chapter-by-chapter navigation</li>
                <li>Cloud storage & sync</li>
                <li>Speed & tone controls</li>
                <li>Priority AI processing</li>
              </ul>
              <button className="pricing-btn primary">
                Start 7-Day Free Trial
              </button>
            </div>
            
            <div className="pricing-card">
              <h3>Enterprise</h3>
              <div className="price">
                <span className="amount">Custom</span>
              </div>
              <ul>
                <li>Everything in Pro</li>
                <li>Custom AI voice training</li>
                <li>API access</li>
                <li>Team management</li>
                <li>White-label options</li>
                <li>Dedicated support</li>
              </ul>
              <button className="pricing-btn secondary">
                Contact Sales
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <h4>🎙️ EbookVoice AI</h4>
              <p>Transform any ebook into a professional audiobook with advanced AI technology.</p>
              <p className="domain">Coming soon: ebookvoice.ai</p>
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
                <li><a href="#contact">Contact AI Support</a></li>
                <li><a href="#docs">API Documentation</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Company</h4>
              <ul>
                <li><a href="#about">About EbookVoice</a></li>
                <li><a href="#privacy">Privacy Policy</a></li>
                <li><a href="#terms">Terms of Service</a></li>
              </ul>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2025 EbookVoice AI. All rights reserved. • ebookvoice.ai</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

// Custom Audio Player Component
const CustomAudioPlayer = ({ fileName }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(120); // 2 minutes for demo
  const [currentChapter, setCurrentChapter] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [showChapters, setShowChapters] = useState(false);

  // Demo chapters for the preview
  const demoChapters = [
    { title: "Introduction", startTime: 0, duration: 30 },
    { title: "Chapter 1: Getting Started", startTime: 30, duration: 45 },
    { title: "Chapter 2: Advanced Concepts", startTime: 75, duration: 45 }
  ];

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
    
    if (!isPlaying) {
        const interval = setInterval(() => {
        setCurrentTime(prev => {
            if (prev >= duration) {
            setIsPlaying(false);
            clearInterval(interval);
            return duration;
            }
            return prev + 1;
        });
        }, 1000);
        
        // Store interval to clean up later
        return () => clearInterval(interval);
    }
};

  const handleSeek = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const newTime = (clickX / rect.width) * duration;
    setCurrentTime(Math.max(0, Math.min(duration, newTime)));
  };

  const skipToChapter = (chapterIndex) => {
    if (chapterIndex >= 0 && chapterIndex < demoChapters.length) {
      setCurrentChapter(chapterIndex);
      setCurrentTime(demoChapters[chapterIndex].startTime);
    }
  };

  const previousChapter = () => {
    if (currentChapter > 0) {
      skipToChapter(currentChapter - 1);
    }
  };

  const nextChapter = () => {
    if (currentChapter < demoChapters.length - 1) {
      skipToChapter(currentChapter + 1);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getCurrentChapter = () => {
    for (let i = demoChapters.length - 1; i >= 0; i--) {
      if (currentTime >= demoChapters[i].startTime) {
        return i;
      }
    }
    return 0;
  };

  const currentChapterIndex = getCurrentChapter();

  return (
    <div className="custom-audio-player">
      {/* Player Header */}
      <div className="player-header">
        <div className="book-info">
          <h4>🎧 {fileName} - AI Audiobook</h4>
          <p className="current-chapter">
            {demoChapters[currentChapterIndex]?.title} • 2:00 preview
          </p>
        </div>
        <button 
          className="chapters-btn"
          onClick={() => setShowChapters(!showChapters)}
        >
          📚 Chapters
        </button>
      </div>

      {/* Main Controls */}
      <div className="main-player-controls">
            <button 
                className="control-btn"
                onClick={previousChapter}
                disabled={currentChapter === 0}
            >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/>
                </svg>
            </button>
            
            <button className="play-btn-main" onClick={togglePlay}>
                {isPlaying ? (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
                </svg>
                ) : (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8 5v14l11-7z"/>
                </svg>
                )}
            </button>
            
            <button 
                className="control-btn"
                onClick={nextChapter}
                disabled={currentChapter === demoChapters.length - 1}
            >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
                </svg>
            </button>
        </div>

      {/* Progress Bar */}
      <div className="progress-section">
        <div className="time-info">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
        <div className="seek-bar" onClick={handleSeek}>
          <div className="seek-track">
            <div 
              className="seek-progress"
              style={{ width: `${(currentTime / duration) * 100}%` }}
            ></div>
            <div 
              className="seek-handle"
              style={{ left: `${(currentTime / duration) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Volume and Options */}
      <div className="player-options">
        <div className="volume-section">
          <span>🔊</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={volume}
            onChange={(e) => setVolume(parseFloat(e.target.value))}
            className="volume-slider"
          />
        </div>
        <div className="playback-speed">
          <label>Speed:</label>
          <select className="speed-select">
            <option value="0.75">0.75x</option>
            <option value="1" selected>1x</option>
            <option value="1.25">1.25x</option>
            <option value="1.5">1.5x</option>
            <option value="2">2x</option>
          </select>
        </div>
      </div>

      {/* Chapter List */}
      {showChapters && (
        <div className="chapters-list">
          <h5>📖 Chapters</h5>
          {demoChapters.map((chapter, index) => (
            <div 
              key={index}
              className={`chapter-item ${index === currentChapterIndex ? 'active' : ''}`}
              onClick={() => skipToChapter(index)}
            >
              <div className="chapter-number">{index + 1}</div>
              <div className="chapter-details">
                <span className="chapter-title">{chapter.title}</span>
                <span className="chapter-duration">{formatTime(chapter.duration)}</span>
              </div>
              {index === currentChapterIndex && isPlaying && (
                <div className="playing-indicator">🔊</div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Demo Notice */}
      <div className="demo-notice">
        <p>🎭 Demo player with simulated chapters • Upgrade for full functionality</p>
      </div>
    </div>
  );
};

export default App;