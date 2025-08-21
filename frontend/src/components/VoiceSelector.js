import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { useAuth } from '../context/AuthContext';

export default function VoiceSelector({ selectedVoice, onVoiceSelect, userTier = 'free' }) {
  const [voices, setVoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const { getAuthHeaders } = useAuth();

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-app.onrender.com';

  useEffect(() => {
    fetchVoices();
  }, []);

  const fetchVoices = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/voices`, {
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setVoices(data.data || []);
        
        // Auto-select first available voice if none selected
        if (!selectedVoice && data.data && data.data.length > 0) {
          const availableVoices = data.data.filter(voice => 
            !voice.tier_required || voice.tier_required === userTier ||
            (userTier === 'professional' && voice.tier_required === 'free') ||
            (userTier === 'enterprise' && ['free', 'professional'].includes(voice.tier_required))
          );
          
          if (availableVoices.length > 0) {
            onVoiceSelect(availableVoices[0].id);
          }
        }
      } else {
        console.error('Failed to fetch voices:', data.error);
        Alert.alert('Error', 'Failed to load voice options');
      }
    } catch (error) {
      console.error('Voice fetch error:', error);
      Alert.alert('Error', 'Failed to connect to voice service');
    } finally {
      setLoading(false);
    }
  };

  const isVoiceAvailable = (voice) => {
    if (!voice.tier_required) return true;
    
    switch (userTier) {
      case 'enterprise':
        return true;
      case 'professional':
        return ['free', 'professional'].includes(voice.tier_required);
      case 'free':
        return voice.tier_required === 'free';
      default:
        return voice.tier_required === 'free';
    }
  };

  const getQualityColor = (quality) => {
    switch (quality) {
      case 'Premium': return '#4CAF50';
      case 'High': return '#FF9800';
      case 'Standard': return '#2196F3';
      default: return '#9E9E9E';
    }
  };

  const getTierBadgeColor = (tier) => {
    switch (tier) {
      case 'enterprise': return '#FF5722';
      case 'professional': return '#4CAF50';
      case 'free': return '#9E9E9E';
      default: return '#9E9E9E';
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="small" color="#007AFF" />
        <Text style={styles.loadingText}>Loading voices...</Text>
      </View>
    );
  }

  const availableVoices = voices.filter(isVoiceAvailable);
  const unavailableVoices = voices.filter(voice => !isVoiceAvailable(voice));

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Select Voice</Text>
      
      {/* Available Voices */}
      <ScrollView style={styles.voiceList} showsVerticalScrollIndicator={false}>
        {availableVoices.map((voice) => (
          <TouchableOpacity
            key={voice.id}
            style={[
              styles.voiceItem,
              selectedVoice === voice.id && styles.selectedVoiceItem
            ]}
            onPress={() => onVoiceSelect(voice.id)}
          >
            <View style={styles.voiceHeader}>
              <Text style={styles.voiceName}>{voice.name}</Text>
              <View style={styles.badges}>
                <View
                  style={[
                    styles.qualityBadge,
                    { backgroundColor: getQualityColor(voice.quality) }
                  ]}
                >
                  <Text style={styles.badgeText}>{voice.quality}</Text>
                </View>
                {voice.tier_required && (
                  <View
                    style={[
                      styles.tierBadge,
                      { backgroundColor: getTierBadgeColor(voice.tier_required) }
                    ]}
                  >
                    <Text style={styles.badgeText}>{voice.tier_required.toUpperCase()}</Text>
                  </View>
                )}
              </View>
            </View>
            
            <Text style={styles.voiceDescription}>{voice.description}</Text>
            
            <View style={styles.voiceDetails}>
              <Text style={styles.voiceEngine}>Engine: {voice.engine}</Text>
              <Text style={styles.voiceGender}>
                {voice.gender} • {voice.language || 'English'}
              </Text>
            </View>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Unavailable Voices (if any) */}
      {unavailableVoices.length > 0 && (
        <View style={styles.unavailableSection}>
          <Text style={styles.unavailableTitle}>
            Upgrade to access more voices
          </Text>
          
          {unavailableVoices.slice(0, 3).map((voice) => (
            <View key={voice.id} style={styles.unavailableVoiceItem}>
              <View style={styles.voiceHeader}>
                <Text style={[styles.voiceName, styles.unavailableText]}>
                  {voice.name}
                </Text>
                <View style={styles.badges}>
                  <View
                    style={[
                      styles.qualityBadge,
                      { backgroundColor: getQualityColor(voice.quality), opacity: 0.6 }
                    ]}
                  >
                    <Text style={styles.badgeText}>{voice.quality}</Text>
                  </View>
                  <View
                    style={[
                      styles.tierBadge,
                      { backgroundColor: getTierBadgeColor(voice.tier_required) }
                    ]}
                  >
                    <Text style={styles.badgeText}>{voice.tier_required.toUpperCase()}</Text>
                  </View>
                </View>
              </View>
              <Text style={[styles.voiceDescription, styles.unavailableText]}>
                {voice.description}
              </Text>
            </View>
          ))}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  loadingText: {
    marginLeft: 10,
    color: '#666',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  voiceList: {
    maxHeight: 300,
  },
  voiceItem: {
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    backgroundColor: '#f9f9f9',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  selectedVoiceItem: {
    backgroundColor: '#e3f2fd',
    borderColor: '#007AFF',
  },
  voiceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  voiceName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  badges: {
    flexDirection: 'row',
    gap: 5,
  },
  qualityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  tierBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  badgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  voiceDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  voiceDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  voiceEngine: {
    fontSize: 12,
    color: '#999',
  },
  voiceGender: {
    fontSize: 12,
    color: '#999',
  },
  unavailableSection: {
    marginTop: 20,
    paddingTop: 15,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  unavailableTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FF9800',
    marginBottom: 10,
    textAlign: 'center',
  },
  unavailableVoiceItem: {
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    backgroundColor: '#f5f5f5',
    opacity: 0.7,
  },
  unavailableText: {
    color: '#999',
  },
});