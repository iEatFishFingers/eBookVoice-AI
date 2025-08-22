import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  RefreshControl,
  ActivityIndicator,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useAuth } from '../context/AuthContext';
import Button from '../components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import { colors, spacing, borderRadius, typography } from '../theme/colors';

export default function DashboardScreen() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { getAuthHeaders, user, logout } = useAuth();
  
  // Mock data for demo purposes when no real backend connection
  const mockDashboardData = {
    usage: {
      current_month: {
        conversions_used: 3,
        conversions_remaining: 7,
        words_used: 1250,
        words_remaining: 8750
      }
    },
    recent_conversions: [
      {
        id: '1',
        original_filename: 'Chapter 1.pdf',
        word_count: 450,
        voice_used: 'Premium Voice',
        status: 'completed',
        created_at: new Date().toISOString()
      },
      {
        id: '2', 
        original_filename: 'Novel Draft.docx',
        word_count: 800,
        voice_used: 'Standard Voice',
        status: 'processing',
        created_at: new Date().toISOString()
      }
    ],
    statistics: {
      total_conversions: 12,
      avg_words_per_conversion: 625,
      total_words: 7500,
      total_downloads: 8
    }
  };

  const API_BASE_URL = 'https://ebookvoice-backend.onrender.com';

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      const response = await fetch(`${API_BASE_URL}/api/dashboard`, {
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setDashboardData(data.data);
      } else {
        console.error('Dashboard fetch failed, using mock data');
        setDashboardData(mockDashboardData);
      }
    } catch (error) {
      console.error('Dashboard error, using mock data:', error);
      setDashboardData(mockDashboardData);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    fetchDashboardData(true);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getTierColor = (tier) => {
    switch (tier) {
      case 'free': return '#9E9E9E';
      case 'professional': return '#4CAF50';
      case 'enterprise': return '#FF9800';
      default: return '#9E9E9E';
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

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading dashboard...</Text>
      </View>
    );
  }

  if (!dashboardData) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Failed to load dashboard data</Text>
        <Button onPress={() => fetchDashboardData()} variant="gradient">
          Retry
        </Button>
      </View>
    );
  }

  const { usage, recent_conversions, statistics } = dashboardData || mockDashboardData;

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
            <Text style={styles.welcomeText}>Welcome back!</Text>
            <Text style={styles.userNameText}>{user?.display_name}</Text>
          </View>
          <Button onPress={logout} variant="glass" size="sm">
            Settings
          </Button>
        </View>
      </LinearGradient>
      
      <ScrollView
        style={styles.scrollContainer}
        refreshControl={
          <RefreshControl 
            refreshing={refreshing} 
            onRefresh={onRefresh}
            tintColor={colors.primary}
            colors={[colors.primary]}
          />
        }
      >

        {/* Subscription Info */}
        <Card variant="gradient" style={styles.subscriptionCard}>
          <CardHeader>
            <CardTitle>Subscription Status</CardTitle>
            <CardDescription>Your current plan and benefits</CardDescription>
          </CardHeader>
          <CardContent>
            <View style={styles.tierContainer}>
              <View style={[
                styles.tierBadge,
                { backgroundColor: getTierColor(user?.subscription_tier) }
              ]}>
                <Text style={styles.tierText}>
                  {user?.subscription_tier?.toUpperCase() || 'FREE'}
                </Text>
              </View>
              <Text style={styles.memberSince}>
                Premium features available
              </Text>
            </View>
          </CardContent>
        </Card>

        {/* Usage Statistics */}
        <Card style={styles.usageCard}>
          <CardHeader>
            <CardTitle>This Month's Usage</CardTitle>
            <CardDescription>Track your conversion and word limits</CardDescription>
          </CardHeader>
          <CardContent>
            <View style={styles.usageItem}>
              <View style={styles.usageRow}>
                <Text style={styles.usageLabel}>Conversions</Text>
                <Text style={styles.usageValue}>
                  {usage?.current_month?.conversions_used || 0} / {(usage?.current_month?.conversions_used || 0) + (usage?.current_month?.conversions_remaining || 10)}
                </Text>
              </View>
              <View style={styles.progressContainer}>
                <View style={[
                  styles.progressBar,
                  {
                    width: `${Math.min(100, ((usage?.current_month?.conversions_used || 0) / ((usage?.current_month?.conversions_used || 0) + (usage?.current_month?.conversions_remaining || 10))) * 100)}%`
                  }
                ]}/>
              </View>
            </View>

            <View style={styles.usageItem}>
              <View style={styles.usageRow}>
                <Text style={styles.usageLabel}>Words</Text>
                <Text style={styles.usageValue}>
                  {(usage?.current_month?.words_used || 0).toLocaleString()} / {((usage?.current_month?.words_used || 0) + (usage?.current_month?.words_remaining || 10000)).toLocaleString()}
                </Text>
              </View>
              <View style={styles.progressContainer}>
                <View style={[
                  styles.progressBar,
                  {
                    width: `${Math.min(100, ((usage?.current_month?.words_used || 0) / ((usage?.current_month?.words_used || 0) + (usage?.current_month?.words_remaining || 10000))) * 100)}%`
                  }
                ]}/>
              </View>
            </View>
          </CardContent>
        </Card>

        {/* Statistics */}
        <Card style={styles.statsCard}>
          <CardHeader>
            <CardTitle>Analytics Overview</CardTitle>
            <CardDescription>Your usage statistics and performance</CardDescription>
          </CardHeader>
          <CardContent>
            <View style={styles.statsGrid}>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{statistics?.total_conversions || 0}</Text>
                <Text style={styles.statLabel}>Total Conversions</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{Math.round(statistics?.avg_words_per_conversion || 0)}</Text>
                <Text style={styles.statLabel}>Avg Words</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{(statistics?.total_words || 0).toLocaleString()}</Text>
                <Text style={styles.statLabel}>Total Words</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{statistics?.total_downloads || 0}</Text>
                <Text style={styles.statLabel}>Downloads</Text>
              </View>
            </View>
          </CardContent>
        </Card>

        {/* Recent Conversions */}
        <Card style={styles.conversionsCard}>
          <CardHeader>
            <CardTitle>Recent Conversions</CardTitle>
            <CardDescription>Your latest audiobook projects</CardDescription>
          </CardHeader>
          <CardContent>
            {recent_conversions && recent_conversions.length > 0 ? (
              recent_conversions.slice(0, 5).map((conversion, index) => (
                <View key={conversion.id || index} style={styles.conversionItem}>
                  <View style={styles.conversionInfo}>
                    <Text style={styles.conversionTitle} numberOfLines={1}>
                      {conversion.original_filename}
                    </Text>
                    <Text style={styles.conversionDetails}>
                      {conversion.word_count} words • {conversion.voice_used}
                    </Text>
                    <Text style={styles.conversionDate}>
                      {formatDate(conversion.created_at)}
                    </Text>
                  </View>
                  <View style={[
                    styles.statusDot,
                    { backgroundColor: getStatusColor(conversion.status) }
                  ]}/>
                </View>
              ))
            ) : (
              <Text style={styles.emptyText}>No conversions yet</Text>
            )}
          </CardContent>
        </Card>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background.primary,
  },
  scrollContainer: {
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
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background.primary,
    paddingHorizontal: spacing.lg,
  },
  errorText: {
    color: colors.error,
    fontSize: typography.fontSizes.md,
    textAlign: 'center',
    marginBottom: spacing.lg,
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
  welcomeText: {
    fontSize: typography.fontSizes.md,
    color: colors.foreground.primary,
    opacity: 0.9,
  },
  userNameText: {
    fontSize: typography.fontSizes.xxxl,
    fontWeight: typography.fontWeights.bold,
    color: colors.foreground.primary,
    marginTop: spacing.xs,
  },
  subscriptionCard: {
    marginTop: spacing.lg,
    marginBottom: spacing.md,
  },
  usageCard: {
    marginBottom: spacing.md,
  },
  statsCard: {
    marginBottom: spacing.md,
  },
  conversionsCard: {
    marginBottom: spacing.lg,
  },
  tierContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  tierBadge: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.md,
  },
  tierText: {
    color: colors.foreground.primary,
    fontWeight: typography.fontWeights.bold,
    fontSize: typography.fontSizes.xs,
  },
  memberSince: {
    color: colors.foreground.muted,
    fontSize: typography.fontSizes.sm,
  },
  usageItem: {
    marginBottom: spacing.lg,
  },
  usageRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  usageLabel: {
    fontSize: typography.fontSizes.md,
    color: colors.foreground.primary,
  },
  usageValue: {
    fontSize: typography.fontSizes.md,
    fontWeight: typography.fontWeights.bold,
    color: colors.primary,
  },
  progressContainer: {
    height: 6,
    backgroundColor: colors.background.tertiary,
    borderRadius: borderRadius.sm,
  },
  progressBar: {
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: borderRadius.sm,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statItem: {
    width: '48%',
    alignItems: 'center',
    marginBottom: spacing.md,
    padding: spacing.md,
    backgroundColor: colors.background.tertiary,
    borderRadius: borderRadius.md,
  },
  statValue: {
    fontSize: typography.fontSizes.xxl,
    fontWeight: typography.fontWeights.bold,
    color: colors.primary,
  },
  statLabel: {
    fontSize: typography.fontSizes.xs,
    color: colors.foreground.muted,
    textAlign: 'center',
    marginTop: spacing.xs,
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
  conversionDetails: {
    fontSize: typography.fontSizes.sm,
    color: colors.foreground.muted,
    marginBottom: 2,
  },
  conversionDate: {
    fontSize: typography.fontSizes.xs,
    color: colors.foreground.disabled,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginLeft: spacing.md,
  },
  emptyText: {
    textAlign: 'center',
    color: colors.foreground.muted,
    fontStyle: 'italic',
  },
});