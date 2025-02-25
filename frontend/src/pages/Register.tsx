import { useState } from 'react';
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
} from '@mui/material';
import { registerArtist } from '../services/api';

const artistTypes = [
  { value: 'Peintre', label: 'Peintre' },
  { value: 'Photographe', label: 'Photographe' },
  { value: 'Numérique', label: 'Artiste Numérique' },
  { value: 'Sculpteur', label: 'Sculpteur' },
] as const;

type ArtistType = typeof artistTypes[number]['value'];

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    nom: '',
    prenom: '',
    nom_artiste: '',
    email: '',
    password: '',
    confirmPassword: '',
    telephone: '',
    adresse: '',
    type_artiste: '' as ArtistType,
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (formData.password !== formData.confirmPassword) {
      setError("Les mots de passe ne correspondent pas");
      return;
    }

    try {
      setLoading(true);
      const artistData = {
        nom: formData.nom,
        prenom: formData.prenom,
        nom_artiste: formData.nom_artiste,
        email: formData.email,
        telephone: formData.telephone,
        adresse: formData.adresse,
        type_artiste: formData.type_artiste,
      };
      await registerArtist(artistData);
      navigate('/connexion', { 
        state: { message: 'Inscription réussie ! Vous pouvez maintenant vous connecter.' }
      });
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur lors de l\'inscription');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 8, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Inscription Artiste
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit} noValidate>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                name="nom"
                label="Nom"
                value={formData.nom}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                name="prenom"
                label="Prénom"
                value={formData.prenom}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                name="nom_artiste"
                label="Nom d'artiste"
                value={formData.nom_artiste}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                name="email"
                label="Adresse email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                name="password"
                label="Mot de passe"
                type="password"
                value={formData.password}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                name="confirmPassword"
                label="Confirmer le mot de passe"
                type="password"
                value={formData.confirmPassword}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="telephone"
                label="Téléphone"
                value={formData.telephone}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                select
                name="type_artiste"
                label="Type d'artiste"
                value={formData.type_artiste}
                onChange={handleChange}
                disabled={loading}
              >
                {artistTypes.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                name="adresse"
                label="Adresse"
                multiline
                rows={2}
                value={formData.adresse}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>
          </Grid>

          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading}
          >
            {loading ? 'Inscription en cours...' : 'S\'inscrire'}
          </Button>

          <Button
            fullWidth
            variant="text"
            onClick={() => navigate('/connexion')}
            disabled={loading}
          >
            Déjà un compte ? Se connecter
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default Register;
