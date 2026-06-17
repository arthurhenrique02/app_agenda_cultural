import React, { useEffect, useState } from 'react';
import { View, Text, Image, ScrollView, StyleSheet, ActivityIndicator, TouchableOpacity, Share } from 'react-native';
import { useRoute, RouteProp } from '@react-navigation/native';
import * as api from '../services/api';
import { EventResponse, CategoryResponse } from '../types/api';
import { RootStackParamList } from '../navigation';

type RouteProps = RouteProp<RootStackParamList, 'EventDetail'>;

export default function EventDetailScreen() {
  const route = useRoute<RouteProps>();
  const { id } = route.params;
  
  const [event, setEvent] = useState<EventResponse | null>(null);
  const [categories, setCategories] = useState<CategoryResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [id]);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const [eventData, categoriesData] = await Promise.all([
        api.getEvent(id),
        api.listCategories()
      ]);
      setEvent(eventData);
      setCategories(categoriesData);
    } catch (err) {
      setError('Não foi possível carregar os detalhes do evento.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleShare = async () => {
    if (!event) return;
    try {
      await Share.share({
        message: `Confira este evento: ${event.title}\nData: ${new Date(event.date).toLocaleDateString('pt-BR')}\nLocal: ${event.venue_name}\n\nVia Agenda Cultural`,
      });
    } catch (error) {
      console.error(error);
    }
  };

  const getCategoryName = (catId: number) => {
    return categories.find(c => c.id === catId)?.name || 'Evento';
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#007bff" />
      </View>
    );
  }

  if (error || !event) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>{error || 'Evento não encontrado.'}</Text>
      </View>
    );
  }

  const formattedDate = new Date(event.date).toLocaleDateString('pt-BR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      {event.image_url ? (
        <Image source={{ uri: event.image_url }} style={styles.image} resizeMode="cover" />
      ) : (
        <View style={styles.imagePlaceholder}>
          <Text style={{ color: '#999' }}>Sem Imagem</Text>
        </View>
      )}

      <View style={styles.content}>
        <Text style={styles.category}>{getCategoryName(event.category_id).toUpperCase()}</Text>
        <Text style={styles.title}>{event.title}</Text>
        
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Data e Hora</Text>
          <Text style={styles.infoValue}>{formattedDate}</Text>
          <Text style={styles.infoValue}>Início: {event.start_time}{event.end_time ? ` • Fim: ${event.end_time}` : ''}</Text>
        </View>

        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Localização</Text>
          <Text style={styles.infoValue}>{event.venue_name}</Text>
          <Text style={styles.infoValue}>{event.address}</Text>
          <Text style={styles.infoValue}>{event.neighborhood}, {event.city}</Text>
        </View>

        <View style={styles.descriptionContainer}>
          <Text style={styles.infoLabel}>Descrição</Text>
          <Text style={styles.description}>{event.description}</Text>
        </View>

        <TouchableOpacity style={styles.shareButton} onPress={handleShare}>
          <Text style={styles.shareButtonText}>Compartilhar Evento</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  contentContainer: {
    paddingBottom: 40,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  image: {
    width: '100%',
    height: 250,
  },
  imagePlaceholder: {
    width: '100%',
    height: 250,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    padding: 20,
  },
  category: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#007bff',
    marginBottom: 8,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
  },
  infoRow: {
    marginBottom: 20,
  },
  infoLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#999',
    marginBottom: 4,
    textTransform: 'uppercase',
  },
  infoValue: {
    fontSize: 16,
    color: '#444',
    marginBottom: 2,
  },
  descriptionContainer: {
    marginBottom: 30,
  },
  description: {
    fontSize: 16,
    lineHeight: 24,
    color: '#555',
  },
  shareButton: {
    backgroundColor: '#007bff',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  shareButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  errorText: {
    fontSize: 16,
    color: '#dc3545',
    textAlign: 'center',
  },
});
