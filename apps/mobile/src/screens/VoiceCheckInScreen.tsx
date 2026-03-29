import React, { useEffect, useRef, useCallback } from 'react';
import { View, Text, StyleSheet, SafeAreaView, TouchableOpacity } from 'react-native';
import { X, Mic, MicOff } from 'lucide-react-native';
import { Room, RoomEvent, Track } from 'livekit-client';
import { AudioSession } from '@livekit/react-native';
import { colors, spacing, rounded } from '../theme';
import { useNavigation } from '@react-navigation/native';
import { useVoiceStore } from '../stores/voice.store';
import VoiceAgentAvatar from '../components/VoiceAgentAvatar';
import LiveTranscript from '../components/LiveTranscript';

export default function VoiceCheckInScreen() {
  const navigation = useNavigation<any>();
  const room = useRef<Room | null>(null);
  const {
    isConnected,
    isMuted,
    agentState,
    transcript,
    error,
    startSession,
    setConnected,
    setAgentState,
    toggleMute,
    addTranscriptEntry,
    endSession,
    setError,
  } = useVoiceStore();

  const handleEnd = useCallback(() => {
    room.current?.disconnect();
    endSession();
    navigation.goBack();
  }, [endSession, navigation]);

  const handleToggleMute = useCallback(() => {
    const localParticipant = room.current?.localParticipant;
    if (localParticipant) {
      localParticipant.setMicrophoneEnabled(isMuted); // isMuted is current state, so enable if muted
    }
    toggleMute();
  }, [isMuted, toggleMute]);

  useEffect(() => {
    let mounted = true;

    async function connect() {
      try {
        await AudioSession.startAudioSession();

        const session = await startSession();
        if (!mounted) return;

        const newRoom = new Room();
        room.current = newRoom;

        // Detect agent audio track (agent started speaking)
        newRoom.on(RoomEvent.TrackSubscribed, (track, _pub, participant) => {
          if (track.kind === Track.Kind.Audio && participant.identity === 'checkin-agent') {
            setAgentState('speaking');
          }
        });

        newRoom.on(RoomEvent.TrackUnsubscribed, (track, _pub, participant) => {
          if (track.kind === Track.Kind.Audio && participant.identity === 'checkin-agent') {
            setAgentState('listening');
          }
        });

        // Transcript data from agent via data channel
        newRoom.on(RoomEvent.DataReceived, (payload, participant) => {
          try {
            const data = JSON.parse(new TextDecoder().decode(payload));
            if (data.type === 'transcript' && data.text) {
              const role = participant?.identity === 'checkin-agent' ? 'ai' : 'patient';
              addTranscriptEntry(role as 'ai' | 'patient', data.text);
            }
          } catch {
            // Ignore non-JSON data
          }
        });

        // Track agent speaking state via active speaker changes
        newRoom.on(RoomEvent.ActiveSpeakersChanged, (speakers) => {
          const agentSpeaking = speakers.some((s) => s.identity === 'checkin-agent');
          setAgentState(agentSpeaking ? 'speaking' : 'listening');
        });

        newRoom.on(RoomEvent.Disconnected, () => {
          if (mounted) setConnected(false);
        });

        await newRoom.connect(session.livekitUrl, session.token);
        if (!mounted) {
          newRoom.disconnect();
          return;
        }

        await newRoom.localParticipant.setMicrophoneEnabled(true);
        setConnected(true);
      } catch (err: any) {
        if (mounted) {
          console.error('Voice connection error:', err);
          setError(err.message || 'Failed to connect to voice session');
        }
      }
    }

    connect();

    return () => {
      mounted = false;
      room.current?.disconnect();
      AudioSession.stopAudioSession();
      endSession();
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={handleEnd} style={styles.iconBtn}>
            <X color={colors.surfaceBg} size={28} />
          </TouchableOpacity>
        </View>

        {/* Central Avatar */}
        <View style={styles.centerStage}>
          <VoiceAgentAvatar agentState={agentState} />
        </View>

        {/* Error display */}
        {error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        {/* Live Transcript */}
        <View style={styles.transcriptArea}>
          <LiveTranscript entries={transcript} />
        </View>

        {/* Bottom Controls */}
        <View style={styles.controls}>
          <TouchableOpacity
            style={[styles.micBtn, isMuted && styles.micBtnMuted]}
            onPress={handleToggleMute}
            disabled={!isConnected}
          >
            {isMuted ? (
              <MicOff color={colors.surfaceBg} size={32} />
            ) : (
              <Mic color={colors.surfaceBg} size={32} />
            )}
          </TouchableOpacity>
          <Text style={styles.muteText}>{isMuted ? 'Unmute' : 'Mute'}</Text>

          <TouchableOpacity style={styles.endCallBtn} onPress={handleEnd}>
            <Text style={styles.endCallText}>End Check-in</Text>
          </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: colors.mainColor },
  container: { flex: 1, padding: spacing.m },
  header: { alignItems: 'flex-end', paddingTop: spacing.s },
  iconBtn: { padding: spacing.xs },

  centerStage: { flex: 2, justifyContent: 'center', alignItems: 'center' },

  errorContainer: {
    backgroundColor: 'rgba(225, 29, 72, 0.15)',
    padding: spacing.m,
    borderRadius: rounded.m,
    marginBottom: spacing.m,
  },
  errorText: { color: colors.danger, fontSize: 14, textAlign: 'center' },

  transcriptArea: { flex: 1, marginBottom: spacing.m },

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
