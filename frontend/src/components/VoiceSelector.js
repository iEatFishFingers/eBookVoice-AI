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
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './ui/Card';
import { colors, spacing, borderRadius, typography } from '../theme/colors';

export default function VoiceSelector({ selectedVoice, onVoiceSelect, userTier = 'free' }) {
  const [voices, setVoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const { getAuthHeaders } = useAuth();

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-app.onrender.com';
  
  // Mock voices for demo purposes
  const mockVoices = [
    {
      id: 'basic_0',
      name: 'Sarah',
      description: 'Clear and natural female voice',
      quality: 'Standard',
      tier_required: 'free',
      engine: 'Basic TTS',
      gender: 'Female',
      language: 'English'
    },
    {
      id: 'premium_1',
      name: 'David',
      description: 'Professional male narrator voice',
      quality: 'High',
      tier_required: 'professional',
      engine: 'Premium TTS',
      gender: 'Male',
      language: 'English'
    },
    {
      id: 'premium_2',
      name: 'Emma',
      description: 'Expressive female storytelling voice',
      quality: 'Premium',
      tier_required: 'professional',
      engine: 'Premium TTS',
      gender: 'Female',
      language: 'English'
    }
  ];

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
        console.error('Failed to fetch voices, using mock data:', data.error);
        setVoices(mockVoices);
        if (!selectedVoice) {
          onVoiceSelect('basic_0');
        }
      }
    } catch (error) {
      console.error('Voice fetch error, using mock data:', error);
      setVoices(mockVoices);
      if (!selectedVoice) {
        onVoiceSelect('basic_0');
      }
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
      case 'Premium': return colors.success;
      case 'High': return colors.warning;
      case 'Standard': return colors.info;
      default: return colors.foreground.disabled;
    }
  };

  const getTierBadgeColor = (tier) => {
    switch (tier) {
      case 'enterprise': return colors.error;
      case 'professional': return colors.success;
      case 'free': return colors.foreground.disabled;
      default: return colors.foreground.disabled;
    }
  };

  if (loading) {
    return (
      <Card style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="small" color={colors.primary} />
          <Text style={styles.loadingText}>Loading voices...</Text>
        </View>
      </Card>
    );
  }

  const availableVoices = voices.filter(isVoiceAvailable);
  const unavailableVoices = voices.filter(voice => !isVoiceAvailable(voice));

  return (
    <Card style={styles.container}>
      <CardHeader>
        <CardTitle>Select Voice</CardTitle>
        <CardDescription>Choose your preferred narrator voice</CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollView style={styles.voiceList} showsVerticalScrollIndicator={false}>
          {availableVoices.map((voice) => (
            <TouchableOpacity
              key={voice.id}
              style={[
                styles.voiceItem,
                selectedVoice === voice.id && styles.selectedVoiceItem
              ]}
              onPress={() => onVoiceSelect(voice.id)}
              activeOpacity={0.7}
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
      </CardContent>
    </Card>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: spacing.lg,
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.lg,
  },
  loadingText: {
    marginLeft: spacing.md,
    color: colors.foreground.muted,
    fontSize: typography.fontSizes.sm,
  },
  voiceList: {
    maxHeight: 300,
  },
  voiceItem: {
    padding: spacing.md,
    borderRadius: borderRadius.md,
    marginBottom: spacing.md,
    backgroundColor: colors.background.tertiary,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  selectedVoiceItem: {
    backgroundColor: colors.background.secondary,
    borderColor: colors.primary,
  },
  voiceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  voiceName: {
    fontSize: typography.fontSizes.md,
    fontWeight: typography.fontWeights.bold,
    color: colors.foreground.primary,
    flex: 1,
  },
  badges: {
    flexDirection: 'row',
    gap: spacing.xs,
  },
  qualityBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.md,
  },
  tierBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.md,
  },
  badgeText: {
    color: colors.foreground.primary,
    fontSize: typography.fontSizes.xs,
    fontWeight: typography.fontWeights.bold,
  },
  voiceDescription: {
    fontSize: typography.fontSizes.sm,
    color: colors.foreground.muted,
    marginBottom: spacing.sm,
    lineHeight: typography.lineHeights.normal * typography.fontSizes.sm,
  },
  voiceDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  voiceEngine: {
    fontSize: typography.fontSizes.xs,
    color: colors.foreground.disabled,
  },
  voiceGender: {
    fontSize: typography.fontSizes.xs,
    color: colors.foreground.disabled,
  },
  unavailableSection: {
    marginTop: spacing.lg,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border.default,
  },
  unavailableTitle: {
    fontSize: typography.fontSizes.md,
    fontWeight: typography.fontWeights.bold,
    color: colors.warning,
    marginBottom: spacing.md,
    textAlign: 'center',
  },
  unavailableVoiceItem: {
    padding: spacing.md,
    borderRadius: borderRadius.md,
    marginBottom: spacing.md,
    backgroundColor: colors.background.tertiary,
    opacity: 0.7,
  },
  unavailableText: {
    color: colors.foreground.disabled,
  },
});