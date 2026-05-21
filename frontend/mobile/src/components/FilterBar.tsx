import React from 'react';
import { View, TextInput, ScrollView, TouchableOpacity, Text, StyleSheet } from 'react-native';
import { CategoryResponse } from '../types/api';

interface FilterBarProps {
  searchQuery: string;
  onSearchChange: (text: string) => void;
  categories: CategoryResponse[];
  selectedCategoryId: number | null;
  onCategorySelect: (id: number | null) => void;
}

export default function FilterBar({
  searchQuery,
  onSearchChange,
  categories,
  selectedCategoryId,
  onCategorySelect,
}: FilterBarProps) {
  return (
    <View style={styles.container}>
      <TextInput
        style={styles.searchInput}
        placeholder="Buscar eventos..."
        value={searchQuery}
        onChangeText={onSearchChange}
      />
      
      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false} 
        style={styles.categoryList}
        contentContainerStyle={styles.categoryContent}
      >
        <TouchableOpacity
          style={[
            styles.categoryItem,
            selectedCategoryId === null && styles.categoryItemSelected
          ]}
          onPress={() => onCategorySelect(null)}
        >
          <Text style={[
            styles.categoryText,
            selectedCategoryId === null && styles.categoryTextSelected
          ]}>Todos</Text>
        </TouchableOpacity>

        {categories.map((cat) => (
          <TouchableOpacity
            key={cat.id}
            style={[
              styles.categoryItem,
              selectedCategoryId === cat.id && styles.categoryItemSelected
            ]}
            onPress={() => onCategorySelect(cat.id)}
          >
            <Text style={[
              styles.categoryText,
              selectedCategoryId === cat.id && styles.categoryTextSelected
            ]}>{cat.name}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  searchInput: {
    height: 45,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    paddingHorizontal: 15,
    marginHorizontal: 15,
    marginBottom: 12,
    fontSize: 16,
  },
  categoryList: {
    paddingLeft: 15,
  },
  categoryContent: {
    paddingRight: 30,
  },
  categoryItem: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
    marginRight: 8,
  },
  categoryItemSelected: {
    backgroundColor: '#007bff',
  },
  categoryText: {
    fontSize: 14,
    color: '#666',
  },
  categoryTextSelected: {
    color: '#fff',
    fontWeight: 'bold',
  },
});
