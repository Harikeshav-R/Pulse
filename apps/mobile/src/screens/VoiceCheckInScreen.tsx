import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, SafeAreaView, TouchableOpacity, Animated } from 'react-native';
import { X, Mic, MicOff, Volume2 } from 'lucide-react-native';
import { colors, spacing, rounded } from '../theme';
import { useNavigation } from '@react-navigation/native';

export default function VoiceCheckInScreen() {
  const navigation = useNavigation<any>();
  const [isMuted, setIsMuted] = useState(false);
  const [pulseAnim] = useState(new Animated.Value(1));

  // Auto pulse animation to simulate agent speaking/listening
  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.2,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, [pulseAnim]);

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        
        {/* Header Options */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.iconBtn}>
            <X color={colors.surfaceBg} size={28} />
          </TouchableOpacity>
        </View>

        {/* Central Avatar */}
        <View style={styles.centerStage}>
          <Text style={styles.statusText}>Agent is listening...</Text>
          <Animated.View style={[styles.avatarRing, { transform: [{ scale: pulseAnim }] }]}>
            <View style={styles.avatarInner}>
              <Volume2 color={colors.surfaceBg} size={48} />
            </View>
          </Animated.View>
        </View>

        {/* Live Transcript area */}
        <View style={styles.transcriptArea}>
          <Text style={styles.speakerAi}>TrialPulse AI:</Text>
          <Text style={styles.transcriptAi}>Hi David, how are you feeling today?</Text>
          
          <Text style={styles.speakerPatient}>You (Speaking...)</Text>
          <Text style={styles.transcriptPatient}>Not feeling great, I've had some nausea...</Text>
        </View>

        {/* Bottom Controls */}
        <View style={styles.controls}>
          <TouchableOpacity 
            style={[styles.micBtn, isMuted && styles.micBtnMuted]} 
            onPress={() => setIsMuted(!isMuted)}
          >
            {isMuted ? (
              <MicOff color={colors.surfaceBg} size={32} />
            ) : (
              <Mic color={colors.surfaceBg} size={32} />
            )}
          </TouchableOpacity>
          <Text style={styles.muteText}>{isMuted ? 'Muted' : 'Mute'}</Text>

          <TouchableOpacity 
            style={styles.endCallBtn} 
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.endCallText}>End Check-in</Text>
          </TouchableOpacity>
        </View>

      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: colors.mainColor }, // Dark background for voice
  container: { flex: 1, padding: spacing.m },
  header: { alignItems: 'flex-end', paddingTop: spacing.s },
  iconBtn: { padding: spacing.xs },
  
  centerStage: { flex: 2, justifyContent: 'center', alignItems: 'center' },
  statusText: { color: colors.secondaryColor, fontSize: 16, marginBottom: spacing.xl },
  avatarRing: {
    width: 160,
    height: 160,
    borderRadius: 80,
    backgroundColor: 'rgba(37, 99, 235, 0.2)', // info + opacity
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarInner: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: colors.info,
    justifyContent: 'center',
    alignItems: 'center',
  },

  transcriptArea: { flex: 1, justifyContent: 'flex-end', marginBottom: spacing.xl },
  speakerAi: { color: colors.info, fontSize: 14, fontWeight: '700', marginBottom: 4 },
  transcriptAi: { color: colors.surfaceBg, fontSize: 18, marginBottom: spacing.l },
  speakerPatient: { color: colors.mutedBorder, fontSize: 14, fontWeight: '700', marginBottom: 4 },
  transcriptPatient: { color: colors.surfaceBg, fontSize: 22, fontWeight: '600' },

  controls: { alignItems: 'center', paddingBottom: spacing.xl },
  micBtn: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  micBtnMuted: { backgroundColor: colors.danger, borderColor: colors.danger },
  muteText: { color: colors.surfaceBg, marginTop: spacing.s, fontSize: 14 },
  
  endCallBtn: {
    marginTop: spacing.xl,
    backgroundColor: colors.danger,
    paddingVertical: 14,
    paddingHorizontal: 32,
    borderRadius: rounded.xl,
  },
  endCallText: { color: colors.surfaceBg, fontSize: 16, fontWeight: '700' },
});
