import { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Button,
  Box,
} from '@mui/material';
import { Artwork } from '../types/artwork';
import { fetchArtworks } from '../services/api';

const Home = () => {
  const [artworks, setArtworks] = useState<Artwork[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadArtworks = async () => {
      try {
        const data = await fetchArtworks();
        setArtworks(data);
        setLoading(false);
      } catch (err) {
        setError('Erreur lors du chargement des œuvres');
        setLoading(false);
      }
    };

    loadArtworks();
  }, []);

  if (loading) {
    return (
      <Container>
        <Typography>Chargement...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Typography color="error">{error}</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h2" component="h1" gutterBottom>
          Bienvenue à l'Exposition d'Art
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          Découvrez une collection unique d'œuvres d'art contemporain
        </Typography>
        <Button
          variant="contained"
          size="large"
          component={RouterLink}
          to="/soumettre"
          sx={{ mt: 2 }}
        >
          Soumettre votre Œuvre
        </Button>
      </Box>

      <Grid container spacing={4}>
        {artworks.map((artwork) => (
          <Grid item key={artwork.id} xs={12} sm={6} md={4}>
            <Card>
              <CardMedia
                component="img"
                height="200"
                image={`/api/artwork/${artwork.id}/image`}
                alt={artwork.nom}
              />
              <CardContent>
                <Typography gutterBottom variant="h6" component="div">
                  {artwork.nom}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {artwork.artist.nom} {artwork.artist.prenom}
                </Typography>
                <Button
                  component={RouterLink}
                  to={`/oeuvre/${artwork.id}`}
                  variant="outlined"
                  sx={{ mt: 2 }}
                >
                  Voir les détails
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default Home;
