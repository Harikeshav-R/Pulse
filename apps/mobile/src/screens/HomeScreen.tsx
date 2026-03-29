import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, SafeAreaView } from 'react-native';
import { MessageCircle, Mic, Activity, Moon, Footprints, ChevronRight } from 'lucide-react-native';
import { colors, spacing, rounded } from '../theme';
import { useNavigation } from '@react-navigation/native';

export default function HomeScreen() {
  const navigation = useNavigation<any>();

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.greeting}>Hi David,</Text>
          <Text style={styles.date}>Thursday, March 28</Text>
        </View>

        {/* Check-in Status Card */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Daily Check-In</Text>
            <View style={styles.badgePending}>
              <Text style={styles.badgeText}>Pending</Text>
            </View>
          </View>
          <Text style={styles.cardSubtitle}>Your check-in window closes in 4 hours.</Text>
          
          <View style={styles.actionRow}>
            <TouchableOpacity 
              style={[styles.button, styles.buttonPrimary]}
              onPress={() => navigation.navigate('Chat')}
            >
              <MessageCircle size={20} color={colors.surfaceBg} />
              <Text style={styles.buttonTextLight}>Start Text Check-In</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.button, styles.buttonSecondary]}
              onPress={() => navigation.navigate('Voice')}
            >
              <Mic size={20} color={colors.mainColor} />
              <Text style={styles.buttonTextDark}>Start Voice Check-In</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Wearable Summary */}
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Latest Health Metrics</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Wearables')}>
            <Text style={styles.seeAll}>See All</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.metricsRow}>
          <View style={styles.metricCard}>
            <Activity color={colors.danger} size={24} />
            <Text style={styles.metricValue}>88<Text style={styles.metricUnit}> bpm</Text></Text>
            <Text style={styles.metricLabel}>Resting HR</Text>
            <Text style={styles.metricTrendDanger}>↑ Rising</Text>
          </View>

          <View style={styles.metricCard}>
            <Footprints color={colors.info} size={24} />
            <Text style={styles.metricValue}>3,200<Text style={styles.metricUnit}> steps</Text></Text>
            <Text style={styles.metricLabel}>Today</Text>
            <Text style={styles.metricTrendWarning}>↓ Declining</Text>
          </View>

          <View style={styles.metricCard}>
            <Moon color={colors.star} size={24} />
            <Text style={styles.metricValue}>5.2<Text style={styles.metricUnit}> hrs</Text></Text>
            <Text style={styles.metricLabel}>Sleep</Text>
            <Text style={styles.metricTrendWarning}>↓ Declining</Text>
          </View>
        </View>

        {/* Timeline Preview */}
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Recent Activity</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Timeline')}>
            <Text style={styles.seeAll}>See All</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.timelineCard}>
          <View style={styles.timelineItem}>
            <View style={[styles.timelineDot, { backgroundColor: colors.warning }]} />
            <View style={styles.timelineContent}>
              <Text style={styles.timelineTime}>Mar 27 • 8:00 AM</Text>
              <Text style={styles.timelineDesc}>Reported Nausea (Grade 2), Fatigue (Grade 1)</Text>
            </View>
            <ChevronRight size={20} color={colors.mutedBorder} />
          </View>
          <View style={[styles.timelineItem, { borderBottomWidth: 0, paddingBottom: 0 }]}>
            <View style={[styles.timelineDot, { backgroundColor: colors.success }]} />
            <View style={styles.timelineContent}>
              <Text style={styles.timelineTime}>Mar 26 • 8:15 AM</Text>
              <Text style={styles.timelineDesc}>Reported Fatigue (Grade 1)</Text>
            </View>
            <ChevronRight size={20} color={colors.mutedBorder} />
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.appBg,
  },
  container: {
    padding: spacing.m,
  },
  header: {
    marginBottom: spacing.l,
    marginTop: spacing.s,
  },
  greeting: {
    fontSize: 28,
    fontWeight: '700',
    color: colors.mainColor,
  },
  date: {
    fontSize: 16,
    color: colors.secondaryColor,
    marginTop: spacing.xs,
  },
  card: {
    backgroundColor: colors.surfaceBg,
    borderRadius: rounded.xl,
    padding: spacing.m,
    marginBottom: spacing.l,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.mainColor,
  },
  badgePending: {
    backgroundColor: colors.warning + '20',
    paddingHorizontal: spacing.s,
    paddingVertical: 4,
    borderRadius: rounded.m,
  },
  badgeText: {
    color: colors.warning,
    fontWeight: '700',
    fontSize: 12,
  },
  cardSubtitle: {
    fontSize: 14,
    color: colors.secondaryColor,
    marginBottom: spacing.m,
  },
  actionRow: {
    flexDirection: 'column',
    gap: spacing.s,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: rounded.l,
    gap: spacing.s,
  },
  buttonPrimary: {
    backgroundColor: colors.buttonBg,
  },
  buttonSecondary: {
    backgroundColor: colors.appBg,
    borderWidth: 1,
    borderColor: colors.messageBoxBorder,
  },
  buttonTextLight: {
    color: colors.surfaceBg,
    fontSize: 16,
    fontWeight: '600',
  },
  buttonTextDark: {
    color: colors.mainColor,
    fontSize: 16,
    fontWeight: '600',
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    marginBottom: spacing.m,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.mainColor,
  },
  seeAll: {
    fontSize: 14,
    color: colors.info,
    fontWeight: '600',
  },
  metricsRow: {
    flexDirection: 'row',
    gap: spacing.s,
    marginBottom: spacing.l,
  },
  metricCard: {
    flex: 1,
    backgroundColor: colors.surfaceBg,
    borderRadius: rounded.l,
    padding: spacing.m,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 1,
  },
  metricValue: {
    fontSize: 22,
    fontWeight: '700',
    color: colors.mainColor,
    marginTop: spacing.s,
  },
  metricUnit: {
    fontSize: 14,
    fontWeight: '400',
    color: colors.secondaryColor,
  },
  metricLabel: {
    fontSize: 12,
    color: colors.secondaryColor,
    marginTop: 2,
  },
  metricTrendDanger: {
    fontSize: 12,
    color: colors.danger,
    marginTop: spacing.s,
    fontWeight: '600',
  },
  metricTrendWarning: {
    fontSize: 12,
    color: colors.warning,
    marginTop: spacing.s,
    fontWeight: '600',
  },
  timelineCard: {
    backgroundColor: colors.surfaceBg,
    borderRadius: rounded.xl,
    padding: spacing.m,
  },
  timelineItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.s,
    borderBottomWidth: 1,
    borderBottomColor: colors.messageBoxBorder,
  },
  timelineDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: spacing.m,
  },
  timelineContent: {
    flex: 1,
  },
  timelineTime: {
    fontSize: 12,
    color: colors.secondaryColor,
    marginBottom: 2,
  },
  timelineDesc: {
    fontSize: 14,
    color: colors.mainColor,
    fontWeight: '500',
  },
});
