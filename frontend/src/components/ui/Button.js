import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { colors, spacing, borderRadius, typography } from '../../theme/colors';

const Button = ({ 
  variant = 'default', 
  size = 'default', 
  children, 
  onPress, 
  disabled = false, 
  loading = false,
  style,
  textStyle,
  ...props 
}) => {
  const buttonStyles = [
    styles.base,
    styles[size],
    !disabled && styles[variant],
    disabled && styles.disabled,
    style,
  ];

  const textStyles = [
    styles.baseText,
    styles[`${size}Text`],
    styles[`${variant}Text`],
    disabled && styles.disabledText,
    textStyle,
  ];

  if (variant === 'gradient' || variant === 'hero') {
    return (
      <TouchableOpacity
        onPress={onPress}
        disabled={disabled || loading}
        activeOpacity={0.8}
        style={[styles.base, styles[size], style]}
        {...props}
      >
        <LinearGradient
          colors={['#8B5DFF', '#9B6CFF']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={[styles.gradient, disabled && styles.disabledGradient]}
        >
          {loading ? (
            <ActivityIndicator color={colors.foreground.primary} />
          ) : (
            <Text style={textStyles}>{children}</Text>
          )}
        </LinearGradient>
      </TouchableOpacity>
    );
  }

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.8}
      style={buttonStyles}
      {...props}
    >
      {loading ? (
        <ActivityIndicator color={
          variant === 'outline' || variant === 'ghost' 
            ? colors.primary 
            : colors.foreground.primary
        } />
      ) : (
        <Text style={textStyles}>{children}</Text>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  base: {
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: borderRadius.lg,
    flexDirection: 'row',
  },
  
  // Sizes
  default: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    minHeight: 44,
  },
  sm: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    minHeight: 36,
    borderRadius: borderRadius.md,
  },
  lg: {
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.lg,
    minHeight: 48,
    borderRadius: borderRadius.xl,
  },
  
  // Variants
  default: {
    backgroundColor: colors.primary,
  },
  outline: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: colors.border.default,
  },
  ghost: {
    backgroundColor: 'transparent',
  },
  glass: {
    backgroundColor: colors.background.glassmorphism,
    borderWidth: 1,
    borderColor: colors.border.glassmorphism,
  },
  destructive: {
    backgroundColor: colors.error,
  },
  
  // Gradient wrapper
  gradient: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: borderRadius.lg,
    minHeight: 44,
  },
  
  // Disabled states
  disabled: {
    opacity: 0.5,
  },
  disabledGradient: {
    opacity: 0.5,
  },
  
  // Text styles
  baseText: {
    fontSize: typography.fontSizes.md,
    fontWeight: typography.fontWeights.medium,
  },
  smText: {
    fontSize: typography.fontSizes.sm,
  },
  lgText: {
    fontSize: typography.fontSizes.lg,
    fontWeight: typography.fontWeights.semibold,
  },
  
  // Variant text colors
  defaultText: {
    color: colors.foreground.primary,
  },
  gradientText: {
    color: colors.foreground.primary,
    fontWeight: typography.fontWeights.semibold,
  },
  heroText: {
    color: colors.foreground.primary,
    fontWeight: typography.fontWeights.semibold,
    fontSize: typography.fontSizes.lg,
  },
  outlineText: {
    color: colors.foreground.primary,
  },
  ghostText: {
    color: colors.primary,
  },
  glassText: {
    color: colors.foreground.primary,
  },
  destructiveText: {
    color: colors.foreground.primary,
  },
  disabledText: {
    color: colors.foreground.disabled,
  },
});

export default Button;