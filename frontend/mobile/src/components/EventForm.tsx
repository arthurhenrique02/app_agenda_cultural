import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, Alert, Image, ActivityIndicator } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as api from '../services/api';
import { CategoryResponse, EventCreateRequest, EventResponse } from '../types/api';

interface EventFormProps {
  initialData?: EventResponse;
  onSubmit: (data: EventCreateRequest) => Promise<void>;
  submitLabel: string;
}

export default function EventForm({ initialData, onSubmit, submitLabel }: EventFormProps) {
  const [categories, setCategories] = useState<CategoryResponse[]>([]);
  const [loadingCats, setLoadingCats] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [title, setTitle] = useState(initialData?.title || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [date, setDate] = useState(initialData?.date || '');
  const [startTime, setStartTime] = useState(initialData?.start_time || '');
  const [endTime, setEndTime] = useState(initialData?.end_time || '');
  const [venueName, setVenueName] = useState(initialData?.venue_name || '');
  const [address, setAddress] = useState(initialData?.address || '');
  const [neighborhood, setNeighborhood] = useState(initialData?.neighborhood || '');
  const [city, setCity] = useState(initialData?.city || '');
  const [categoryId, setCategoryId] = useState<number | string>(initialData?.category_id || '');
  const [imageUrl, setImageUrl] = useState(initialData?.image_url || '');
  const [uploadingImage, setUploadingImage] = useState(false);

  useEffect(() => {
    api.listCategories().then(setCategories).finally(() => setLoadingCats(false));
  }, []);

  async function pickImage() {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [16, 9],
      quality: 0.8,
    });

    if (!result.canceled) {
      handleUpload(result.assets[0].uri);
    }
  }

  async function handleUpload(uri: string) {
    setUploadingImage(true);
    try {
      const filename = uri.split('/').pop() || 'upload.jpg';
      const match = /\.(\w+)$/.exec(filename);
      const type = match ? `image/${match[1]}` : `image`;
      
      const res = await api.uploadImage(uri, type, filename);
      setImageUrl(res.url);
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível carregar a imagem.');
    } finally {
      setUploadingImage(false);
    }
  }

  async function handleSubmit() {
    if (!title || !description || !date || !startTime || !venueName || !address || !neighborhood || !city || !categoryId) {
      Alert.alert('Campos Obrigatórios', 'Por favor, preencha todos os campos obrigatórios.');
      return;
    }

    setSubmitting(true);
    try {
      await onSubmit({
        title,
        description,
        date,
        start_time: startTime,
        end_time: endTime || null,
        venue_name: venueName,
        address,
        neighborhood,
        city,
        category_id: Number(categoryId),
        image_url: imageUrl || null,
      });
    } catch (error: any) {
      Alert.alert('Erro ao Salvar', error.message || 'Ocorreu um erro inesperado.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.label}>Título do Evento *</Text>
      <TextInput style={styles.input} value={title} onChangeText={setTitle} placeholder="Ex: Show de Rock" />

      <Text style={styles.label}>Descrição *</Text>
      <TextInput 
        style={[styles.input, styles.textArea]} 
        value={description} 
        onChangeText={setDescription} 
        placeholder="Detalhes sobre o evento..."
        multiline
        numberOfLines={4}
      />

      <View style={styles.row}>
        <View style={styles.flex1}>
          <Text style={styles.label}>Data (AAAA-MM-DD) *</Text>
          <TextInput style={styles.input} value={date} onChangeText={setDate} placeholder="2026-05-21" />
        </View>
      </View>

      <View style={styles.row}>
        <View style={styles.flex1}>
          <Text style={styles.label}>Início *</Text>
          <TextInput style={styles.input} value={startTime} onChangeText={setStartTime} placeholder="19:00" />
        </View>
        <View style={styles.flex1}>
          <Text style={styles.label}>Término</Text>
          <TextInput style={styles.input} value={endTime || ''} onChangeText={setEndTime} placeholder="22:00" />
        </View>
      </View>

      <Text style={styles.label}>Nome do Local *</Text>
      <TextInput style={styles.input} value={venueName} onChangeText={setVenueName} placeholder="Ex: Teatro Municipal" />

      <Text style={styles.label}>Endereço Completo *</Text>
      <TextInput style={styles.input} value={address} onChangeText={setAddress} placeholder="Rua, Número" />

      <View style={styles.row}>
        <View style={styles.flex1}>
          <Text style={styles.label}>Bairro *</Text>
          <TextInput style={styles.input} value={neighborhood} onChangeText={setNeighborhood} />
        </View>
        <View style={styles.flex1}>
          <Text style={styles.label}>Cidade *</Text>
          <TextInput style={styles.input} value={city} onChangeText={setCity} />
        </View>
      </View>

      <Text style={styles.label}>Categoria *</Text>
      {loadingCats ? (
        <ActivityIndicator size="small" color="#007bff" />
      ) : (
        <View style={styles.categoryGrid}>
          {categories.map(cat => (
            <TouchableOpacity 
              key={cat.id} 
              style={[styles.categoryBtn, categoryId === cat.id && styles.categoryBtnSelected]}
              onPress={() => setCategoryId(cat.id)}
            >
              <Text style={[styles.categoryBtnText, categoryId === cat.id && styles.categoryBtnTextSelected]}>
                {cat.name}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      )}

      <Text style={styles.label}>Imagem do Evento</Text>
      <TouchableOpacity style={styles.imagePicker} onPress={pickImage} disabled={uploadingImage}>
        {uploadingImage ? (
          <ActivityIndicator color="#007bff" />
        ) : imageUrl ? (
          <Image source={{ uri: imageUrl }} style={styles.previewImage} />
        ) : (
          <Text style={styles.imagePickerText}>Selecionar Foto</Text>
        )}
      </TouchableOpacity>
      {imageUrl ? (
        <TouchableOpacity onPress={() => setImageUrl('')}>
          <Text style={styles.removeImage}>Remover Imagem</Text>
        </TouchableOpacity>
      ) : null}

      <TouchableOpacity 
        style={[styles.submitBtn, submitting && styles.submitBtnDisabled]} 
        onPress={handleSubmit}
        disabled={submitting}
      >
        {submitting ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.submitBtnText}>{submitLabel}</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    padding: 20,
    paddingBottom: 40,
  },
  label: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
    marginTop: 15,
  },
  input: {
    height: 50,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 15,
    fontSize: 16,
  },
  textArea: {
    height: 100,
    paddingTop: 12,
    textAlignVertical: 'top',
  },
  row: {
    flexDirection: 'row',
    gap: 15,
  },
  flex1: {
    flex: 1,
  },
  categoryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  categoryBtn: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
    borderWidth: 1,
    borderColor: '#eee',
  },
  categoryBtnSelected: {
    backgroundColor: '#007bff',
    borderColor: '#007bff',
  },
  categoryBtnText: {
    fontSize: 12,
    color: '#666',
  },
  categoryBtnTextSelected: {
    color: '#fff',
    fontWeight: 'bold',
  },
  imagePicker: {
    height: 150,
    borderWidth: 1,
    borderColor: '#ddd',
    borderStyle: 'dashed',
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f9f9f9',
    overflow: 'hidden',
  },
  imagePickerText: {
    color: '#007bff',
  },
  previewImage: {
    width: '100%',
    height: '100%',
  },
  removeImage: {
    color: '#dc3545',
    textAlign: 'center',
    marginTop: 10,
    fontSize: 14,
  },
  submitBtn: {
    height: 55,
    backgroundColor: '#007bff',
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 40,
  },
  submitBtnDisabled: {
    backgroundColor: '#a0cfff',
  },
  submitBtnText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
