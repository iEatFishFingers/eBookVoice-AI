import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { colors, spacing, borderRadius, typography } from '../../theme/colors';

export const Card = ({ children, variant = 'default', style, ...props }) => {
  if (variant === 'gradient') {
    return (
      <View style={[styles.wrapper, style]}>
        <LinearGradient
          colors={['rgba(139, 93, 255, 0.1)', 'rgba(155, 108, 255, 0.1)']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.gradientCard}
        >
          {children}
        </LinearGradient>
      </View>
    );
  }

  if (variant === 'glass') {
    return (
      <View style={[styles.base, styles.glass, style]} {...props}>
        {children}
      </View>
    );
  }

  return (
    <View style={[styles.base, styles.default, style]} {...props}>
      {children}
    </View>
  );
};

export const CardHeader = ({ children, style, ...props }) => (
  <View style={[styles.header, style]} {...props}>
    {children}
  </View>
);

export const CardTitle = ({ children, style, ...props }) => (
  <Text style={[styles.title, style]} {...props}>
    {children}
  </Text>
);

export const CardDescription = ({ children, style, ...props }) => (
  <Text style={[styles.description, style]} {...props}>
    {children}
  </Text>
);

export const CardContent = ({ children, style, ...props }) => (
  <View style={[styles.content, style]} {...props}>
    {children}
  </View>
);

export const CardFooter = ({ children, style, ...props }) => (
  <View style={[styles.footer, style]} {...props}>
    {children}
  </View>
);

const styles = StyleSheet.create({
  wrapper: {
    borderRadius: borderRadius.lg,
  },
  
  base: {
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    ...colors.shadows.card,
  },
  
  default: {
    backgroundColor: colors.background.secondary,
    borderWidth: 1,
    borderColor: colors.border.default,
  },
  
  glass: {
    backgroundColor: colors.background.glassmorphism,
    borderWidth: 1,
    borderColor: colors.border.glassmorphism,
  },
  
  gradientCard: {
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: 'rgba(139, 93, 255, 0.2)',
  },
  
  header: {
    marginBottom: spacing.md,
  },
  
  title: {
    fontSize: typography.fontSizes.xl,
    fontWeight: typography.fontWeights.semibold,
    color: colors.foreground.primary,
    marginBottom: spacing.xs,
  },
  
  description: {
    fontSize: typography.fontSizes.sm,
    color: colors.foreground.muted,
    lineHeight: typography.lineHeights.normal * typography.fontSizes.sm,
  },
  
  content: {
    flex: 1,
  },
  
  footer: {
    marginTop: spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
  },
});

export default Card;