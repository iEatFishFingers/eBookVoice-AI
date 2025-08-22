import React, { useState } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  ScrollView,
  Alert,
  Platform,
} from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import { LinearGradient } from 'expo-linear-gradient';
import Button from '../components/ui/Button';
import { colors, spacing, borderRadius, typography } from '../theme/colors';

const API_BASE_URL = Platform.OS === 'web' && window.location.hostname === 'localhost' 
  ? 'https://ebookvoice-backend.onrender.com' 
  : 'https://ebookvoice-backend.onrender.com';

const LandingScreen = ({ onNavigateToApp }) => {
  const [showDemo, setShowDemo] = useState(false);
  const [file, setFile] = useState(null);
  const [isConverting, setIsConverting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState('');
  const [jobId, setJobId] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);

  const handleFileUpload = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['application/pdf', 'application/epub+zip', 'text/plain'],
        copyToCacheDirectory: true,
      });

      if (result.canceled) return;

      const uploadedFile = result.assets[0];
      
      if (uploadedFile.size > 5 * 1024 * 1024) {
        Alert.alert('File Too Large', 'File size must be under 5MB for demo');
        return;
      }

      setFile(uploadedFile);
    } catch (error) {
      Alert.alert('Error', 'Failed to pick document');
    }
  };

  const convertFile = async () => {
    if (!file) return;

    setIsConverting(true);
    setProgress(0);
    setCurrentStage('Uploading file...');

    try {
      // Create form data
      const formData = new FormData();
      formData.append('file', {
        uri: file.uri,
        type: file.mimeType,
        name: file.name,
      });
      formData.append('voice_id', 'basic_0'); // Default voice for demo

      // Upload file and start conversion
      const uploadResponse = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const uploadData = await uploadResponse.json();
      
      if (!uploadData.success) {
        throw new Error(uploadData.error || 'Upload failed');
      }

      const convertJobId = uploadData.job_id;
      setJobId(convertJobId);
      setCurrentStage('Processing with AI...');

      // Poll for conversion status
      pollConversionStatus(convertJobId);

    } catch (error) {
      console.error('Conversion error:', error);
      setIsConverting(false);
      Alert.alert('Error', error.message || 'Failed to convert file');
    }
  };

  const pollConversionStatus = async (convertJobId) => {
    try {
      const statusResponse = await fetch(`${API_BASE_URL}/conversions/${convertJobId}`);
      const statusData = await statusResponse.json();

      if (statusData.status === 'completed') {
        setProgress(100);
        setCurrentStage('Conversion complete!');
        setIsConverting(false);
        setAudioUrl(`${API_BASE_URL}/download/${convertJobId}`);
        Alert.alert('Success!', 'Your audiobook is ready! Click the download link below.');
      } else if (statusData.status === 'failed') {
        setIsConverting(false);
        Alert.alert('Error', statusData.error || 'Conversion failed');
      } else {
        // Still processing, update progress
        const newProgress = Math.min(90, (Date.now() % 10000) / 100); // Simulated progress
        setProgress(newProgress);
        setCurrentStage(statusData.current_phase || 'Processing...');
        
        // Continue polling
        setTimeout(() => pollConversionStatus(convertJobId), 2000);
      }
    } catch (error) {
      console.error('Status check error:', error);
      setIsConverting(false);
      Alert.alert('Error', 'Failed to check conversion status');
    }
  };

  const resetDemo = () => {
    setFile(null);
    setProgress(0);
    setCurrentStage('');
    setIsConverting(false);
    setJobId(null);
    setAudioUrl(null);
  };

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.logo}>🎙️ EbookVoice AI</Text>
        <View style={styles.headerButtons}>
          <TouchableOpacity style={styles.headerBtn} onPress={onNavigateToApp}>
            <Text style={styles.headerBtnText}>Sign In</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.headerBtnPrimary} onPress={() => setShowDemo(true)}>
            <Text style={styles.headerBtnPrimaryText}>Try Demo</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Hero Section */}
      <View style={styles.hero}>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>🚀 AI-Powered Technology</Text>
        </View>
        
        <Text style={styles.heroTitle}>
          Transform Your Ebooks Into{'\n'}Professional Audiobooks
        </Text>
        
        <Text style={styles.heroSubtitle}>
          Convert any PDF, EPUB, or TXT file into high-quality audiobooks using 
          advanced AI technology. Get natural-sounding narration in minutes.
        </Text>
        
        <View style={styles.heroStats}>
          <View style={styles.stat}>
            <Text style={styles.statNumber}>1,000+</Text>
            <Text style={styles.statLabel}>Books Converted</Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statNumber}>Under 5 min</Text>
            <Text style={styles.statLabel}>Average Time</Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statNumber}>AI-Powered</Text>
            <Text style={styles.statLabel}>Technology</Text>
          </View>
        </View>

        <View style={styles.heroButtons}>
          <TouchableOpacity style={styles.primaryButton} onPress={() => setShowDemo(true)}>
            <Text style={styles.primaryButtonText}>Try Free Demo</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.secondaryButton} onPress={onNavigateToApp}>
            <Text style={styles.secondaryButtonText}>Get Started →</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Demo Section */}
      {showDemo && (
        <View style={styles.demoSection}>
          <Text style={styles.sectionTitle}>Try EbookVoice AI Demo</Text>
          <Text style={styles.sectionSubtitle}>
            Upload a document and see AI conversion in action
          </Text>

          <View style={styles.demoContainer}>
            {!file && !isConverting && (
              <TouchableOpacity style={styles.uploadArea} onPress={handleFileUpload}>
                <Text style={styles.uploadIcon}>📄</Text>
                <Text style={styles.uploadTitle}>Click to Upload File</Text>
                <Text style={styles.uploadSubtitle}>
                  PDF, EPUB, or TXT • Max 5MB • 2-minute preview
                </Text>
              </TouchableOpacity>
            )}

            {file && !isConverting && !audioUrl && (
              <View style={styles.fileReady}>
                <Text style={styles.fileName}>📄 {file.name}</Text>
                <Text style={styles.fileSize}>
                  {(file.size / 1024 / 1024).toFixed(1)} MB • Ready for conversion
                </Text>
                
                <TouchableOpacity style={styles.convertButton} onPress={convertFile}>
                  <Text style={styles.convertButtonText}>🎙️ Convert to Audio</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.resetButton} onPress={resetDemo}>
                  <Text style={styles.resetButtonText}>Choose Different File</Text>
                </TouchableOpacity>
              </View>
            )}

            {isConverting && (
              <View style={styles.processing}>
                <Text style={styles.processingIcon}>🤖</Text>
                <Text style={styles.processingTitle}>Converting your book...</Text>
                <Text style={styles.processingStage}>{currentStage}</Text>
                
                <View style={styles.progressBar}>
                  <View style={[styles.progressFill, { width: `${progress}%` }]} />
                </View>
                <Text style={styles.progressText}>{Math.round(progress)}%</Text>
              </View>
            )}

            {audioUrl && (
              <View style={styles.success}>
                <Text style={styles.successIcon}>🎉</Text>
                <Text style={styles.successTitle}>Conversion Complete!</Text>
                <Text style={styles.successSubtitle}>
                  Your audiobook is ready for download
                </Text>
                
                <TouchableOpacity 
                  style={styles.downloadButton} 
                  onPress={() => {
                    if (Platform.OS === 'web') {
                      window.open(audioUrl, '_blank');
                    } else {
                      Alert.alert('Download Ready', `Download your audiobook: ${audioUrl}`);
                    }
                  }}
                >
                  <Text style={styles.downloadButtonText}>📥 Download Audiobook</Text>
                </TouchableOpacity>
                
                <TouchableOpacity style={styles.resetButton} onPress={resetDemo}>
                  <Text style={styles.resetButtonText}>Convert Another File</Text>
                </TouchableOpacity>
                
                <View style={styles.upgradePrompt}>
                  <Text style={styles.upgradeTitle}>🚀 Want More?</Text>
                  <Text style={styles.upgradeText}>
                    • Unlimited conversions • Multiple voices • Chapter navigation
                  </Text>
                  <TouchableOpacity style={styles.upgradeButton} onPress={onNavigateToApp}>
                    <Text style={styles.upgradeButtonText}>Upgrade to Pro - £19.99/month</Text>
                  </TouchableOpacity>
                </View>
              </View>
            )}
          </View>
        </View>
      )}

      {/* Features */}
      <View style={styles.features}>
        <Text style={styles.sectionTitle}>Why Choose EbookVoice AI?</Text>
        <Text style={styles.sectionSubtitle}>
          Powerful features that make audiobook creation effortless
        </Text>
        
        <View style={styles.featuresGrid}>
          {[
            { icon: '🤖', title: 'AI Technology', desc: 'Advanced neural networks create natural-sounding speech' },
            { icon: '⚡', title: 'Lightning Fast', desc: 'Convert entire books in minutes, not hours' },
            { icon: '🎭', title: 'Multiple Voices', desc: 'Choose from professional AI voice options' },
            { icon: '📚', title: 'Smart Chapters', desc: 'Automatic chapter detection and navigation' },
            { icon: '☁️', title: 'Cloud Storage', desc: 'Access your library from any device' },
            { icon: '🎧', title: 'HD Quality', desc: 'Studio-quality audio output every time' }
          ].map((feature, index) => (
            <View key={index} style={styles.featureCard}>
              <Text style={styles.featureIcon}>{feature.icon}</Text>
              <Text style={styles.featureTitle}>{feature.title}</Text>
              <Text style={styles.featureDesc}>{feature.desc}</Text>
            </View>
          ))}
        </View>
      </View>

      {/* Pricing */}
      <View style={styles.pricing}>
        <Text style={styles.sectionTitle}>Simple Pricing</Text>
        <Text style={styles.sectionSubtitle}>
          Choose the plan that works for you
        </Text>
        
        <View style={styles.pricingCards}>
          {/* Free Plan */}
          <View style={styles.pricingCard}>
            <Text style={styles.planName}>Free Trial</Text>
            <Text style={styles.planPrice}>£0</Text>
            <Text style={styles.planPeriod}>2-minute previews</Text>
            <View style={styles.planFeatures}>
              <Text style={styles.planFeature}>• Basic AI voice</Text>
              <Text style={styles.planFeature}>• 2-minute limit</Text>
              <Text style={styles.planFeature}>• No credit card</Text>
            </View>
            <TouchableOpacity style={styles.planButton} onPress={() => setShowDemo(true)}>
              <Text style={styles.planButtonText}>Try Free</Text>
            </TouchableOpacity>
          </View>

          {/* Pro Plan */}
          <View style={[styles.pricingCard, styles.featuredCard]}>
            <View style={styles.popularBadge}>
              <Text style={styles.popularText}>Most Popular</Text>
            </View>
            <Text style={styles.planName}>Pro</Text>
            <Text style={styles.planPrice}>£19.99</Text>
            <Text style={styles.planPeriod}>per month</Text>
            <View style={styles.planFeatures}>
              <Text style={styles.planFeature}>• Unlimited conversions</Text>
              <Text style={styles.planFeature}>• 10+ premium voices</Text>
              <Text style={styles.planFeature}>• Chapter navigation</Text>
              <Text style={styles.planFeature}>• Cloud storage</Text>
            </View>
            <TouchableOpacity style={styles.planButtonPrimary} onPress={onNavigateToApp}>
              <Text style={styles.planButtonPrimaryText}>Start Free Trial</Text>
            </TouchableOpacity>
          </View>

          {/* Enterprise Plan */}
          <View style={styles.pricingCard}>
            <Text style={styles.planName}>Enterprise</Text>
            <Text style={styles.planPrice}>Custom</Text>
            <Text style={styles.planPeriod}>Contact us</Text>
            <View style={styles.planFeatures}>
              <Text style={styles.planFeature}>• Everything in Pro</Text>
              <Text style={styles.planFeature}>• Custom voices</Text>
              <Text style={styles.planFeature}>• API access</Text>
              <Text style={styles.planFeature}>• Priority support</Text>
            </View>
            <TouchableOpacity style={styles.planButton}>
              <Text style={styles.planButtonText}>Contact Sales</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerTitle}>🎙️ EbookVoice AI</Text>
        <Text style={styles.footerText}>
          Transform your reading experience with AI-powered audiobooks
        </Text>
        <Text style={styles.footerCopyright}>
          © 2025 EbookVoice AI. All rights reserved.
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background.primary,
  },

  // Header
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: Platform.OS === 'web' ? 20 : 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
    backgroundColor: colors.background.primary,
  },
  logo: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.primary,
  },
  headerButtons: {
    flexDirection: 'row',
    gap: 10,
  },
  headerBtn: {
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: colors.border.default,
  },
  headerBtnText: {
    color: colors.foreground.secondary,
    fontSize: 14,
  },
  headerBtnPrimary: {
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: colors.primary,
  },
  headerBtnPrimaryText: {
    color: colors.foreground.primary,
    fontSize: 14,
    fontWeight: '600',
  },

  // Hero
  hero: {
    paddingVertical: 60,
    paddingHorizontal: 20,
    alignItems: 'center',
    backgroundColor: colors.background.primary,
  },
  badge: {
    backgroundColor: colors.primary + '20',
    borderColor: colors.primary + '40',
    borderWidth: 1,
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 20,
    marginBottom: 30,
  },
  badgeText: {
    color: colors.primary,
    fontSize: 14,
    fontWeight: '500',
  },
  heroTitle: {
    fontSize: 36,
    fontWeight: '800',
    color: colors.foreground.primary,
    textAlign: 'center',
    marginBottom: 20,
    lineHeight: 42,
  },
  heroSubtitle: {
    fontSize: 16,
    color: colors.foreground.secondary,
    textAlign: 'center',
    marginBottom: 40,
    maxWidth: 600,
    lineHeight: 24,
  },
  heroStats: {
    flexDirection: 'row',
    gap: 40,
    marginBottom: 40,
    flexWrap: 'wrap',
    justifyContent: 'center',
  },
  stat: {
    alignItems: 'center',
    minWidth: 100,
  },
  statNumber: {
    fontSize: 20,
    fontWeight: '800',
    color: colors.primary,
    marginBottom: 5,
  },
  statLabel: {
    fontSize: 14,
    color: colors.foreground.muted,
    textAlign: 'center',
  },
  heroButtons: {
    flexDirection: 'row',
    gap: 15,
    flexWrap: 'wrap',
    justifyContent: 'center',
  },
  primaryButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 12,
    minWidth: 160,
  },
  primaryButtonText: {
    color: colors.foreground.primary,
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  secondaryButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: colors.border.default,
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 12,
    minWidth: 160,
  },
  secondaryButtonText: {
    color: colors.foreground.primary,
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },

  // Demo Section
  demoSection: {
    backgroundColor: colors.background.secondary,
    paddingVertical: 60,
    paddingHorizontal: 20,
  },
  sectionTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: colors.foreground.primary,
    textAlign: 'center',
    marginBottom: 10,
  },
  sectionSubtitle: {
    fontSize: 16,
    color: colors.foreground.secondary,
    textAlign: 'center',
    marginBottom: 40,
  },
  demoContainer: {
    backgroundColor: colors.background.glassmorphism,
    borderColor: colors.border.glassmorphism,
    borderWidth: 1,
    borderRadius: 16,
    padding: 30,
    maxWidth: 600,
    alignSelf: 'center',
    width: '100%',
  },

  // Upload
  uploadArea: {
    borderWidth: 2,
    borderStyle: 'dashed',
    borderColor: colors.primary + '40',
    borderRadius: 12,
    paddingVertical: 40,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  uploadIcon: {
    fontSize: 48,
    marginBottom: 20,
  },
  uploadTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.foreground.primary,
    marginBottom: 5,
    textAlign: 'center',
  },
  uploadSubtitle: {
    color: colors.foreground.muted,
    textAlign: 'center',
  },

  // File Ready
  fileReady: {
    alignItems: 'center',
    gap: 20,
  },
  fileName: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.foreground.primary,
    textAlign: 'center',
  },
  fileSize: {
    color: colors.foreground.muted,
    textAlign: 'center',
    marginBottom: 10,
  },
  convertButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 12,
    width: '100%',
    maxWidth: 250,
  },
  convertButtonText: {
    color: colors.foreground.primary,
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  resetButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: colors.border.default,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  resetButtonText: {
    color: colors.foreground.secondary,
    fontSize: 14,
    textAlign: 'center',
  },

  // Processing
  processing: {
    alignItems: 'center',
    gap: 15,
  },
  processingIcon: {
    fontSize: 48,
    marginBottom: 10,
  },
  processingTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.primary,
    textAlign: 'center',
  },
  processingStage: {
    color: colors.foreground.muted,
    textAlign: 'center',
    marginBottom: 20,
  },
  progressBar: {
    width: '100%',
    height: 8,
    backgroundColor: colors.background.glassmorphism,
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: colors.primary,
  },
  progressText: {
    color: colors.primary,
    fontWeight: '600',
    textAlign: 'center',
  },

  // Success/Download
  success: {
    alignItems: 'center',
    gap: 20,
  },
  successIcon: {
    fontSize: 48,
    marginBottom: 10,
  },
  successTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.success,
    textAlign: 'center',
  },
  successSubtitle: {
    color: colors.foreground.muted,
    textAlign: 'center',
  },
  downloadButton: {
    backgroundColor: colors.success,
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 12,
    width: '100%',
    maxWidth: 250,
  },
  downloadButtonText: {
    color: colors.foreground.primary,
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  upgradePrompt: {
    backgroundColor: colors.primary + '20',
    borderColor: colors.primary + '40',
    borderWidth: 1,
    borderRadius: 12,
    padding: 20,
    width: '100%',
    marginTop: 20,
  },
  upgradeTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.primary,
    textAlign: 'center',
    marginBottom: 10,
  },
  upgradeText: {
    color: colors.foreground.secondary,
    textAlign: 'center',
    marginBottom: 15,
    fontSize: 14,
  },
  upgradeButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 10,
    width: '100%',
  },
  upgradeButtonText: {
    color: colors.foreground.primary,
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },

  // Features
  features: {
    paddingVertical: 60,
    paddingHorizontal: 20,
    backgroundColor: colors.background.primary,
  },
  featuresGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 20,
    justifyContent: 'center',
    maxWidth: 1000,
    alignSelf: 'center',
  },
  featureCard: {
    backgroundColor: colors.background.glassmorphism,
    borderColor: colors.border.glassmorphism,
    borderWidth: 1,
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    width: 300,
    minHeight: 140,
  },
  featureIcon: {
    fontSize: 32,
    marginBottom: 15,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.foreground.primary,
    marginBottom: 8,
    textAlign: 'center',
  },
  featureDesc: {
    color: colors.foreground.secondary,
    textAlign: 'center',
    fontSize: 14,
    lineHeight: 20,
  },

  // Pricing
  pricing: {
    backgroundColor: colors.background.secondary,
    paddingVertical: 60,
    paddingHorizontal: 20,
  },
  pricingCards: {
    flexDirection: 'row',
    gap: 20,
    justifyContent: 'center',
    flexWrap: 'wrap',
  },
  pricingCard: {
    backgroundColor: colors.background.glassmorphism,
    borderColor: colors.border.glassmorphism,
    borderWidth: 1,
    borderRadius: 12,
    padding: 25,
    alignItems: 'center',
    width: 280,
    position: 'relative',
  },
  featuredCard: {
    backgroundColor: colors.primary + '10',
    borderColor: colors.primary + '30',
    borderWidth: 2,
  },
  popularBadge: {
    position: 'absolute',
    top: -12,
    backgroundColor: colors.primary,
    paddingHorizontal: 15,
    paddingVertical: 5,
    borderRadius: 15,
  },
  popularText: {
    color: colors.foreground.primary,
    fontSize: 12,
    fontWeight: '600',
  },
  planName: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.foreground.primary,
    marginBottom: 15,
    textAlign: 'center',
  },
  planPrice: {
    fontSize: 32,
    fontWeight: '800',
    color: colors.primary,
    textAlign: 'center',
  },
  planPeriod: {
    color: colors.foreground.muted,
    marginBottom: 25,
    textAlign: 'center',
  },
  planFeatures: {
    alignSelf: 'stretch',
    marginBottom: 25,
    gap: 8,
  },
  planFeature: {
    color: colors.foreground.secondary,
    fontSize: 14,
  },
  planButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: colors.border.default,
    paddingHorizontal: 25,
    paddingVertical: 12,
    borderRadius: 10,
    width: '100%',
  },
  planButtonText: {
    color: colors.foreground.primary,
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  planButtonPrimary: {
    backgroundColor: colors.primary,
    paddingHorizontal: 25,
    paddingVertical: 12,
    borderRadius: 10,
    width: '100%',
  },
  planButtonPrimaryText: {
    color: colors.foreground.primary,
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },

  // Footer
  footer: {
    paddingVertical: 40,
    paddingHorizontal: 20,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: colors.border.default,
    backgroundColor: colors.background.primary,
  },
  footerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.primary,
    marginBottom: 15,
  },
  footerText: {
    color: colors.foreground.secondary,
    textAlign: 'center',
    marginBottom: 15,
    maxWidth: 400,
  },
  footerCopyright: {
    color: colors.foreground.muted,
    fontSize: 14,
    textAlign: 'center',
  },
});

export default LandingScreen;