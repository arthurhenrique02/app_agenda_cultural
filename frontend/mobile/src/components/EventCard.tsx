import React from 'react';
import { View, Text, Image, StyleSheet, TouchableOpacity } from 'react-native';
import { EventResponse } from '../types/api';

interface EventCardProps {
  event: EventResponse;
  onPress: () => void;
  categoryName: string;
}

export default function EventCard({ event, onPress, categoryName }: EventCardProps) {
  const formattedDate = new Date(event.date).toLocaleDateString('pt-BR');

  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.7}>
      {event.image_url ? (
        <Image source={{ uri: event.image_url }} style={styles.image} />
      ) : (
        <View style={[styles.image, styles.placeholder]}>
          <Text style={styles.placeholderText}>Sem Imagem</Text>
        </View>
      )}
      
      <View style={styles.content}>
        <Text style={styles.category}>{categoryName.toUpperCase()}</Text>
        <Text style={styles.title} numberOfLines={2}>{event.title}</Text>
        
        <View style={styles.footer}>
          <Text style={styles.info}>{formattedDate} • {event.start_time}</Text>
          <Text style={styles.venue} numberOfLines={1}>{event.venue_name}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 16,
    overflow: 'hidden',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  image: {
    width: '100%',
    height: 180,
  },
  placeholder: {
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
    justifyContent: 'center',
  },
  placeholderText: {
    color: '#999',
  },
  content: {
    padding: 12,
  },
  category: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#007bff',
    marginBottom: 4,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  footer: {
    marginTop: 4,
  },
  info: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  venue: {
    fontSize: 12,
    color: '#888',
    fontStyle: 'italic',
  },
});
