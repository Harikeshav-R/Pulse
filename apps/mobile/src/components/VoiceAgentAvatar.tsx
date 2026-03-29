import React, { useEffect, useRef } from 'react';
import { View, Text, Animated, StyleSheet, ActivityIndicator } from 'react-native';
import { Volume2, Mic } from 'lucide-react-native';
import { colors, spacing } from '../theme';
import type { AgentState } from '../stores/voice.store';

interface Props {
  agentState: AgentState;
}

const STATUS_LABELS: Record<AgentState, string> = {
  idle: 'Idle',
  connecting: 'Connecting...',
  listening: 'Listening...',
  speaking: 'Agent is speaking...',
};

export default function VoiceAgentAvatar({ agentState }: Props) {
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const animRef = useRef<Animated.CompositeAnimation | null>(null);

  useEffect(() => {
    if (animRef.current) {
      animRef.current.stop();
      animRef.current = null;
    }

    if (agentState === 'speaking') {
      const anim = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.15,
            duration: 600,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 600,
            useNativeDriver: true,
          }),
        ]),
      );
      animRef.current = anim;
      anim.start();
    } else if (agentState === 'listening') {
      const anim = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.05,
            duration: 1200,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 1200,
            useNativeDriver: true,
          }),
        ]),
      );
      animRef.current = anim;
      anim.start();
    } else {
      pulseAnim.setValue(1);
    }

    return () => {
      animRef.current?.stop();
    };
  }, [agentState, pulseAnim]);

  const ringColor =
    agentState === 'speaking'
      ? 'rgba(37, 99, 235, 0.3)'
      : agentState === 'listening'
        ? 'rgba(22, 163, 106, 0.2)'
        : 'rgba(107, 114, 128, 0.15)';

  const innerColor =
    agentState === 'speaking'
      ? colors.info
      : agentState === 'listening'
        ? colors.success
        : '#6b7280';

  return (
    <View style={styles.container}>
      <Text style={styles.statusText}>{STATUS_LABELS[agentState]}</Text>

      {agentState === 'connecting' ? (
        <View style={[styles.avatarRing, { backgroundColor: ringColor }]}>
          <View style={[styles.avatarInner, { backgroundColor: innerColor }]}>
            <ActivityIndicator size="large" color={colors.surfaceBg} />
          </View>
        </View>
      ) : (
        <Animated.View
          style={[
            styles.avatarRing,
            { backgroundColor: ringColor, transform: [{ scale: pulseAnim }] },
          ]}
        >
          <View style={[styles.avatarInner, { backgroundColor: innerColor }]}>
            {agentState === 'listening' ? (
              <Mic color={colors.surfaceBg} size={48} />
            ) : (
              <Volume2 color={colors.surfaceBg} size={48} />
            )}
          </View>
        </Animated.View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  statusText: {
    color: colors.secondaryColor,
    fontSize: 16,
    marginBottom: spacing.xl,
  },
  avatarRing: {
    width: 160,
    height: 160,
    borderRadius: 80,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarInner: {
    width: 120,
    height: 120,
    borderRadius: 60,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
