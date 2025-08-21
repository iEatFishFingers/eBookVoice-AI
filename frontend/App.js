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

export default function App() {
  const [conversions, setConversions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchConversions();
  }, []);

  const fetchConversions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/conversions`);
      const data = await response.json();
      if (data.success) {
        setConversions(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch conversions:', error);
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

      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const data = await response.json();
      
      if (data.success) {
        Alert.alert('Success', 'File uploaded successfully! Conversion started.');
        fetchConversions();
      } else {
        Alert.alert('Error', data.error || 'Upload failed');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to upload file');
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
      Alert.alert('Error', 'Failed to download audio file');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#4CAF50';
      case 'processing': return '#FF9800';
      case 'failed': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>eBookVoice AI</Text>
      <Text style={styles.subtitle}>Convert eBooks to Audio</Text>

      <TouchableOpacity
        style={[styles.uploadButton, loading && styles.uploadButtonDisabled]}
        onPress={pickDocument}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.uploadButtonText}>Upload eBook</Text>
        )}
      </TouchableOpacity>

      <ScrollView style={styles.conversionsContainer}>
        <Text style={styles.sectionTitle}>Conversions</Text>
        
        {conversions.length === 0 ? (
          <Text style={styles.emptyText}>No conversions yet. Upload an eBook to get started!</Text>
        ) : (
          conversions.map((conversion) => (
            <View key={conversion.id} style={styles.conversionCard}>
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

              {conversion.status === 'completed' && (
                <TouchableOpacity
                  style={styles.downloadButton}
                  onPress={() => downloadAudio(conversion.id, conversion.title)}
                >
                  <Text style={styles.downloadButtonText}>Download Audio</Text>
                </TouchableOpacity>
              )}

              {conversion.error && (
                <Text style={styles.errorText}>Error: {conversion.error}</Text>
              )}
            </View>
          ))
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    paddingTop: Platform.OS === 'web' ? 20 : 50,
    paddingHorizontal: 20,
    maxWidth: Platform.OS === 'web' ? 800 : '100%',
    alignSelf: Platform.OS === 'web' ? 'center' : 'stretch',
    width: '100%',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    color: '#333',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    color: '#666',
    marginBottom: 30,
  },
  uploadButton: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 30,
  },
  uploadButtonDisabled: {
    backgroundColor: '#999',
  },
  uploadButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  conversionsContainer: {
    flex: 1,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  emptyText: {
    textAlign: 'center',
    color: '#999',
    fontSize: 16,
    marginTop: 50,
  },
  conversionCard: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  conversionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  conversionFile: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 8,
  },
  statusText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  phaseText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 10,
  },
  progressContainer: {
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
    marginBottom: 10,
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 2,
  },
  downloadButton: {
    backgroundColor: '#4CAF50',
    padding: 10,
    borderRadius: 5,
    alignItems: 'center',
  },
  downloadButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  errorText: {
    color: '#F44336',
    fontSize: 12,
    marginTop: 5,
  },
});
