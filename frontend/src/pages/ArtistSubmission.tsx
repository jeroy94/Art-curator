import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  MenuItem,
  Grid,
  CircularProgress,
} from '@mui/material';
import { submitArtwork } from '../services/api';

const artworkTypes = [
  { value: 'Peinture', label: 'Peinture' },
  { value: 'Photo', label: 'Photographie' },
  { value: 'Numérique', label: 'Art Numérique' },
  { value: 'Sculpture', label: 'Sculpture' },
];

interface FormData {
  nom: string;
  prix: string;
  technique: string;
  type_oeuvre: string;
  photo: File | null;
  dimension_hors_cadre_hauteur?: string;
  dimension_hors_cadre_largeur?: string;
  dimension_avec_cadre_hauteur?: string;
  dimension_avec_cadre_largeur?: string;
  dimension_hauteur?: string;
  dimension_largeur?: string;
  dimension_longueur?: string;
  poids?: string;
  dimension_socle?: string;
}

const ArtistSubmission = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<FormData>({
    nom: '',
    prix: '',
    technique: '',
    type_oeuvre: '',
    photo: null,
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  useEffect(() => {
    // Vérifier si l'utilisateur est connecté
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/connexion', { 
        state: { message: 'Veuillez vous connecter pour soumettre une œuvre.' }
      });
    }
  }, [navigate]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setFormData((prev) => ({
        ...prev,
        photo: file,
      }));

      // Créer une URL pour la prévisualisation
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);

      // Nettoyer l'URL lors du démontage du composant
      return () => URL.revokeObjectURL(url);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // Validation des champs requis
      if (!formData.nom || !formData.prix || !formData.type_oeuvre || !formData.photo) {
        throw new Error('Veuillez remplir tous les champs obligatoires');
      }

      // Créer un FormData pour l'envoi du fichier
      const submitData = new FormData();
      Object.entries(formData).forEach(([key, value]) => {
        if (value !== null && value !== '') {
          submitData.append(key, value);
        }
      });

      await submitArtwork(submitData);
      navigate('/', { 
        state: { message: 'Votre œuvre a été soumise avec succès !' }
      });
    } catch (err: any) {
      setError(err.message || 'Erreur lors de la soumission');
    } finally {
      setLoading(false);
    }
  };

  const renderDimensionFields = () => {
    if (formData.type_oeuvre === 'Sculpture') {
      return (
        <>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              name="dimension_hauteur"
              label="Hauteur (cm)"
              type="number"
              value={formData.dimension_hauteur || ''}
              onChange={handleChange}
              disabled={loading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              name="dimension_largeur"
              label="Largeur (cm)"
              type="number"
              value={formData.dimension_largeur || ''}
              onChange={handleChange}
              disabled={loading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              name="dimension_longueur"
              label="Longueur (cm)"
              type="number"
              value={formData.dimension_longueur || ''}
              onChange={handleChange}
              disabled={loading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              name="poids"
              label="Poids (kg)"
              type="number"
              value={formData.poids || ''}
              onChange={handleChange}
              disabled={loading}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              name="dimension_socle"
              label="Dimensions du socle"
              value={formData.dimension_socle || ''}
              onChange={handleChange}
              disabled={loading}
            />
          </Grid>
        </>
      );
    } else {
      return (
        <>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="dimension_hors_cadre_hauteur"
              label="Hauteur hors cadre (cm)"
              type="number"
              value={formData.dimension_hors_cadre_hauteur || ''}
              onChange={handleChange}
              disabled={loading}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="dimension_hors_cadre_largeur"
              label="Largeur hors cadre (cm)"
              type="number"
              value={formData.dimension_hors_cadre_largeur || ''}
              onChange={handleChange}
              disabled={loading}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="dimension_avec_cadre_hauteur"
              label="Hauteur avec cadre (cm)"
              type="number"
              value={formData.dimension_avec_cadre_hauteur || ''}
              onChange={handleChange}
              disabled={loading}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="dimension_avec_cadre_largeur"
              label="Largeur avec cadre (cm)"
              type="number"
              value={formData.dimension_avec_cadre_largeur || ''}
              onChange={handleChange}
              disabled={loading}
            />
          </Grid>
        </>
      );
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 8, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Soumettre une Œuvre
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit} noValidate>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                name="nom"
                label="Nom de l'œuvre"
                value={formData.nom}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                name="prix"
                label="Prix (€)"
                type="number"
                value={formData.prix}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                select
                name="type_oeuvre"
                label="Type d'œuvre"
                value={formData.type_oeuvre}
                onChange={handleChange}
                disabled={loading}
              >
                {artworkTypes.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                name="technique"
                label="Technique utilisée"
                multiline
                rows={2}
                value={formData.technique}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>

            {formData.type_oeuvre && renderDimensionFields()}

            <Grid item xs={12}>
              <Button
                variant="contained"
                component="label"
                fullWidth
                disabled={loading}
              >
                {formData.photo ? 'Changer la photo' : 'Ajouter une photo'}
                <input
                  type="file"
                  hidden
                  accept="image/*"
                  onChange={handleFileChange}
                />
              </Button>
            </Grid>

            {previewUrl && (
              <Grid item xs={12}>
                <Box
                  component="img"
                  src={previewUrl}
                  alt="Prévisualisation"
                  sx={{
                    width: '100%',
                    maxHeight: 300,
                    objectFit: 'contain',
                    mt: 2,
                  }}
                />
              </Grid>
            )}

            <Grid item xs={12}>
              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={loading}
                sx={{ mt: 2 }}
              >
                {loading ? (
                  <>
                    <CircularProgress size={24} sx={{ mr: 1 }} />
                    Soumission en cours...
                  </>
                ) : (
                  'Soumettre l\'œuvre'
                )}
              </Button>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    </Container>
  );
};

export default ArtistSubmission;
