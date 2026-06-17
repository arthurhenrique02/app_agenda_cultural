import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ActivityIndicator, Alert, Text } from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import * as api from '../services/api';
import EventForm from '../components/EventForm';
import { RootStackParamList } from '../navigation';
import { EventResponse } from '../types/api';

type RouteProps = RouteProp<RootStackParamList, 'EditEvent'>;

export default function EditEventScreen() {
  const route = useRoute<RouteProps>();
  const { id } = route.params;
  const navigation = useNavigation();
  const [event, setEvent] = useState<EventResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getEvent(id).then(setEvent).finally(() => setLoading(false));
  }, [id]);

  async function handleSubmit(data: any) {
    if (event?.status === 'aprovado') {
      const confirm = await new Promise((resolve) => {
        Alert.alert(
          'Aviso de Moderação',
          'Este evento já está aprovado. Ao editá-lo, ele voltará para a fila de moderação e ficará temporariamente invisível. Deseja continuar?',
          [
            { text: 'Cancelar', onPress: () => resolve(false), style: 'cancel' },
            { text: 'Sim, Editar', onPress: () => resolve(true) }
          ]
        );
      });
      if (!confirm) return;
    }

    await api.updateEvent(id, data);
    Alert.alert('Sucesso', 'Evento atualizado!');
    navigation.goBack();
  }

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#007bff" />
      </View>
    );
  }

  if (!event) return null;

  return (
    <View style={styles.container}>
      {event.status === 'aprovado' && (
        <View style={styles.warningBanner}>
          <Text style={styles.warningText}>
            Atenção: Este evento está aprovado. Edições exigirão nova moderação.
          </Text>
        </View>
      )}
      <EventForm 
        initialData={event} 
        onSubmit={handleSubmit} 
        submitLabel="Salvar Alterações" 
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  warningBanner: {
    backgroundColor: '#fff3cd',
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#ffeeba',
  },
  warningText: {
    color: '#856404',
    fontSize: 12,
    textAlign: 'center',
  },
});
