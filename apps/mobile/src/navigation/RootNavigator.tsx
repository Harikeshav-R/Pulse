import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { NavigationContainer } from '@react-navigation/native';
import { Home, ListOrdered, Activity, UserCircle } from 'lucide-react-native';
import { colors } from '../theme';

import HomeScreen from '../screens/HomeScreen';
import TimelineScreen from '../screens/TimelineScreen';
import WearableScreen from '../screens/WearableScreen';
import ProfileScreen from '../screens/ProfileScreen';
import ChatScreen from '../screens/ChatScreen';
import VoiceCheckInScreen from '../screens/VoiceCheckInScreen';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.mainColor,
        tabBarInactiveTintColor: colors.lightFont,
        tabBarStyle: {
          backgroundColor: colors.surfaceBg,
          borderTopColor: colors.messageBoxBorder,
        },
      }}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen} 
        options={{
          tabBarIcon: ({ color, size }) => <Home color={color} size={size} />
        }}
      />
      <Tab.Screen 
        name="Timeline" 
        component={TimelineScreen}
        options={{
          tabBarIcon: ({ color, size }) => <ListOrdered color={color} size={size} />
        }}
      />
      <Tab.Screen 
        name="Wearables" 
        component={WearableScreen}
        options={{
          tabBarIcon: ({ color, size }) => <Activity color={color} size={size} />
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          tabBarIcon: ({ color, size }) => <UserCircle color={color} size={size} />
        }}
      />
    </Tab.Navigator>
  );
}

export default function RootNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="MainTabs" component={MainTabs} />
        {/* Modals / Full screens */}
        <Stack.Screen 
          name="Chat" 
          component={ChatScreen} 
          options={{ presentation: 'card' }}
        />
        <Stack.Screen 
          name="Voice" 
          component={VoiceCheckInScreen} 
          options={{ presentation: 'fullScreenModal', animation: 'slide_from_bottom' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
