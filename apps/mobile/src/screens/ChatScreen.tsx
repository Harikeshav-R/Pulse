import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, SafeAreaView, TextInput, TouchableOpacity, ScrollView, Platform, KeyboardAvoidingView, ActivityIndicator } from 'react-native';
import { ArrowLeft, Send, Mic, User } from 'lucide-react-native';
import { colors, spacing, rounded } from '../theme';
import { useNavigation } from '@react-navigation/native';
import { useCheckinStore } from '../stores/checkin.store';

export default function ChatScreen() {
  const navigation = useNavigation<any>();
  const [inputText, setInputText] = useState('');
  
  const { messages, isLoading, error, startCheckin, sendMessage, sessionId } = useCheckinStore();

  useEffect(() => {
    // Only start a new check-in if one isn't active
    if (!sessionId) {
      startCheckin();
    }
  }, [sessionId, startCheckin]);

  const handleSend = () => {
    if (inputText.trim() && !isLoading) {
      sendMessage(inputText.trim());
      setInputText('');
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView 
        style={styles.container} 
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
            <ArrowLeft color={colors.mainColor} size={24} />
          </TouchableOpacity>
          <View style={styles.headerTitleContainer}>
            <Text style={styles.title}>Daily Check-In</Text>
            <Text style={styles.subtitle}>TrialPulse AI</Text>
          </View>
          <View style={{ width: 40 }} />
        </View>

        <ScrollView contentContainerStyle={styles.chatArea} style={styles.scrollArea}>
          {messages.map((msg) => {
            const isPatient = msg.role === 'patient';
            return (
              <View key={msg.id} style={[styles.messageRow, isPatient ? styles.messageRowRight : styles.messageRowLeft]}>
                {!isPatient && (
                  <View style={styles.aiAvatar}>
                    <Text style={styles.aiInitial}>T</Text>
                  </View>
                )}
                <View style={[styles.bubble, isPatient ? styles.bubblePatient : styles.bubbleAi]}>
                  <Text style={[styles.messageText, isPatient ? styles.textPatient : styles.textAi]}>
                    {msg.text}
                  </Text>
                </View>
                {isPatient && <User style={{ marginLeft: 8 }} color={colors.secondaryColor} size={20} />}
              </View>
            );
          })}
          {isLoading && (
            <View style={[styles.messageRow, styles.messageRowLeft]}>
              <View style={styles.aiAvatar}>
                <Text style={styles.aiInitial}>T</Text>
              </View>
              <View style={[styles.bubble, styles.bubbleAi, { paddingVertical: spacing.s }]}>
                <ActivityIndicator size="small" color={colors.mainColor} />
              </View>
            </View>
          )}
        </ScrollView>

        <View style={styles.inputArea}>
          <TouchableOpacity style={styles.voiceBtn} onPress={() => navigation.navigate('Voice')}>
            <Mic color={colors.secondaryColor} size={24} />
          </TouchableOpacity>
          <TextInput
            style={styles.input}
            placeholder="Type your reply..."
            placeholderTextColor={colors.lightFont}
            value={inputText}
            onChangeText={setInputText}
            multiline
          />
          <TouchableOpacity style={styles.sendBtn} onPress={handleSend}>
            <Send color={colors.surfaceBg} size={18} />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: colors.appBg },
  container: { flex: 1 },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.m,
    backgroundColor: colors.surfaceBg,
    borderBottomWidth: 1,
    borderBottomColor: colors.messageBoxBorder,
  },
  backBtn: { padding: spacing.xs },
  headerTitleContainer: { flex: 1, alignItems: 'center' },
  title: { fontSize: 18, fontWeight: '700', color: colors.mainColor },
  subtitle: { fontSize: 13, color: colors.info, marginTop: 2, fontWeight: '500' },
  scrollArea: { flex: 1 },
  chatArea: { padding: spacing.m, paddingBottom: spacing.xl },
  messageRow: { flexDirection: 'row', marginBottom: spacing.m, alignItems: 'flex-end' },
  messageRowLeft: { justifyContent: 'flex-start' },
  messageRowRight: { justifyContent: 'flex-end' },
  aiAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.info,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  aiInitial: { color: colors.surfaceBg, fontWeight: '700', fontSize: 16 },
  bubble: {
    maxWidth: '75%',
    padding: spacing.m,
    borderRadius: rounded.l,
  },
  bubbleAi: {
    backgroundColor: colors.surfaceBg,
    borderBottomLeftRadius: 4,
  },
  bubblePatient: {
    backgroundColor: colors.mainColor,
    borderBottomRightRadius: 4,
  },
  messageText: { fontSize: 16, lineHeight: 22 },
  textAi: { color: colors.mainColor },
  textPatient: { color: colors.surfaceBg },
  inputArea: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.m,
    backgroundColor: colors.surfaceBg,
    borderTopWidth: 1,
    borderTopColor: colors.messageBoxBorder,
  },
  voiceBtn: { padding: spacing.s, marginRight: spacing.xs },
  input: {
    flex: 1,
    backgroundColor: colors.appBg,
    borderRadius: rounded.xl,
    paddingHorizontal: spacing.m,
    paddingTop: 12,
    paddingBottom: 12,
    minHeight: 44,
    maxHeight: 120,
    fontSize: 16,
    color: colors.mainColor,
  },
  sendBtn: {
    backgroundColor: colors.info,
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: spacing.s,
  },
});
