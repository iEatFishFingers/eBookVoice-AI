// src/pages/LoginPage.js - Modern version matching App.js theme
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { 
  registerWithEmailAndPassword, 
  loginWithEmailAndPassword, 
  loginWithGoogle, 
  resetUserPassword
} from '../services/auth';

const LoginPage = () => {
  const navigate = useNavigate();
  
  // State management
  const [isSignUp, setIsSignUp] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  
  // Form data
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    displayName: ''
  });
  
  // Messages
  const [message, setMessage] = useState({ type: '', text: '' });
  
  // Handle input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    if (message.text) {
      setMessage({ type: '', text: '' });
    }
  };
  
  // Validate form
  const validateForm = () => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setMessage({ type: 'error', text: 'Please enter a valid email address.' });
      return false;
    }
    
    if (formData.password.length < 6) {
      setMessage({ type: 'error', text: 'Password must be at least 6 characters long.' });
      return false;
    }
    
    if (isSignUp) {
      if (formData.password !== formData.confirmPassword) {
        setMessage({ type: 'error', text: 'Passwords do not match.' });
        return false;
      }
      
      if (!formData.displayName.trim()) {
        setMessage({ type: 'error', text: 'Please enter your name.' });
        return false;
      }
    }
    
    return true;
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setIsLoading(true);
    setMessage({ type: '', text: '' });
    
    try {
      let result;
      
      if (isSignUp) {
        result = await registerWithEmailAndPassword(
          formData.email, 
          formData.password, 
          formData.displayName
        );
        
        if (result.success) {
          setMessage({ 
            type: 'success', 
            text: 'Account created successfully! Welcome to AudioBook Pro!' 
          });
          
          setTimeout(() => {
            navigate('/dashboard');
          }, 2000);
        }
      } else {
        result = await loginWithEmailAndPassword(formData.email, formData.password);
        
        if (result.success) {
          setMessage({ 
            type: 'success', 
            text: 'Welcome back! Redirecting to your dashboard...' 
          });
          
          setTimeout(() => {
            navigate('/dashboard');
          }, 1500);
        }
      }
      
      if (!result.success) {
        setMessage({ type: 'error', text: result.error });
      }
      
    } catch (error) {
      console.error('Authentication error:', error);
      setMessage({ 
        type: 'error', 
        text: 'Something went wrong. Please try again.' 
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle Google sign in
  const handleGoogleSignIn = async () => {
    setIsLoading(true);
    setMessage({ type: '', text: '' });
    
    try {
      const result = await loginWithGoogle();
      
      if (result.success) {
        setMessage({ 
          type: 'success', 
          text: 'Signed in with Google! Redirecting...' 
        });
        
        setTimeout(() => {
          navigate('/dashboard');
        }, 1500);
      } else {
        setMessage({ type: 'error', text: result.error });
      }
    } catch (error) {
      console.error('Google sign-in error:', error);
      setMessage({ 
        type: 'error', 
        text: 'Google sign-in failed. Please try again.' 
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle password reset
  const handlePasswordReset = async (e) => {
    e.preventDefault();
    
    if (!formData.email) {
      setMessage({ type: 'error', text: 'Please enter your email address first.' });
      return;
    }
    
    setIsLoading(true);
    
    try {
      const result = await resetUserPassword(formData.email);
      
      if (result.success) {
        setMessage({ type: 'success', text: result.message });
        setShowForgotPassword(false);
      } else {
        setMessage({ type: 'error', text: result.error });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to send reset email. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Switch between sign up and sign in
  const switchMode = () => {
    setIsSignUp(!isSignUp);
    setFormData({
      email: '',
      password: '',
      confirmPassword: '',
      displayName: ''
    });
    setMessage({ type: '', text: '' });
    setShowForgotPassword(false);
  };

  return (
    <div className="login-page modern">
      {/* SEO */}
      <Helmet>
        <title>{isSignUp ? 'Sign Up for AudioBook Pro' : 'Sign In to AudioBook Pro'}</title>
        <meta 
          name="description" 
          content={isSignUp 
            ? 'Create your AudioBook Pro account and start converting ebooks to audiobooks instantly. Free trial included.'
            : 'Sign in to your AudioBook Pro account to access unlimited audiobook conversions and premium features.'
          } 
        />
      </Helmet>

      {/* Navigation matching App.js theme */}
      <nav className="nav modern">
        <div className="nav-container">
          <Link to="/" className="logo">
            <img 
              src="/logo.svg" 
              alt="EbookVoice AI" 
              className="logo-image"
            />
          </Link>
          <div className="nav-buttons">
            <Link to="/" className="nav-btn back-btn">
              ← Back to Home
            </Link>
          </div>
        </div>
      </nav>

      {/* Main login content with App.js styling */}
      <div className="login-container modern">
        <div className="login-content">
          {/* Left side - Welcome message matching hero section */}
          <div className="login-welcome">
            <div className="welcome-badge">
              🎧 AudioBook Pro
            </div>
            
            <h1>
              {isSignUp ? 'Join the AI Revolution' : 'Welcome Back'}
            </h1>
            <p>
              {isSignUp 
                ? 'Transform your entire ebook library into professional audiobooks. Join thousands of readers who\'ve discovered the power of AI narration.'
                : 'Continue your audiobook journey with AI-powered conversion technology.'
              }
            </p>
            
            {/* Benefits matching features section */}
            <div className="benefits-showcase">
              <div className="benefit-card">
                <div className="benefit-icon">🤖</div>
                <div className="benefit-content">
                  <h3>Smart AI Processing</h3>
                  <p>Automatic chapter detection and intelligent content processing</p>
                </div>
              </div>
              
              <div className="benefit-card">
                <div className="benefit-icon">🎭</div>
                <div className="benefit-content">
                  <h3>Premium Voices</h3>
                  <p>Natural-sounding AI narration with multiple voice options</p>
                </div>
              </div>
              
              <div className="benefit-card">
                <div className="benefit-icon">☁️</div>
                <div className="benefit-content">
                  <h3>Cloud Library</h3>
                  <p>Access your audiobooks anywhere with secure cloud storage</p>
                </div>
              </div>
            </div>

            {/* Stats matching hero stats */}
            <div className="auth-stats">
              <div className="stat">
                <span className="stat-number">10K+</span>
                <span className="stat-label">Users</span>
              </div>
              <div className="stat">
                <span className="stat-number">50K+</span>
                <span className="stat-label">Books</span>
              </div>
              <div className="stat">
                <span className="stat-number">99%</span>
                <span className="stat-label">Satisfaction</span>
              </div>
            </div>
          </div>

          {/* Right side - Login form with modern styling */}
          <div className="login-form-container modern">
            <div className="login-form-card">
              <div className="form-header">
                <h2>
                  {showForgotPassword 
                    ? 'Reset Password' 
                    : isSignUp 
                      ? 'Create Account' 
                      : 'Sign In'
                  }
                </h2>
                <p className="form-subtitle">
                  {showForgotPassword
                    ? 'Enter your email to receive reset instructions'
                    : isSignUp
                      ? 'Start your audiobook journey today'
                      : 'Access your audiobook library'
                  }
                </p>
              </div>
              
              {/* Messages */}
              {message.text && (
                <div className={`message modern ${message.type}`}>
                  <div className="message-icon">
                    {message.type === 'success' ? '✅' : '⚠️'}
                  </div>
                  <div className="message-text">{message.text}</div>
                </div>
              )}
              
              {/* Password reset form */}
              {showForgotPassword ? (
                <form onSubmit={handlePasswordReset} className="login-form modern">
                  <div className="form-group">
                    <label htmlFor="email">Email Address</label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      placeholder="Enter your email address"
                      required
                    />
                  </div>
                  
                  <button 
                    type="submit" 
                    className="form-button primary modern"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <span className="loading-content">
                        <span className="spinner">🔄</span> Sending...
                      </span>
                    ) : (
                      <span>📧 Send Reset Email</span>
                    )}
                  </button>
                  
                  <button 
                    type="button" 
                    className="link-button modern"
                    onClick={() => setShowForgotPassword(false)}
                  >
                    ← Back to Sign In
                  </button>
                </form>
              ) : (
                <>
                  {/* Google sign in */}
                  <button 
                    type="button"
                    onClick={handleGoogleSignIn}
                    className="google-button modern"
                    disabled={isLoading}
                  >
                    <span className="google-icon">🌐</span>
                    <span>Continue with Google</span>
                    <span className="button-shine"></span>
                  </button>
                  
                  <div className="divider modern">
                    <span>or continue with email</span>
                  </div>
                  
                  {/* Email/password form */}
                  <form onSubmit={handleSubmit} className="login-form modern">
                    {/* Name field for sign up */}
                    {isSignUp && (
                      <div className="form-group">
                        <label htmlFor="displayName">Your Name</label>
                        <input
                          type="text"
                          id="displayName"
                          name="displayName"
                          value={formData.displayName}
                          onChange={handleInputChange}
                          placeholder="Enter your full name"
                          required
                        />
                      </div>
                    )}
                    
                    {/* Email field */}
                    <div className="form-group">
                      <label htmlFor="email">Email Address</label>
                      <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        placeholder="Enter your email address"
                        required
                      />
                    </div>
                    
                    {/* Password field */}
                    <div className="form-group">
                      <label htmlFor="password">Password</label>
                      <input
                        type="password"
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleInputChange}
                        placeholder={isSignUp ? "Create a secure password" : "Enter your password"}
                        required
                      />
                    </div>
                    
                    {/* Confirm password for sign up */}
                    {isSignUp && (
                      <div className="form-group">
                        <label htmlFor="confirmPassword">Confirm Password</label>
                        <input
                          type="password"
                          id="confirmPassword"
                          name="confirmPassword"
                          value={formData.confirmPassword}
                          onChange={handleInputChange}
                          placeholder="Confirm your password"
                          required
                        />
                      </div>
                    )}
                    
                    {/* Submit button */}
                    <button 
                      type="submit" 
                      className="form-button primary modern"
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <span className="loading-content">
                          <span className="spinner">🔄</span> 
                          {isSignUp ? 'Creating Account...' : 'Signing In...'}
                        </span>
                      ) : (
                        <span>
                          {isSignUp ? '🎧 Create Account' : '🚀 Sign In'}
                        </span>
                      )}
                      <span className="button-shine"></span>
                    </button>
                  </form>
                  
                  {/* Additional options */}
                  <div className="form-footer modern">
                    {!isSignUp && (
                      <button 
                        type="button"
                        className="link-button modern"
                        onClick={() => setShowForgotPassword(true)}
                      >
                        Forgot your password?
                      </button>
                    )}
                    
                    <div className="switch-mode">
                      {isSignUp ? (
                        <p>
                          Already have an account?{' '}
                          <button 
                            type="button"
                            className="link-button modern primary"
                            onClick={switchMode}
                          >
                            Sign In
                          </button>
                        </p>
                      ) : (
                        <p>
                          Don't have an account?{' '}
                          <button 
                            type="button"
                            className="link-button modern primary"
                            onClick={switchMode}
                          >
                            Sign Up Free
                          </button>
                        </p>
                      )}
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* Trust indicators */}
            <div className="trust-indicators">
              <div className="indicator">
                <span className="indicator-icon">🔒</span>
                <span>Secure & Encrypted</span>
              </div>
              <div className="indicator">
                <span className="indicator-icon">⚡</span>
                <span>Instant Access</span>
              </div>
              <div className="indicator">
                <span className="indicator-icon">💯</span>
                <span>100% Free Trial</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced styling matching App.js theme */}
      <style jsx>{`
        .login-page.modern {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          position: relative;
          overflow-x: hidden;
        }

        .login-page.modern::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: 
            radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
          pointer-events: none;
        }

        /* Navigation matching App.js */
        .nav.modern {
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(20px);
          padding: 1rem 0;
          border-bottom: 1px solid rgba(255, 255, 255, 0.2);
          position: relative;
          z-index: 10;
        }

        .nav-container {
          max-width: 1200px;
          margin: 0 auto;
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0 2rem;
        }

        .logo {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 1.5rem;
          font-weight: bold;
          color: white;
          text-decoration: none;
          transition: all 0.3s ease;
        }

        .logo:hover {
          opacity: 0.8;
          transform: translateY(-1px);
        }

        .logo-image {
          height: 2rem;
          width: auto;
        }

        .nav-buttons {
          display: flex;
          gap: 1rem;
          align-items: center;
        }

        .nav-btn.back-btn {
          color: rgba(255, 255, 255, 0.9);
          text-decoration: none;
          font-weight: 500;
          padding: 0.5rem 1rem;
          border-radius: 8px;
          transition: all 0.3s ease;
          border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .nav-btn.back-btn:hover {
          background: rgba(255, 255, 255, 0.1);
          color: white;
          transform: translateX(-2px);
        }

        /* Main container */
        .login-container.modern {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: calc(100vh - 80px);
          padding: 2rem;
          position: relative;
          z-index: 5;
        }

        .login-content {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 4rem;
          max-width: 1400px;
          width: 100%;
          align-items: center;
        }

        /* Welcome section matching hero */
        .login-welcome {
          color: white;
          padding: 2rem 0;
        }

        .welcome-badge {
          display: inline-block;
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 25px;
          padding: 0.5rem 1.5rem;
          font-size: 0.9rem;
          font-weight: 600;
          margin-bottom: 2rem;
          backdrop-filter: blur(10px);
        }

        .login-welcome h1 {
          font-size: 3.5rem;
          font-weight: 800;
          margin-bottom: 1.5rem;
          line-height: 1.2;
          background: linear-gradient(135deg, #ffffff 0%, #f0f8ff 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .login-welcome p {
          font-size: 1.2rem;
          line-height: 1.6;
          margin-bottom: 2.5rem;
          opacity: 0.9;
        }

        /* Benefits showcase */
        .benefits-showcase {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
          margin-bottom: 2rem;
        }

        .benefit-card {
          display: flex;
          align-items: center;
          gap: 1rem;
          background: rgba(255, 255, 255, 0.05);
          padding: 1.5rem;
          border-radius: 16px;
          border: 1px solid rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          transition: all 0.3s ease;
        }

        .benefit-card:hover {
          background: rgba(255, 255, 255, 0.1);
          transform: translateX(10px);
        }

        .benefit-icon {
          font-size: 2rem;
          flex-shrink: 0;
        }

        .benefit-content h3 {
          margin: 0 0 0.5rem 0;
          font-size: 1.1rem;
          font-weight: 600;
        }

        .benefit-content p {
          margin: 0;
          font-size: 0.9rem;
          opacity: 0.8;
        }

        /* Stats matching hero */
        .auth-stats {
          display: flex;
          gap: 2rem;
          margin-top: 2rem;
        }

        .stat {
          text-align: center;
        }

        .stat-number {
          display: block;
          font-size: 2rem;
          font-weight: 800;
          color: white;
        }

        .stat-label {
          font-size: 0.9rem;
          opacity: 0.8;
        }

        /* Form container */
        .login-form-container.modern {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1.5rem;
        }

        .login-form-card {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(20px);
          border-radius: 24px;
          padding: 3rem;
          box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.2),
            0 0 0 1px rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          width: 100%;
          max-width: 480px;
          position: relative;
          overflow: hidden;
        }

        .login-form-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 4px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .form-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .form-header h2 {
          color: #2d3748;
          font-size: 2.2rem;
          font-weight: 700;
          margin-bottom: 0.5rem;
        }

        .form-subtitle {
          color: #718096;
          font-size: 1rem;
          margin: 0;
        }

        /* Messages */
        .message.modern {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1rem 1.5rem;
          border-radius: 12px;
          margin-bottom: 1.5rem;
          font-weight: 500;
          animation: slideIn 0.3s ease-out;
        }

        .message.modern.success {
          background: linear-gradient(135deg, #c6f6d5 0%, #9ae6b4 100%);
          color: #2f855a;
          border: 1px solid #9ae6b4;
        }

        .message.modern.error {
          background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
          color: #c53030;
          border: 1px solid #feb2b2;
        }

        .message-icon {
          font-size: 1.2rem;
        }

        .message-text {
          flex: 1;
        }

        /* Google button */
        .google-button.modern {
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 1rem;
          padding: 1rem 1.5rem;
          border: 2px solid #e2e8f0;
          border-radius: 12px;
          background: white;
          color: #4a5568;
          font-weight: 600;
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.3s ease;
          margin-bottom: 1.5rem;
          position: relative;
          overflow: hidden;
        }

        .google-button.modern:hover:not(:disabled) {
          border-color: #667eea;
          background: #f8fafc;
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        }

        .google-button.modern:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          transform: none;
        }

        .google-icon {
          font-size: 1.2rem;
        }

        .button-shine {
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
          transition: left 0.5s ease;
        }

        .google-button.modern:hover .button-shine {
          left: 100%;
        }

        /* Divider */
        .divider.modern {
          text-align: center;
          margin: 1.5rem 0;
          position: relative;
        }

        .divider.modern::before {
          content: '';
          position: absolute;
          top: 50%;
          left: 0;
          right: 0;
          height: 1px;
          background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        }

        .divider.modern span {
          background: rgba(255, 255, 255, 0.95);
          padding: 0 1.5rem;
          color: #718096;
          font-size: 0.9rem;
          font-weight: 500;
        }

        /* Form styles */
        .login-form.modern {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .form-group label {
          font-weight: 600;
          color: #4a5568;
          font-size: 0.95rem;
        }

        .form-group input {
          padding: 1rem 1.25rem;
          border: 2px solid #e2e8f0;
          border-radius: 12px;
          font-size: 1rem;
          transition: all 0.3s ease;
          background: white;
        }

        .form-group input:focus {
          outline: none;
          border-color: #667eea;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
          transform: translateY(-1px);
        }

        .form-group input::placeholder {
          color: #a0aec0;
        }

        /* Form buttons */
        .form-button.modern {
          padding: 1.25rem 2rem;
          border: none;
          border-radius: 12px;
          font-weight: 700;
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.3s ease;
          text-align: center;
          position: relative;
          overflow: hidden;
        }

        .form-button.primary.modern {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        }

        .form-button.primary.modern:hover:not(:disabled) {
          transform: translateY(-3px);
          box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4);
        }

        .form-button.primary.modern:hover .button-shine {
          left: 100%;
        }

        .form-button:disabled {
          opacity: 0.7;
          cursor: not-allowed;
          transform: none;
        }

        .loading-content {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          justify-content: center;
        }

        .spinner {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        /* Link buttons */
        .link-button.modern {
          background: none;
          border: none;
          color: #667eea;
          font-weight: 600;
          cursor: pointer;
          text-decoration: none;
          font-size: inherit;
          padding: 0.5rem;
          border-radius: 6px;
          transition: all 0.3s ease;
        }

        .link-button.modern:hover {
          color: #5a67d8;
          background: rgba(102, 126, 234, 0.1);
        }

        .link-button.modern.primary {
          color: #667eea;
          font-weight: 700;
        }

        /* Form footer */
        .form-footer.modern {
          margin-top: 1.5rem;
          text-align: center;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .switch-mode {
          color: #718096;
          font-size: 0.95rem;
        }

        .switch-mode p {
          margin: 0;
        }

        /* Trust indicators */
        .trust-indicators {
          display: flex;
          justify-content: center;
          gap: 2rem;
          max-width: 480px;
        }

        .indicator {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: rgba(255, 255, 255, 0.9);
          font-size: 0.9rem;
          font-weight: 500;
        }

        .indicator-icon {
          font-size: 1.1rem;
        }

        /* Responsive design */
        @media (max-width: 1024px) {
          .login-content {
            grid-template-columns: 1fr;
            gap: 3rem;
            text-align: center;
          }

          .login-welcome h1 {
            font-size: 3rem;
          }

          .benefits-showcase {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1rem;
          }

          .benefit-card:hover {
            transform: translateY(-5px);
          }
        }

        @media (max-width: 768px) {
          .login-container.modern {
            padding: 1rem;
          }

          .login-welcome {
            padding: 1rem 0;
          }

          .login-welcome h1 {
            font-size: 2.5rem;
          }

          .login-welcome p {
            font-size: 1.1rem;
          }

          .login-form-card {
            padding: 2rem 1.5rem;
          }

          .auth-stats {
            justify-content: center;
            gap: 1.5rem;
          }

          .trust-indicators {
            flex-direction: column;
            gap: 1rem;
            align-items: center;
          }
        }

        @media (max-width: 480px) {
          .nav-container {
            padding: 0 1rem;
          }

          .login-welcome h1 {
            font-size: 2rem;
          }

          .login-form-card {
            padding: 1.5rem;
          }

          .form-header h2 {
            font-size: 1.8rem;
          }

          .benefits-showcase {
            gap: 1rem;
          }

          .benefit-card {
            padding: 1rem;
          }
        }

        /* Animations */
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        /* High contrast mode */
        @media (prefers-contrast: high) {
          .login-form-card {
            background: white;
            border: 2px solid #333;
          }

          .form-group input {
            border-color: #333;
          }

          .message.modern.success {
            background: #e6ffed;
            border-color: #00b300;
          }

          .message.modern.error {
            background: #ffe6e6;
            border-color: #cc0000;
          }
        }

        /* Reduced motion */
        @media (prefers-reduced-motion: reduce) {
          .message.modern {
            animation: none;
          }

          .form-button:hover,
          .google-button.modern:hover,
          .logo:hover,
          .benefit-card:hover {
            transform: none;
          }

          .spinner {
            animation: none;
          }

          .button-shine {
            display: none;
          }
        }
      `}</style>
    </div>
  );
};

export default LoginPage;