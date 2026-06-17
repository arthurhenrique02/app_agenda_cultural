import React from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import * as api from '../services/api';
import EventForm from '../components/EventForm';

export default function CreateEventScreen() {
  const navigation = useNavigation();

  async function handleSubmit(data: any) {
    await api.createEvent(data);
    Alert.alert('Sucesso', 'Evento enviado para moderação!');
    navigation.goBack();
  }

  return (
    <View style={styles.container}>
      <EventForm onSubmit={handleSubmit} submitLabel="Criar Evento" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
});
