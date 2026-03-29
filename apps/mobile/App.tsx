import React, { useEffect } from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import RootNavigator from './src/navigation/RootNavigator';
import { useAuthStore } from './src/stores/auth.store';

export default function App() {
  const loginDemoPatient = useAuthStore((state) => state.loginDemoPatient);

  useEffect(() => {
    // Automatically log in the demo patient on app start
    loginDemoPatient();
  }, [loginDemoPatient]);

  return (
    <SafeAreaProvider>
      <RootNavigator />
      <StatusBar style="auto" />
    </SafeAreaProvider>
  );
}
