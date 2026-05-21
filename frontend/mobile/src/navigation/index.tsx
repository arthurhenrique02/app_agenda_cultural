import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useAuth } from '../contexts/AuthContext';

import HomeScreen from '../screens/HomeScreen';
import EventDetailScreen from '../screens/EventDetailScreen';
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import CreateEventScreen from '../screens/CreateEventScreen';
import MyEventsScreen from '../screens/MyEventsScreen';
import EditEventScreen from '../screens/EditEventScreen';

export type RootStackParamList = {
  Home: undefined;
  EventDetail: { id: number };
  Login: undefined;
  Register: undefined;
  MainTabs: undefined;
  EditEvent: { id: number };
};

export type MainTabParamList = {
  HomeTab: undefined;
  MyEvents: undefined;
  CreateEvent: undefined;
};

const Stack = createStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();

function MainTabs() {
  return (
    <Tab.Navigator>
      <Tab.Screen name="HomeTab" component={HomeScreen} options={{ title: 'Explorar' }} />
      <Tab.Screen name="MyEvents" component={MyEventsScreen} options={{ title: 'Meus Eventos' }} />
      <Tab.Screen name="CreateEvent" component={CreateEventScreen} options={{ title: 'Criar' }} />
    </Tab.Navigator>
  );
}

export default function Navigation() {
  const { user, loading } = useAuth();

  if (loading) {
    return null; // Or a splash screen
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {user ? (
          <>
            <Stack.Screen name="MainTabs" component={MainTabs} />
            <Stack.Screen name="EventDetail" component={EventDetailScreen} options={{ headerShown: true, title: 'Evento' }} />
            <Stack.Screen name="EditEvent" component={EditEventScreen as any} options={{ headerShown: true, title: 'Editar Evento' }} />
          </>
        ) : (
          <>
            <Stack.Screen name="Home" component={HomeScreen} />
            <Stack.Screen name="EventDetail" component={EventDetailScreen} options={{ headerShown: true, title: 'Evento' }} />
            <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: true, title: 'Entrar' }} />
            <Stack.Screen name="Register" component={RegisterScreen} options={{ headerShown: true, title: 'Cadastrar' }} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
