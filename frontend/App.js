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
import LandingScreen from './src/screens/LandingScreen';
import VoiceSelector from './src/components/VoiceSelector';
import Button from './src/components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './src/components/ui/Card';
import { colors, spacing, borderRadius, typography } from './src/theme/colors';
import { LinearGradient } from 'expo-linear-gradient';

// API URL configuration
const API_BASE_URL = 'https://ebookvoice-backend.onrender.com';

function MainApp() {
  const [conversions, setConversions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState('xtts_female_narrator');
  const [uploadProgress, setUploadProgress] = useState(null);
  const [activeConversions, setActiveConversions] = useState(new Set());
  const [showDashboard, setShowDashboard] = useState(false);
  const [currentScreen, setCurrentScreen] = useState('landing'); // 'landing', 'app', 'dashboard'
  const { isAuthenticated, loading: authLoading, user, getAuthHeaders } = useAuth();

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
      }
    } catch (error) {
      console.error('Failed to fetch conversions:', error);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchConversions();
    }
  }, [isAuthenticated]);

  if (authLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  // Always authenticated (bypassed for demo)

  // Show landing screen first
  if (currentScreen === 'landing') {
    return (
      <LandingScreen 
        onNavigateToApp={() => setCurrentScreen('app')}
      />
    );
  }

  if (showDashboard || currentScreen === 'dashboard') {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => {
              setShowDashboard(false);
              setCurrentScreen('app');
            }}
          >
            <Text style={styles.backButtonText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Dashboard</Text>
        </View>
        <DashboardScreen />
      </View>
    );
  }

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
    setUploadProgress('Uploading file...');
    
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
        const { job_id } = data;
        setActiveConversions(prev => new Set([...prev, job_id]));
        
        setUploadProgress('Upload successful! Starting conversion...');
        
        // Start polling for progress
        startPollingConversion(job_id);
        
        Alert.alert('Success', `File uploaded! Converting "${file.name}" to high-quality audio.`);
        fetchConversions();
      } else {
        Alert.alert('Error', data.error || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      Alert.alert('Error', 'Failed to upload file. Please check your connection.');
    } finally {
      setLoading(false);
      setTimeout(() => setUploadProgress(null), 3000);
    }
  };

  const startPollingConversion = (jobId) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/conversions/${jobId}`);
        const data = await response.json();
        
        if (data.success) {
          const conversion = data.data;
          
          // Update conversions list
          setConversions(prev => 
            prev.map(c => c.id === jobId ? conversion : c)
          );
          
          // Stop polling if completed or failed
          if (conversion.status === 'completed' || conversion.status === 'failed') {
            clearInterval(pollInterval);
            setActiveConversions(prev => {
              const newSet = new Set(prev);
              newSet.delete(jobId);
              return newSet;
            });
            
            if (conversion.status === 'completed') {
              Alert.alert('Success', `Audio conversion completed for "${conversion.title}"!`);
            } else if (conversion.status === 'failed') {
              Alert.alert('Error', `Conversion failed: ${conversion.error || 'Unknown error'}`);
            }
          }
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    }, 2000); // Poll every 2 seconds
    
    // Clear interval after 10 minutes to prevent infinite polling
    setTimeout(() => clearInterval(pollInterval), 10 * 60 * 1000);
  };
  
  const downloadAudio = async (jobId, title) => {
    try {
      const url = `${API_BASE_URL}/download/${jobId}`;
      
      if (Platform.OS === 'web') {
        // For web, open download link in new tab
        const link = document.createElement('a');
        link.href = url;
        link.download = `${title}_audiobook.wav`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        // For mobile, show URL in alert with copy option
        Alert.alert(
          'Download Ready', 
          `High-quality audiobook ready for: "${title}"\n\nTap OK to copy download link.`,
          [
            { text: 'Cancel', style: 'cancel' },
            { 
              text: 'Copy Link', 
              onPress: () => {
                // In a real app, you'd use Clipboard API
                Alert.alert('Link Copied', url);
              }
            }
          ]
        );
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to download audio file');
    }
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
          <View style={styles.headerButtons}>
            <Button
              onPress={() => setCurrentScreen('landing')}
              variant="ghost"
              size="sm"
            >
              ← Landing
            </Button>
            <Button
              onPress={() => {
                setShowDashboard(true);
                setCurrentScreen('dashboard');
              }}
              variant="glass"
              size="sm"
            >
              Dashboard
            </Button>
          </View>
        </View>
      </LinearGradient>

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
              {loading ? 'Converting to Audio...' : 'Convert to Audio'}
            </Button>
            {uploadProgress && (
              <Text style={styles.uploadProgressText}>{uploadProgress}</Text>
            )}
            <Text style={styles.supportedFormats}>
              Supports PDF, EPUB, and TXT files
            </Text>
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
                    <Button
                      onPress={() => downloadAudio(conversion.id, conversion.title)}
                      variant="outline"
                      size="sm"
                    >
                      Download
                    </Button>
                  )}
                </View>
              ))
            )}
          </CardContent>
        </Card>
      </ScrollView>
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
  headerButtons: {
    flexDirection: 'row',
    gap: spacing.md,
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
  uploadProgressText: {
    color: colors.foreground.muted,
    fontSize: typography.fontSizes.sm,
    marginTop: spacing.sm,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  supportedFormats: {
    color: colors.foreground.disabled,
    fontSize: typography.fontSizes.xs,
    marginTop: spacing.xs,
    textAlign: 'center',
  },
});
