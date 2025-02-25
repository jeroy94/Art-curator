import axios from 'axios';
import { Artwork, Artist } from '../types/artwork';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token JWT aux requêtes
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Authentification
export const login = async (email: string, password: string) => {
  const response = await api.post('/auth/login', { email, password });
  return response.data;
};

export const registerArtist = async (artistData: Partial<Artist>) => {
  const response = await api.post('/auth/register/artist', artistData);
  return response.data;
};

// Œuvres d'art
export const fetchArtworks = async (): Promise<Artwork[]> => {
  const response = await api.get('/artworks');
  return response.data;
};

export const fetchArtworkById = async (id: number): Promise<Artwork> => {
  const response = await api.get(`/artwork/${id}`);
  return response.data;
};

export const submitArtwork = async (formData: FormData) => {
  const response = await api.post('/artwork', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Administration
export const voteForArtwork = async (artworkId: number) => {
  const response = await api.post('/vote', { oeuvre_id: artworkId });
  return response.data;
};

export const finalizeSelection = async (selectedArtworks: number[]) => {
  const response = await api.post('/selection/finalize', {
    selected_artworks: selectedArtworks,
  });
  return response.data;
};

// Génération de PDF
export const generateCatalog = async () => {
  const response = await api.get('/pdf/generate/catalog', {
    responseType: 'blob',
  });
  return response.data;
};

export const generateArtistSummary = async (artistId: number) => {
  const response = await api.get(`/pdf/generate/artist-summary/${artistId}`, {
    responseType: 'blob',
  });
  return response.data;
};

// Gestion des erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/connexion';
    }
    return Promise.reject(error);
  }
);
