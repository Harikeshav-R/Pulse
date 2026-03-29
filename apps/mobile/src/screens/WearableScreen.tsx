import React from 'react';
import { View, Text, StyleSheet, ScrollView, SafeAreaView } from 'react-native';
import { Activity, Moon, Footprints, Droplets, Battery } from 'lucide-react-native';
import { colors, spacing, rounded } from '../theme';

export default function WearableScreen() {
  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>Wearable Dashboard</Text>
        </View>

        {/* Connection Status */}
        <View style={styles.connectionCard}>
          <View style={styles.row}>
            <View>
              <Text style={styles.deviceTitle}>Apple Watch Series 9</Text>
              <Text style={styles.syncStatus}>Last synced: 15 min ago</Text>
            </View>
            <View style={styles.batteryBadge}>
              <Battery size={16} color={colors.success} />
              <Text style={styles.batteryText}>84%</Text>
            </View>
          </View>
        </View>

        {/* Anomaly Alert */}
        <View style={styles.alertBanner}>
          <Activity size={20} color={colors.danger} />
          <View style={styles.alertContent}>
            <Text style={styles.alertTitle}>Resting HR Anomaly</Text>
            <Text style={styles.alertDesc}>Trend detected: +2.3 bpm/day over last 7 days.</Text>
          </View>
        </View>

        {/* Metrics Grid */}
        <View style={styles.metricsGrid}>
          {/* HR Card */}
          <View style={styles.metricCard}>
            <View style={styles.cardHeader}>
              <Activity color={colors.danger} size={20} />
              <Text style={styles.metricName}>Resting HR</Text>
            </View>
            <Text style={styles.metricValue}>88<Text style={styles.unit}> bpm</Text></Text>
            <View style={styles.chartMock}>
              <View style={styles.barDanger} />
              <View style={[styles.barDanger, { height: 25 }]} />
              <View style={[styles.barDanger, { height: 35 }]} />
              <View style={[styles.barDanger, { height: 50 }]} />
            </View>
            <View style={styles.baselineRange}>
              <Text style={styles.baselineText}>Baseline: 72±5</Text>
            </View>
          </View>

          {/* Steps Card */}
          <View style={styles.metricCard}>
            <View style={styles.cardHeader}>
              <Footprints color={colors.info} size={20} />
              <Text style={styles.metricName}>Steps</Text>
            </View>
            <Text style={styles.metricValue}>3,200<Text style={styles.unit}> steps</Text></Text>
            <View style={styles.chartMock}>
              <View style={styles.barInfo} />
              <View style={[styles.barInfo, { height: 35 }]} />
              <View style={[styles.barInfo, { height: 25 }]} />
              <View style={[styles.barInfo, { height: 15 }]} />
            </View>
            <View style={styles.baselineRange}>
              <Text style={styles.baselineText}>Baseline: 6k - 8k</Text>
            </View>
          </View>
          
          {/* Sleep Card */}
          <View style={styles.metricCard}>
            <View style={styles.cardHeader}>
              <Moon color={colors.star} size={20} />
              <Text style={styles.metricName}>Sleep</Text>
            </View>
            <Text style={styles.metricValue}>5.2<Text style={styles.unit}> hrs</Text></Text>
            <View style={styles.chartMock}>
              <View style={styles.barWarning} />
              <View style={[styles.barWarning, { height: 40 }]} />
              <View style={[styles.barWarning, { height: 30 }]} />
              <View style={[styles.barWarning, { height: 20 }]} />
            </View>
            <View style={styles.baselineRange}>
              <Text style={styles.baselineText}>Baseline: 7.2±1</Text>
            </View>
          </View>

          {/* SpO2 Card */}
          <View style={styles.metricCard}>
            <View style={styles.cardHeader}>
              <Droplets color={colors.success} size={20} />
              <Text style={styles.metricName}>SpO2</Text>
            </View>
            <Text style={styles.metricValue}>96<Text style={styles.unit}> %</Text></Text>
            <View style={styles.chartMock}>
              <View style={[styles.barSuccess, { height: 45 }]} />
              <View style={[styles.barSuccess, { height: 45 }]} />
              <View style={[styles.barSuccess, { height: 40 }]} />
              <View style={[styles.barSuccess, { height: 40 }]} />
            </View>
            <View style={styles.baselineRange}>
              <Text style={styles.baselineText}>Baseline: 96-100%</Text>
            </View>
          </View>
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: colors.appBg },
  container: { padding: spacing.m, paddingBottom: 100 },
  header: { marginBottom: spacing.l, marginTop: spacing.s },
  title: { fontSize: 24, fontWeight: '700', color: colors.mainColor },
  connectionCard: {
    backgroundColor: colors.surfaceBg,
    borderRadius: rounded.xl,
    padding: spacing.m,
    marginBottom: spacing.m,
  },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  deviceTitle: { fontSize: 16, fontWeight: '700', color: colors.mainColor },
  syncStatus: { fontSize: 13, color: colors.secondaryColor, marginTop: 4 },
  batteryBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.appBg,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  batteryText: { fontSize: 13, fontWeight: '600', color: colors.success, marginLeft: 4 },
  alertBanner: {
    flexDirection: 'row',
    backgroundColor: '#fef2f2',
    borderColor: '#fecaca',
    borderWidth: 1,
    borderRadius: rounded.l,
    padding: spacing.m,
    marginBottom: spacing.l,
    alignItems: 'center',
  },
  alertContent: { marginLeft: spacing.m, flex: 1 },
  alertTitle: { fontSize: 15, fontWeight: '700', color: colors.danger },
  alertDesc: { fontSize: 13, color: '#991b1b', marginTop: 2 },
  metricsGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
  metricCard: {
    width: '48%',
    backgroundColor: colors.surfaceBg,
    borderRadius: rounded.xl,
    padding: spacing.m,
    marginBottom: spacing.m,
  },
  cardHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: spacing.s },
  metricName: { fontSize: 14, fontWeight: '600', color: colors.secondaryColor, marginLeft: spacing.s },
  metricValue: { fontSize: 28, fontWeight: '700', color: colors.mainColor },
  unit: { fontSize: 14, fontWeight: '500', color: colors.secondaryColor },
  chartMock: {
    height: 60,
    flexDirection: 'row',
    alignItems: 'flex-end',
    justifyContent: 'space-around',
    marginTop: spacing.m,
    marginBottom: spacing.s,
    backgroundColor: colors.appBg,
    borderRadius: rounded.m,
    padding: spacing.xs,
  },
  barDanger: { width: 12, height: 15, backgroundColor: colors.danger, borderRadius: 3 },
  barInfo: { width: 12, height: 45, backgroundColor: colors.info, borderRadius: 3 },
  barWarning: { width: 12, height: 50, backgroundColor: colors.star, borderRadius: 3 },
  barSuccess: { width: 12, height: 45, backgroundColor: colors.success, borderRadius: 3 },
  baselineRange: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.appBg,
    paddingVertical: 4,
    borderRadius: rounded.s,
  },
  baselineText: { fontSize: 11, color: colors.secondaryColor, fontWeight: '600' }
});
