import React from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView, TouchableOpacity } from 'react-native';
import { Settings, Bell, ChevronRight, UserCircle, LogOut } from 'lucide-react-native';
import { colors, spacing, rounded } from '../theme';

export default function ProfileScreen() {
  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>Profile & Settings</Text>
        </View>

        <View style={styles.profileCard}>
          <UserCircle size={60} color={colors.mainColor} />
          <Text style={styles.name}>David Thompson</Text>
          <Text style={styles.subjectId}>Subject ID: 001-0042</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Trial Information</Text>
          <View style={styles.card}>
            <View style={styles.row}>
              <Text style={styles.label}>Trial</Text>
              <Text style={styles.value}>ONCO-2026-TP1</Text>
            </View>
            <View style={styles.divider} />
            <View style={styles.row}>
              <Text style={styles.label}>Site Name</Text>
              <Text style={styles.value}>Memorial City Cancer Center</Text>
            </View>
            <View style={styles.divider} />
            <View style={styles.row}>
              <Text style={styles.label}>Enrolled</Text>
              <Text style={styles.value}>Feb 15, 2026</Text>
            </View>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Preferences</Text>
          <View style={styles.card}>
            <TouchableOpacity style={styles.rowClickable}>
              <View style={styles.iconRow}>
                <Bell size={20} color={colors.secondaryColor} />
                <Text style={styles.labelIcon}>Notifications</Text>
              </View>
              <ChevronRight size={20} color={colors.mutedBorder} />
            </TouchableOpacity>
            <View style={styles.divider} />
            <TouchableOpacity style={styles.rowClickable}>
              <View style={styles.iconRow}>
                <Settings size={20} color={colors.secondaryColor} />
                <Text style={styles.labelIcon}>App Settings</Text>
              </View>
              <ChevronRight size={20} color={colors.mutedBorder} />
            </TouchableOpacity>
          </View>
        </View>

        <TouchableOpacity style={styles.logoutBtn}>
          <LogOut size={20} color={colors.danger} />
          <Text style={styles.logoutText}>Log Out</Text>
        </TouchableOpacity>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: colors.appBg },
  container: { padding: spacing.m },
  header: { marginBottom: spacing.l, marginTop: spacing.s },
  title: { fontSize: 24, fontWeight: '700', color: colors.mainColor },
  profileCard: {
    backgroundColor: colors.surfaceBg,
    padding: spacing.xl,
    borderRadius: rounded.xl,
    alignItems: 'center',
    marginBottom: spacing.l,
  },
  name: { fontSize: 22, fontWeight: '700', color: colors.mainColor, marginTop: spacing.m },
  subjectId: { fontSize: 14, color: colors.secondaryColor, marginTop: 4 },
  section: { marginBottom: spacing.l },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: colors.mainColor, marginBottom: spacing.s, marginLeft: spacing.xs },
  card: { backgroundColor: colors.surfaceBg, borderRadius: rounded.xl, paddingVertical: spacing.s, paddingHorizontal: spacing.m },
  row: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: spacing.m },
  rowClickable: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: spacing.m },
  label: { fontSize: 15, color: colors.secondaryColor },
  value: { fontSize: 15, fontWeight: '600', color: colors.mainColor },
  divider: { height: 1, backgroundColor: colors.messageBoxBorder },
  iconRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.s },
  labelIcon: { fontSize: 15, color: colors.mainColor, fontWeight: '500' },
  logoutBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.m,
    gap: spacing.s,
    backgroundColor: '#fef2f2',
    borderRadius: rounded.l,
    marginTop: spacing.m,
  },
  logoutText: { color: colors.danger, fontSize: 16, fontWeight: '600' }
});
