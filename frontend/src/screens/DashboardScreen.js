import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  Platform,
} from 'react-native';
import { useAuth } from '../context/AuthContext';

export default function DashboardScreen() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { getAuthHeaders, user, logout } = useAuth();

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-app.onrender.com';

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
        console.error('Dashboard fetch failed:', data.error);
      }
    } catch (error) {
      console.error('Dashboard error:', error);
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
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading dashboard...</Text>
      </View>
    );
  }

  if (!dashboardData) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Failed to load dashboard data</Text>
        <TouchableOpacity style={styles.retryButton} onPress={() => fetchDashboardData()}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const { usage, recent_conversions, statistics } = dashboardData;

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.welcomeText}>Welcome back!</Text>
          <Text style={styles.userNameText}>{user?.display_name}</Text>
        </View>
        <TouchableOpacity style={styles.logoutButton} onPress={logout}>
          <Text style={styles.logoutButtonText}>Logout</Text>
        </TouchableOpacity>
      </View>

      {/* Subscription Info */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Subscription</Text>
        <View style={styles.tierContainer}>
          <View
            style={[
              styles.tierBadge,
              { backgroundColor: getTierColor(user?.subscription_tier) }
            ]}
          >
            <Text style={styles.tierText}>
              {user?.subscription_tier?.toUpperCase() || 'FREE'}
            </Text>
          </View>
          <Text style={styles.memberSince}>
            Member since {formatDate(user?.member_since)}
          </Text>
        </View>
      </View>

      {/* Usage Statistics */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>This Month's Usage</Text>
        
        <View style={styles.usageRow}>
          <Text style={styles.usageLabel}>Conversions</Text>
          <Text style={styles.usageValue}>
            {usage?.current_month?.conversions_used || 0} / {usage?.current_month?.conversions_limit || 0}
          </Text>
        </View>
        
        <View style={styles.progressContainer}>
          <View
            style={[
              styles.progressBar,
              {
                width: `${Math.min(
                  100,
                  ((usage?.current_month?.conversions_used || 0) /
                    (usage?.current_month?.conversions_limit || 1)) * 100
                )}%`
              }
            ]}
          />
        </View>

        <View style={styles.usageRow}>
          <Text style={styles.usageLabel}>Words</Text>
          <Text style={styles.usageValue}>
            {(usage?.current_month?.words_used || 0).toLocaleString()} / {(usage?.current_month?.words_limit || 0).toLocaleString()}
          </Text>
        </View>
        
        <View style={styles.progressContainer}>
          <View
            style={[
              styles.progressBar,
              {
                width: `${Math.min(
                  100,
                  ((usage?.current_month?.words_used || 0) /
                    (usage?.current_month?.words_limit || 1)) * 100
                )}%`
              }
            ]}
          />
        </View>
      </View>

      {/* Statistics */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Statistics</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{statistics?.total_conversions || 0}</Text>
            <Text style={styles.statLabel}>Total Conversions</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{Math.round(statistics?.avg_words_per_conversion || 0)}</Text>
            <Text style={styles.statLabel}>Avg Words/Conversion</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{(statistics?.total_words || 0).toLocaleString()}</Text>
            <Text style={styles.statLabel}>Total Words</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{statistics?.total_downloads || 0}</Text>
            <Text style={styles.statLabel}>Total Downloads</Text>
          </View>
        </View>
      </View>

      {/* Recent Conversions */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Recent Conversions</Text>
        {recent_conversions && recent_conversions.length > 0 ? (
          recent_conversions.slice(0, 5).map((conversion, index) => (
            <View key={index} style={styles.conversionItem}>
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
              <View
                style={[
                  styles.statusDot,
                  { backgroundColor: getStatusColor(conversion.status) }
                ]}
              />
            </View>
          ))
        ) : (
          <Text style={styles.emptyText}>No conversions yet</Text>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    paddingTop: Platform.OS === 'web' ? 20 : 50,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 10,
    color: '#666',
    fontSize: 16,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    paddingHorizontal: 20,
  },
  errorText: {
    color: '#F44336',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  welcomeText: {
    fontSize: 16,
    color: '#666',
  },
  userNameText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  logoutButton: {
    backgroundColor: '#F44336',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 8,
  },
  logoutButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  card: {
    backgroundColor: '#fff',
    marginHorizontal: 20,
    marginBottom: 15,
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  tierContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  tierBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
  },
  tierText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 12,
  },
  memberSince: {
    color: '#666',
    fontSize: 14,
  },
  usageRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  usageLabel: {
    fontSize: 16,
    color: '#333',
  },
  usageValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  progressContainer: {
    height: 6,
    backgroundColor: '#e0e0e0',
    borderRadius: 3,
    marginBottom: 15,
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 3,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statItem: {
    width: '48%',
    alignItems: 'center',
    marginBottom: 15,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  conversionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  conversionInfo: {
    flex: 1,
  },
  conversionTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 4,
  },
  conversionDetails: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  conversionDate: {
    fontSize: 12,
    color: '#999',
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginLeft: 10,
  },
  emptyText: {
    textAlign: 'center',
    color: '#999',
    fontStyle: 'italic',
  },
});