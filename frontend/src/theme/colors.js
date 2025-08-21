// eBookVoice AI Design System
// Based on the visual language from the old version
// All colors are HSL-based for consistency

export const colors = {
  // Brand Colors
  primary: '#8B5DFF', // hsl(256 65% 60%)
  primaryGlow: '#A674FF', // hsl(268 70% 75%)
  accent: '#9B6CFF', // hsl(268 70% 65%)
  
  // Background System
  background: {
    primary: '#0A0A0F', // hsl(240 10% 4%)
    secondary: '#0F0F16', // hsl(240 10% 6%)
    tertiary: '#1A1A26', // hsl(240 5% 15%)
    glassmorphism: 'rgba(255, 255, 255, 0.05)',
  },
  
  // Foreground/Text
  foreground: {
    primary: '#FFFFFF', // hsl(0 0% 100%)
    secondary: '#E6E6E6', // hsl(0 0% 90%)
    muted: '#A6A6A6', // hsl(240 5% 65%)
    disabled: '#666666', // hsl(0 0% 40%)
  },
  
  // Interactive States
  border: {
    default: '#262633', // hsl(240 5% 15%)
    input: '#262633',
    focus: '#8B5DFF',
    glassmorphism: 'rgba(255, 255, 255, 0.1)',
  },
  
  // Status Colors
  success: '#4ADE80', // Green
  warning: '#FBBF24', // Amber
  error: '#EF4444', // Red
  info: '#3B82F6', // Blue
  
  // Gradients
  gradients: {
    primary: 'linear-gradient(135deg, #8B5DFF 0%, #9B6CFF 100%)',
    hero: 'linear-gradient(135deg, #8B5DFF 0%, #9B6CFF 100%)',
    card: 'linear-gradient(135deg, rgba(139, 93, 255, 0.1) 0%, rgba(155, 108, 255, 0.1) 100%)',
  },
  
  // Shadows
  shadows: {
    elegant: {
      shadowColor: '#8B5DFF',
      shadowOffset: { width: 0, height: 10 },
      shadowOpacity: 0.4,
      shadowRadius: 20,
      elevation: 15,
    },
    glow: {
      shadowColor: '#8B5DFF',
      shadowOffset: { width: 0, height: 0 },
      shadowOpacity: 0.3,
      shadowRadius: 20,
      elevation: 10,
    },
    card: {
      shadowColor: '#000000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 8,
      elevation: 5,
    },
  },
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
  xxxl: 64,
};

export const borderRadius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  full: 9999,
};

export const typography = {
  fontSizes: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 20,
    xxl: 24,
    xxxl: 32,
    hero: 40,
  },
  fontWeights: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    extrabold: '800',
  },
  lineHeights: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.75,
  },
};