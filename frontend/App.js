import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
  Platform,
} from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import { AuthProvider, useAuth } from './src/context/AuthContext';
import AuthScreen from './src/screens/AuthScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import VoiceSelector from './src/components/VoiceSelector';
import AudioPlayer from './src/components/AudioPlayer';
import Button from './src/components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './src/components/ui/Card';
import { colors, spacing, borderRadius, typography } from './src/theme/colors';
import { LinearGradient } from 'expo-linear-gradient';

// Environment-based API URL configuration
const getApiBaseUrl = () => {
  // For Expo development
  if (__DEV__) {
    return 'http://localhost:5001';
  }
  
  // For web deployment - replace with your actual Render URL
  if (Platform.OS === 'web') {
    return process.env.REACT_APP_API_URL || 'https://your-app.onrender.com';
  }
  
  // For mobile production builds
  return process.env.EXPO_PUBLIC_API_URL || 'https://your-app.onrender.com';
};

const API_BASE_URL = getApiBaseUrl();

function MainApp() {
  const [conversions, setConversions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState('basic_0');
  const [showDashboard, setShowDashboard] = useState(false);
  const [serverOnline, setServerOnline] = useState(true);
  const [currentJobId, setCurrentJobId] = useState(null);
  const [showAudioPlayer, setShowAudioPlayer] = useState(false);
  const [currentAudioUrl, setCurrentAudioUrl] = useState(null);
  const [currentAudioTitle, setCurrentAudioTitle] = useState('');
  const { isAuthenticated, loading: authLoading, user, getAuthHeaders } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      fetchConversions();
    }
    
    // Start health check polling
    const healthInterval = setInterval(checkServerHealth, 30000); // Check every 30 seconds
    checkServerHealth(); // Check immediately
    
    return () => clearInterval(healthInterval);
  }, [isAuthenticated]);

  // Poll for job progress when we have an active conversion
  useEffect(() => {
    let progressInterval;
    
    if (currentJobId) {
      progressInterval = setInterval(() => {
        pollJobProgress(currentJobId);
      }, 2000); // Poll every 2 seconds
    }
    
    return () => {
      if (progressInterval) {
        clearInterval(progressInterval);
      }
    };
  }, [currentJobId]);

  if (authLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  // For demo purposes, bypass authentication check but keep for production
  // if (!isAuthenticated) {
  //   return <AuthScreen />;
  // }

  if (showDashboard) {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => setShowDashboard(false)}
          >
            <Text style={styles.backButtonText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Dashboard</Text>
        </View>
        <DashboardScreen />
      </View>
    );
  }

  const checkServerHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: 'GET',
        timeout: 10000, // 10 second timeout
      });
      
      if (response.ok) {
        setServerOnline(true);
      } else {
        setServerOnline(false);
      }
    } catch (error) {
      setServerOnline(false);
    }
  };

  const pollJobProgress = async (jobId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/conversions/${jobId}`, {
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          const job = data.data;
          
          // Update conversions list with latest job status
          setConversions(prev => 
            prev.map(conv => 
              conv.id === jobId ? { ...conv, ...job } : conv
            )
          );
          
          // If job is complete or failed, stop polling
          if (job.status === 'completed' || job.status === 'failed') {
            setCurrentJobId(null);
            fetchConversions(); // Refresh full list
          }
        }
      }
    } catch (error) {
      console.error('Failed to poll job progress:', error);
      // Stop polling on repeated failures to prevent spam
      setCurrentJobId(null);
      setServerOnline(false);
    }
  };

  const fetchConversions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/conversions`, {
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
      });
      const data = await response.json();
      if (data.success) {
        setConversions(data.data);
        
        // Check if there are any active jobs that need polling
        const activeJobs = data.data.filter(job => 
          job.status === 'processing' || job.status === 'pending'
        );
        
        if (activeJobs.length > 0 && !currentJobId) {
          setCurrentJobId(activeJobs[0].id);
        }
      }
    } catch (error) {
      console.error('Failed to fetch conversions:', error);
      setServerOnline(false);
    }
  };

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['application/pdf', 'application/epub+zip', 'text/plain'],
        copyToCacheDirectory: true,
      });

      if (result.canceled) return;

      const file = result.assets[0];
      uploadFile(file);
    } catch (error) {
      Alert.alert('Error', 'Failed to pick document');
    }
  };

  const uploadFile = async (file) => {
    setLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: file.uri,
        type: file.mimeType,
        name: file.name,
      });
      formData.append('voice_id', selectedVoice);

      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
          ...getAuthHeaders(),
        },
      });

      const data = await response.json();
      
      if (data.success) {
        Alert.alert('Success', 'File uploaded successfully! Conversion started.');
        
        // Start tracking the new job
        setCurrentJobId(data.data.id);
        fetchConversions();
      } else {
        Alert.alert('Error', data.error || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      
      // More specific error messages
      let errorMessage = 'Failed to upload file';
      if (error.message?.includes('Network')) {
        errorMessage = 'Network error. Please check your connection and try again.';
      } else if (error.message?.includes('timeout')) {
        errorMessage = 'Upload timeout. The file might be too large or connection is slow.';
      }
      
      Alert.alert('Upload Error', errorMessage);
      setServerOnline(false); // Mark server as potentially offline
    } finally {
      setLoading(false);
    }
  };

  const downloadAudio = async (jobId, title) => {
    try {
      const url = `${API_BASE_URL}/download/${jobId}`;
      
      if (Platform.OS === 'web') {
        // For web, open download link in new tab
        window.open(url, '_blank');
      } else {
        // For mobile, show URL in alert
        Alert.alert('Download', `Audio file ready for: ${title}\nURL: ${url}`);
      }
    } catch (error) {
      console.error('Download error:', error);
      Alert.alert('Download Error', 'Failed to download audio file. Please check your connection and try again.');
    }
  };

  const openAudioPlayer = async (jobId, title) => {
    try {
      const audioUrl = `${API_BASE_URL}/download/${jobId}`;
      setCurrentAudioUrl(audioUrl);
      setCurrentAudioTitle(title);
      setShowAudioPlayer(true);
    } catch (error) {
      console.error('Audio player error:', error);
      Alert.alert('Player Error', 'Failed to open audio player. The audio file might not be ready yet.');
    }
  };

  const closeAudioPlayer = () => {
    setShowAudioPlayer(false);
    setCurrentAudioUrl(null);
    setCurrentAudioTitle('');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return colors.success;
      case 'processing': return colors.warning;
      case 'failed': return colors.error;
      default: return colors.foreground.disabled;
    }
  };

  return (
    <View style={styles.container}>
      {/* Header with gradient */}
      <LinearGradient
        colors={[colors.primary, colors.accent]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <View>
            <Text style={styles.title}>eBookVoice AI</Text>
            <Text style={styles.subtitle}>Convert eBooks to Audio</Text>
          </View>
          <Button
            onPress={() => setShowDashboard(true)}
            variant="glass"
            size="sm"
          >
            Dashboard
          </Button>
        </View>
      </LinearGradient>

      {/* Server Offline Notification */}
      {!serverOnline && (
        <View style={styles.offlineNotification}>
          <Text style={styles.offlineText}>
            🚨 AI conversion service is currently down. Please try again later.
          </Text>
          <Button
            onPress={checkServerHealth}
            variant="outline"
            size="sm"
            style={styles.retryButton}
          >
            Retry Connection
          </Button>
        </View>
      )}

      <ScrollView style={styles.content}>
        <VoiceSelector
          selectedVoice={selectedVoice}
          onVoiceSelect={setSelectedVoice}
          userTier={user?.subscription_tier || 'free'}
        />

        <Card style={styles.uploadCard}>
          <CardHeader>
            <CardTitle>Upload Your eBook</CardTitle>
            <CardDescription>Select a file to convert to audio</CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              onPress={pickDocument}
              disabled={loading}
              variant="gradient"
              size="lg"
              loading={loading}
            >
              {loading ? 'Processing...' : 'Choose File'}
            </Button>
          </CardContent>
        </Card>

        <Card style={styles.conversionsCard}>
          <CardHeader>
            <CardTitle>Recent Conversions</CardTitle>
            <CardDescription>Track your audiobook projects</CardDescription>
          </CardHeader>
          <CardContent>
            {conversions.length === 0 ? (
              <Text style={styles.emptyText}>No conversions yet. Upload an eBook to get started!</Text>
            ) : (
              conversions.map((conversion) => (
                <View key={conversion.id} style={styles.conversionItem}>
                  <View style={styles.conversionInfo}>
                    <Text style={styles.conversionTitle}>{conversion.title}</Text>
                    <Text style={styles.conversionFile}>{conversion.fileName}</Text>
                    
                    <View style={styles.statusContainer}>
                      <View
                        style={[
                          styles.statusDot,
                          { backgroundColor: getStatusColor(conversion.status) }
                        ]}
                      />
                      <Text style={styles.statusText}>
                        {conversion.status.charAt(0).toUpperCase() + conversion.status.slice(1)}
                      </Text>
                    </View>

                    {conversion.current_phase && (
                      <Text style={styles.phaseText}>{conversion.current_phase}</Text>
                    )}

                    {conversion.progress > 0 && (
                      <View style={styles.progressContainer}>
                        <View
                          style={[
                            styles.progressBar,
                            { width: `${conversion.progress}%` }
                          ]}
                        />
                      </View>
                    )}

                    {conversion.error && (
                      <Text style={styles.errorText}>Error: {conversion.error}</Text>
                    )}
                  </View>

                  {conversion.status === 'completed' && (
                    <View style={styles.actionButtons}>
                      <Button
                        onPress={() => openAudioPlayer(conversion.id, conversion.title)}
                        variant="gradient"
                        size="sm"
                        style={styles.playButton}
                      >
                        ▶️ Play
                      </Button>
                      <Button
                        onPress={() => downloadAudio(conversion.id, conversion.title)}
                        variant="outline"
                        size="sm"
                      >
                        Download
                      </Button>
                    </View>
                  )}
                </View>
              ))
            )}
          </CardContent>
        </Card>
      </ScrollView>

      {/* Audio Player Modal */}
      {showAudioPlayer && currentAudioUrl && (
        <View style={styles.audioPlayerOverlay}>
          <AudioPlayer
            audioUrl={currentAudioUrl}
            title={currentAudioTitle}
            onClose={closeAudioPlayer}
          />
        </View>
      )}
    </View>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background.primary,
  },
  content: {
    flex: 1,
    paddingHorizontal: spacing.md,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background.primary,
  },
  loadingText: {
    marginTop: spacing.md,
    color: colors.foreground.muted,
    fontSize: typography.fontSizes.md,
  },
  header: {
    paddingTop: Platform.OS === 'web' ? spacing.lg : spacing.xxxl,
    paddingBottom: spacing.xl,
    paddingHorizontal: spacing.lg,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: typography.fontSizes.xl,
    fontWeight: typography.fontWeights.bold,
    color: colors.foreground.primary,
  },
  backButton: {
    backgroundColor: colors.background.glassmorphism,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: colors.border.glassmorphism,
  },
  backButtonText: {
    color: colors.foreground.primary,
    fontWeight: typography.fontWeights.medium,
  },
  title: {
    fontSize: typography.fontSizes.hero,
    fontWeight: typography.fontWeights.bold,
    color: colors.foreground.primary,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: typography.fontSizes.lg,
    color: colors.foreground.primary,
    opacity: 0.9,
  },
  uploadCard: {
    marginBottom: spacing.lg,
  },
  conversionsCard: {
    marginBottom: spacing.lg,
  },
  emptyText: {
    textAlign: 'center',
    color: colors.foreground.muted,
    fontSize: typography.fontSizes.md,
    fontStyle: 'italic',
    paddingVertical: spacing.xl,
  },
  conversionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border.default,
  },
  conversionInfo: {
    flex: 1,
  },
  conversionTitle: {
    fontSize: typography.fontSizes.md,
    fontWeight: typography.fontWeights.medium,
    color: colors.foreground.primary,
    marginBottom: spacing.xs,
  },
  conversionFile: {
    fontSize: typography.fontSizes.sm,
    color: colors.foreground.muted,
    marginBottom: spacing.sm,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: spacing.sm,
  },
  statusText: {
    fontSize: typography.fontSizes.sm,
    fontWeight: typography.fontWeights.medium,
    color: colors.foreground.primary,
  },
  phaseText: {
    fontSize: typography.fontSizes.xs,
    color: colors.foreground.muted,
    marginBottom: spacing.sm,
  },
  progressContainer: {
    height: 4,
    backgroundColor: colors.background.tertiary,
    borderRadius: borderRadius.sm,
    marginBottom: spacing.sm,
  },
  progressBar: {
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: borderRadius.sm,
  },
  errorText: {
    color: colors.error,
    fontSize: typography.fontSizes.xs,
    marginTop: spacing.xs,
  },
  offlineNotification: {
    backgroundColor: colors.error,
    marginHorizontal: spacing.md,
    marginTop: spacing.sm,
    padding: spacing.md,
    borderRadius: borderRadius.md,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  offlineText: {
    color: colors.foreground.primary,
    fontSize: typography.fontSizes.sm,
    fontWeight: typography.fontWeights.medium,
    flex: 1,
    marginRight: spacing.md,
  },
  retryButton: {
    minWidth: 80,
  },
  actionButtons: {
    flexDirection: 'column',
    gap: spacing.sm,
    minWidth: 100,
  },
  playButton: {
    minWidth: 80,
  },
  audioPlayerOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
});