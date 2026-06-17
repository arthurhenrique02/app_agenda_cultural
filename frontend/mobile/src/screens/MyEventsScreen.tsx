import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator, TouchableOpacity, RefreshControl, Alert } from 'react-native';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import * as api from '../services/api';
import { EventResponse, CategoryResponse } from '../types/api';
import { RootStackParamList } from '../navigation';
import { useAuth } from '../contexts/AuthContext';

type NavigationProp = StackNavigationProp<RootStackParamList, 'MainTabs'>;

export default function MyEventsScreen() {
  const [events, setEvents] = useState<EventResponse[]>([]);
  const [categories, setCategories] = useState<CategoryResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  const navigation = useNavigation<NavigationProp>();
  const { logout } = useAuth();

  useFocusEffect(
    useCallback(() => {
      setPage(1);
      loadData(1, true);
    }, [])
  );

  async function loadData(pageNumber: number, reset: boolean = false) {
    if (pageNumber === 1) {
      if (!reset) setLoading(true);
    } else {
      setLoadingMore(true);
    }

    try {
      const [res, catsData] = await Promise.all([
        api.getMyEvents(pageNumber),
        api.listCategories()
      ]);
      
      if (reset || pageNumber === 1) {
        setEvents(res.items);
      } else {
        setEvents(prev => [...prev, ...res.items]);
      }
      
      setCategories(catsData);
      setTotalPages(res.pages);
      setPage(pageNumber);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
      setRefreshing(false);
      setLoadingMore(false);
    }
  }

  const onRefresh = () => {
    setRefreshing(true);
    loadData(1, true);
  };

  const loadMore = () => {
    if (!loadingMore && page < totalPages) {
      loadData(page + 1);
    }
  };

  async function handleDelete(id: number) {
    Alert.alert(
      'Confirmar Exclusão',
      'Tem certeza que deseja excluir este evento?',
      [
        { text: 'Cancelar', style: 'cancel' },
        { 
          text: 'Excluir', 
          style: 'destructive',
          onPress: async () => {
            try {
              await api.deleteEvent(id);
              setEvents(events.filter(e => e.id !== id));
            } catch (error) {
              Alert.alert('Erro', 'Não foi possível excluir o evento.');
            }
          }
        }
      ]
    );
  }

  const getStatusStyle = (status: string) => {
    switch (status) {
      case 'aprovado': return { color: '#28a745', bg: '#d4edda' };
      case 'pendente': return { color: '#856404', bg: '#fff3cd' };
      case 'rejeitado': return { color: '#dc3545', bg: '#f8d7da' };
      case 'cancelado': return { color: '#6c757d', bg: '#e2e3e5' };
      default: return { color: '#333', bg: '#eee' };
    }
  };

  const getCategoryName = (id: number) => categories.find(c => c.id === id)?.name || 'Evento';

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Meus Eventos</Text>
        <TouchableOpacity onPress={logout}>
          <Text style={styles.logoutText}>Sair</Text>
        </TouchableOpacity>
      </View>

      {loading ? (
        <ActivityIndicator size="large" color="#007bff" style={{ marginTop: 50 }} />
      ) : (
        <FlatList
          data={events}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.list}
          onEndReached={loadMore}
          onEndReachedThreshold={0.5}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          renderItem={({ item }) => {
            const status = getStatusStyle(item.status);
            return (
              <View style={styles.card}>
                <View style={styles.cardHeader}>
                  <Text style={styles.eventTitle}>{item.title}</Text>
                  <View style={[styles.badge, { backgroundColor: status.bg }]}>
                    <Text style={[styles.badgeText, { color: status.color }]}>
                      {item.status.toUpperCase()}
                    </Text>
                  </View>
                </View>
                
                <Text style={styles.eventDate}>
                  {new Date(item.date).toLocaleDateString('pt-BR')} • {getCategoryName(item.category_id)}
                </Text>

                {item.status === 'rejeitado' && item.rejection_reason && (
                  <View style={styles.rejectionBox}>
                    <Text style={styles.rejectionLabel}>Motivo da Rejeição:</Text>
                    <Text style={styles.rejectionText}>{item.rejection_reason}</Text>
                  </View>
                )}

                <View style={styles.actions}>
                  <TouchableOpacity 
                    style={styles.editButton}
                    onPress={() => navigation.navigate('EditEvent' as any, { id: item.id })}
                  >
                    <Text style={styles.actionText}>Editar</Text>
                  </TouchableOpacity>
                  <TouchableOpacity 
                    style={styles.deleteButton}
                    onPress={() => handleDelete(item.id)}
                  >
                    <Text style={styles.deleteText}>Excluir</Text>
                  </TouchableOpacity>
                </View>
              </View>
            );
          }}
          ListEmptyComponent={
            <View style={styles.empty}>
              <Text style={styles.emptyText}>Você ainda não criou nenhum evento.</Text>
              <TouchableOpacity 
                style={styles.createBtn}
                onPress={() => navigation.navigate('CreateEvent' as any)}
              >
                <Text style={styles.createBtnText}>Criar meu primeiro evento</Text>
              </TouchableOpacity>
            </View>
          }
          ListFooterComponent={
            loadingMore ? (
              <ActivityIndicator style={{ marginVertical: 20 }} color="#007bff" />
            ) : null
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  logoutText: {
    color: '#dc3545',
    fontWeight: 'bold',
  },
  list: {
    padding: 15,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 5,
  },
  eventTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    flex: 1,
    marginRight: 10,
  },
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  badgeText: {
    fontSize: 10,
    fontWeight: 'bold',
  },
  eventDate: {
    color: '#666',
    fontSize: 14,
    marginBottom: 10,
  },
  rejectionBox: {
    backgroundColor: '#fff5f5',
    padding: 10,
    borderRadius: 6,
    borderLeftWidth: 3,
    borderLeftColor: '#dc3545',
    marginBottom: 15,
  },
  rejectionLabel: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#dc3545',
    marginBottom: 2,
  },
  rejectionText: {
    fontSize: 13,
    color: '#333',
  },
  actions: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#eee',
    paddingTop: 10,
    gap: 15,
  },
  editButton: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 8,
    backgroundColor: '#007bff',
    borderRadius: 4,
  },
  deleteButton: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: '#dc3545',
    borderRadius: 4,
  },
  actionText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  deleteText: {
    color: '#dc3545',
    fontWeight: 'bold',
  },
  empty: {
    marginTop: 100,
    alignItems: 'center',
  },
  emptyText: {
    color: '#666',
    marginBottom: 20,
  },
  createBtn: {
    backgroundColor: '#007bff',
    padding: 15,
    borderRadius: 8,
  },
  createBtnText: {
    color: '#fff',
    fontWeight: 'bold',
  },
});
