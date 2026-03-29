import React, { useRef, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { colors, spacing } from '../theme';
import type { TranscriptEntry } from '../stores/voice.store';

interface Props {
  entries: TranscriptEntry[];
}

export default function LiveTranscript({ entries }: Props) {
  const scrollRef = useRef<ScrollView>(null);

  useEffect(() => {
    // Auto-scroll to bottom when new entries arrive
    if (entries.length > 0) {
      setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 100);
    }
  }, [entries.length]);

  if (entries.length === 0) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>Conversation will appear here...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      ref={scrollRef}
      style={styles.scrollView}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      {entries.map((entry) => (
        <View key={entry.id} style={styles.entry}>
          <Text style={entry.role === 'ai' ? styles.speakerAi : styles.speakerPatient}>
            {entry.role === 'ai' ? 'TrialPulse AI' : 'You'}
          </Text>
          <Text style={entry.role === 'ai' ? styles.textAi : styles.textPatient}>
            {entry.text}
          </Text>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scrollView: {
    flex: 1,
  },
  content: {
    paddingVertical: spacing.s,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    color: '#6b7280',
    fontSize: 15,
    fontStyle: 'italic',
  },
  entry: {
    marginBottom: spacing.m,
  },
  speakerAi: {
    color: colors.info,
    fontSize: 13,
    fontWeight: '700',
    marginBottom: 2,
  },
  speakerPatient: {
    color: colors.mutedBorder,
    fontSize: 13,
    fontWeight: '700',
    marginBottom: 2,
  },
  textAi: {
    color: colors.surfaceBg,
    fontSize: 16,
    lineHeight: 22,
  },
  textPatient: {
    color: colors.surfaceBg,
    fontSize: 18,
    fontWeight: '600',
    lineHeight: 24,
  },
});
