import React from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView, TouchableOpacity } from 'react-native';
import { ChevronRight, ArrowLeft } from 'lucide-react-native';
import { colors, spacing, rounded } from '../theme';

export default function TimelineScreen() {
  const events = [
    {
      id: '1',
      date: 'Mar 28 • 8:15 AM',
      title: 'Reported Nausea (Grade 3), Headache (Grade 2)',
      type: 'critical',
      description: 'AI confidence: 0.94, 0.91',
    },
    {
      id: '2',
      date: 'Mar 28 • 8:00 AM',
      title: 'Resting HR elevated (88 bpm)',
      type: 'warning',
      description: 'Z-score: +3.2',
    },
    {
      id: '3',
      date: 'Mar 27 • 8:00 AM',
      title: 'Reported Nausea (Grade 2), Fatigue (Grade 1)',
      type: 'warning',
      description: 'CRC Reviewed by J. Smith',
    },
    {
      id: '4',
      date: 'Mar 26 • 8:15 AM',
      title: 'Reported Fatigue (Grade 1)',
      type: 'success',
      description: 'AI confidence: 0.88',
    },
    {
      id: '5',
      date: 'Mar 22 • 9:00 AM',
      title: 'Missed scheduled check-in',
      type: 'warning',
      description: '1st missed check-in',
    },
  ];

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.header}>
        <Text style={styles.title}>Health Timeline</Text>
      </View>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.filters}>
          <TouchableOpacity style={[styles.filterChip, styles.filterActive]}>
            <Text style={styles.filterTextActive}>All</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.filterChip}>
            <Text style={styles.filterText}>Symptoms</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.filterChip}>
            <Text style={styles.filterText}>Alerts</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.timeline}>
          {events.map((ev, index) => {
            let dotColor = colors.info;
            if (ev.type === 'critical') dotColor = colors.danger;
            if (ev.type === 'warning') dotColor = colors.warning;
            if (ev.type === 'success') dotColor = colors.success;

            return (
              <View style={styles.timelineEvent} key={ev.id}>
                {/* Line connects dots */}
                {index !== events.length - 1 && <View style={styles.timelineLine} />}
                
                <View style={[styles.dot, { backgroundColor: dotColor }]} />
                <View style={styles.contentCard}>
                  <Text style={styles.time}>{ev.date}</Text>
                  <Text style={styles.eventTitle}>{ev.title}</Text>
                  <Text style={styles.eventDesc}>{ev.description}</Text>
                </View>
              </View>
            );
          })}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: colors.appBg },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.m,
    backgroundColor: colors.surfaceBg,
    borderBottomWidth: 1,
    borderBottomColor: colors.messageBoxBorder,
  },
  title: { fontSize: 20, fontWeight: '700', color: colors.mainColor, marginLeft: spacing.s },
  container: { padding: spacing.m, paddingBottom: 100 },
  filters: { flexDirection: 'row', gap: spacing.s, marginBottom: spacing.l },
  filterChip: {
    paddingHorizontal: spacing.m,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: colors.surfaceBg,
    borderWidth: 1,
    borderColor: colors.messageBoxBorder,
  },
  filterActive: { backgroundColor: colors.mainColor, borderColor: colors.mainColor },
  filterText: { color: colors.secondaryColor, fontWeight: '600' },
  filterTextActive: { color: colors.surfaceBg, fontWeight: '600' },
  timeline: { paddingLeft: 10 },
  timelineEvent: { flexDirection: 'row', marginBottom: spacing.xl, position: 'relative' },
  dot: { width: 14, height: 14, borderRadius: 7, marginTop: 4, zIndex: 2 },
  timelineLine: {
    position: 'absolute',
    left: 6,
    top: 18,
    bottom: -spacing.xl,
    width: 2,
    backgroundColor: colors.messageBoxBorder,
    zIndex: 1,
  },
  contentCard: {
    flex: 1,
    marginLeft: spacing.m,
    backgroundColor: colors.surfaceBg,
    padding: spacing.m,
    borderRadius: rounded.l,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 1,
  },
  time: { fontSize: 12, color: colors.secondaryColor, marginBottom: spacing.xs, fontWeight: '600' },
  eventTitle: { fontSize: 16, fontWeight: '700', color: colors.mainColor, marginBottom: 4 },
  eventDesc: { fontSize: 14, color: colors.secondaryColor },
});
