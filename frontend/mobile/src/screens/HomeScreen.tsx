import React, { useEffect, useState, useCallback } from 'react';
import { View, FlatList, StyleSheet, ActivityIndicator, Text, RefreshControl } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import * as api from '../services/api';
import { EventResponse, CategoryResponse, PaginatedResponse } from '../types/api';
import EventCard from '../components/EventCard';
import FilterBar from '../components/FilterBar';
import { RootStackParamList } from '../navigation';

type NavigationProp = StackNavigationProp<RootStackParamList, 'Home'>;

export default function HomeScreen() {
  const navigation = useNavigation<NavigationProp>();
  const [events, setEvents] = useState<EventResponse[]>([]);
  const [categories, setCategories] = useState<CategoryResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setPage(1);
      loadEvents(1, true);
    }, 500);
    return () => clearTimeout(timer);
  }, [searchQuery, selectedCategoryId]);

  useEffect(() => {
    loadCategories();
  }, []);

  async function loadCategories() {
    try {
      const cats = await api.listCategories();
      setCategories(cats);
    } catch (error) {
      console.error('Failed to load categories', error);
    }
  }

  async function loadEvents(pageNumber: number, reset: boolean = false) {
    if (pageNumber === 1) {
      if (!reset) setLoading(true);
    } else {
      setLoadingMore(true);
    }

    try {
      let res: PaginatedResponse<EventResponse>;
      
      if (searchQuery.length >= 2) {
        res = await api.searchEvents(searchQuery, pageNumber);
      } else {
        res = await api.listEvents({
          page: pageNumber,
          category_id: selectedCategoryId || undefined,
        });
      }

      if (reset || pageNumber === 1) {
        setEvents(res.items);
      } else {
        setEvents(prev => [...prev, ...res.items]);
      }
      
      setTotalPages(res.pages);
      setPage(pageNumber);
    } catch (error) {
      console.error('Failed to load events', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
      setLoadingMore(false);
    }
  }

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    loadEvents(1, true);
  }, [searchQuery, selectedCategoryId]);

  const loadMore = () => {
    if (!loadingMore && page < totalPages) {
      loadEvents(page + 1);
    }
  };

  const getCategoryName = (id: number) => {
    return categories.find(c => c.id === id)?.name || 'Evento';
  };

  return (
    <View style={styles.container}>
      <FilterBar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        categories={categories}
        selectedCategoryId={selectedCategoryId}
        onCategorySelect={setSelectedCategoryId}
      />

      {loading && page === 1 ? (
        <View style={styles.centered}>
          <ActivityIndicator size="large" color="#007bff" />
        </View>
      ) : (
        <FlatList
          data={events}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <EventCard
              event={item}
              categoryName={getCategoryName(item.category_id)}
              onPress={() => navigation.navigate('EventDetail', { id: item.id })}
            />
          )}
          contentContainerStyle={styles.listContent}
          onEndReached={loadMore}
          onEndReachedThreshold={0.5}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#007bff']} />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyText}>Nenhum evento encontrado.</Text>
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
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  listContent: {
    padding: 15,
    paddingBottom: 30,
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    color: '#666',
    fontSize: 16,
  },
});
