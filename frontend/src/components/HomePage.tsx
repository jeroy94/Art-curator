import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  Typography,
  Paper,
  Grid,
} from '@mui/material';
import { Palette as PaletteIcon, AdminPanelSettings as AdminIcon } from '@mui/icons-material';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 8, mb: 4 }}>
        <Typography variant="h2" align="center" gutterBottom>
          Exposition d'Art
        </Typography>
        <Typography variant="h5" align="center" color="textSecondary" paragraph>
          Bienvenue sur notre plateforme d'exposition d'art numérique
        </Typography>
      </Box>
      
      <Grid container spacing={4} justifyContent="center">
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 4,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              cursor: 'pointer',
              transition: '0.3s',
              '&:hover': {
                transform: 'translateY(-5px)',
                boxShadow: 3,
              },
            }}
            onClick={() => navigate('/register')}
          >
            <PaletteIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Espace Artiste
            </Typography>
            <Typography align="center" color="textSecondary">
              Inscrivez-vous pour soumettre vos œuvres d'art
            </Typography>
            <Button
              variant="contained"
              color="primary"
              sx={{ mt: 2 }}
              onClick={(e: React.MouseEvent) => {
                e.stopPropagation();
                navigate('/register');
              }}
            >
              S'inscrire
            </Button>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 4,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              cursor: 'pointer',
              transition: '0.3s',
              '&:hover': {
                transform: 'translateY(-5px)',
                boxShadow: 3,
              },
            }}
            onClick={() => navigate('/admin/login')}
          >
            <AdminIcon sx={{ fontSize: 60, color: 'secondary.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Espace Administrateur
            </Typography>
            <Typography align="center" color="textSecondary">
              Gérez les artistes et les œuvres
            </Typography>
            <Button
              variant="contained"
              color="secondary"
              sx={{ mt: 2 }}
              onClick={(e: React.MouseEvent) => {
                e.stopPropagation();
                navigate('/admin/login');
              }}
            >
              Se connecter
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default HomePage;
