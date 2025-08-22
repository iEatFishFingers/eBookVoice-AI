import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Platform,
  Alert,
} from 'react-native';
import { Audio } from 'expo-av';
import Button from './ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card';
import { colors, spacing, borderRadius, typography } from '../theme/colors';

export default function AudioPlayer({ audioUrl, title, onClose }) {
  const [sound, setSound] = useState(null);
  const [status, setStatus] = useState({});
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [duration, setDuration] = useState(0);
  const [position, setPosition] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  
  // Ref to track if component is mounted
  const mountedRef = useRef(true);
  
  useEffect(() => {
    mountedRef.current = true;
    loadAudio();
    
    return () => {
      mountedRef.current = false;
      unloadAudio();
    };
  }, []);

  useEffect(() => {
    // Update position if not currently dragging
    if (status.positionMillis && !isDragging && mountedRef.current) {
      setPosition(status.positionMillis);
    }
    
    // Update duration
    if (status.durationMillis && mountedRef.current) {
      setDuration(status.durationMillis);
    }
    
    // Update playing state
    if (status.isPlaying !== undefined && mountedRef.current) {
      setIsPlaying(status.isPlaying);
    }
  }, [status, isDragging]);

  const loadAudio = async () => {
    try {
      setIsLoading(true);
      
      // Configure audio session for playback
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
        staysActiveInBackground: false,
        playsInSilentModeIOS: true,
        shouldDuckAndroid: true,
        playThroughEarpieceAndroid: false,
      });

      const { sound: newSound } = await Audio.Sound.createAsync(
        { uri: audioUrl },
        { shouldPlay: false },
        onPlaybackStatusUpdate
      );
      
      if (mountedRef.current) {
        setSound(newSound);
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Error loading audio:', error);
      if (mountedRef.current) {
        setIsLoading(false);
        Alert.alert('Error', 'Failed to load audio file. Please try again.');
      }
    }
  };

  const unloadAudio = async () => {
    if (sound) {
      try {
        await sound.unloadAsync();
      } catch (error) {
        console.error('Error unloading audio:', error);
      }
    }
  };

  const onPlaybackStatusUpdate = (status) => {
    if (mountedRef.current) {
      setStatus(status);
    }
  };

  const playPauseAudio = async () => {
    if (!sound) return;
    
    try {
      if (isPlaying) {
        await sound.pauseAsync();
      } else {
        await sound.playAsync();
      }
    } catch (error) {
      console.error('Error playing/pausing audio:', error);
      Alert.alert('Error', 'Failed to control audio playback.');
    }
  };

  const seekToPosition = async (value) => {
    if (!sound || !duration) return;
    
    try {
      const seekPosition = value * duration;
      await sound.setPositionAsync(seekPosition);
      setPosition(seekPosition);
    } catch (error) {
      console.error('Error seeking audio:', error);
    }
  };

  const skipBackward = async () => {
    if (!sound) return;
    
    try {
      const newPosition = Math.max(0, position - 15000); // Skip back 15 seconds
      await sound.setPositionAsync(newPosition);
    } catch (error) {
      console.error('Error skipping backward:', error);
    }
  };

  const skipForward = async () => {
    if (!sound) return;
    
    try {
      const newPosition = Math.min(duration, position + 15000); // Skip forward 15 seconds
      await sound.setPositionAsync(newPosition);
    } catch (error) {
      console.error('Error skipping forward:', error);
    }
  };

  const formatTime = (millis) => {
    const totalSeconds = Math.floor(millis / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <Card style={styles.container}>
      <CardHeader>
        <View style={styles.headerRow}>
          <CardTitle style={styles.title} numberOfLines={1}>
            {title || 'Audiobook'}
          </CardTitle>
          <Button
            onPress={onClose}
            variant="ghost"
            size="sm"
          >
            ✕
          </Button>
        </View>
      </CardHeader>
      
      <CardContent>
        {isLoading ? (
          <View style={styles.loadingContainer}>
            <Text style={styles.loadingText}>Loading audio...</Text>
          </View>
        ) : (
          <>
            {/* Progress Slider */}
            <View style={styles.progressContainer}>
              <Text style={styles.timeText}>
                {formatTime(position)}
              </Text>
              <View style={styles.progressBar}>
                <View 
                  style={[
                    styles.progressFill,
                    { width: `${duration > 0 ? (position / duration) * 100 : 0}%` }
                  ]}
                />
                <TouchableOpacity
                  style={[
                    styles.progressThumb,
                    { left: `${duration > 0 ? (position / duration) * 100 : 0}%` }
                  ]}
                  onPress={() => {}}
                />
              </View>
              <Text style={styles.timeText}>
                {formatTime(duration)}
              </Text>
            </View>

            {/* Control Buttons */}
            <View style={styles.controlsContainer}>
              <Button
                onPress={skipBackward}
                variant="ghost"
                size="sm"
                style={styles.controlButton}
              >
                ⏪ 15s
              </Button>
              
              <Button
                onPress={playPauseAudio}
                variant="gradient"
                size="lg"
                style={styles.playButton}
              >
                {isPlaying ? '⏸️' : '▶️'}
              </Button>
              
              <Button
                onPress={skipForward}
                variant="ghost"
                size="sm"
                style={styles.controlButton}
              >
                15s ⏩
              </Button>
            </View>

            {/* Audio Info */}
            <View style={styles.infoContainer}>
              <Text style={styles.infoText}>
                Tap and hold the slider to scrub through the audio
              </Text>
            </View>
          </>
        )}
      </CardContent>
    </Card>
  );
}

const styles = StyleSheet.create({
  container: {
    margin: spacing.md,
    maxWidth: Platform.OS === 'web' ? 500 : '100%',
    alignSelf: 'center',
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  title: {
    flex: 1,
    marginRight: spacing.md,
  },
  loadingContainer: {
    alignItems: 'center',
    paddingVertical: spacing.xl,
  },
  loadingText: {
    color: colors.foreground.muted,
    fontSize: typography.fontSizes.md,
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  timeText: {
    color: colors.foreground.muted,
    fontSize: typography.fontSizes.sm,
    minWidth: 40,
    textAlign: 'center',
  },
  progressBar: {
    flex: 1,
    height: 6,
    backgroundColor: colors.background.tertiary,
    borderRadius: 3,
    marginHorizontal: spacing.md,
    position: 'relative',
  },
  progressFill: {
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: 3,
  },
  progressThumb: {
    position: 'absolute',
    top: -7,
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: colors.primary,
    transform: [{ translateX: -10 }],
  },
  controlsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.lg,
    gap: spacing.lg,
  },
  controlButton: {
    minWidth: 60,
  },
  playButton: {
    minWidth: 80,
    minHeight: 60,
  },
  infoContainer: {
    alignItems: 'center',
  },
  infoText: {
    color: colors.foreground.disabled,
    fontSize: typography.fontSizes.xs,
    textAlign: 'center',
    fontStyle: 'italic',
  },
});