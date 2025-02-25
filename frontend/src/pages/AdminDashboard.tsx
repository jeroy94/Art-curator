import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Grid,
  Box,
  Button,
  Dialog,
  Tab,
  Tabs,
  TextField,
  InputAdornment,
  CircularProgress,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  Search as SearchIcon,
  FileDownload as FileDownloadIcon,
  Save as SaveIcon,
} from '@mui/icons-material';
import { Artwork } from '../types/artwork';
import ArtworkCard from '../components/ArtworkCard';
import ArtworkViewer3D from '../components/ArtworkViewer3D';
import ArtworkDetails from '../components/ArtworkDetails';
import { fetchArtworks, finalizeSelection, generateCatalog } from '../services/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
};

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [artworks, setArtworks] = useState<Artwork[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedArtworks, setSelectedArtworks] = useState<number[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [viewer3DOpen, setViewer3DOpen] = useState(false);
  const [currentArtwork, setCurrentArtwork] = useState<Artwork | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error',
  });

  useEffect(() => {
    // Vérifier si l'utilisateur est admin
    const user = localStorage.getItem('user');
    if (!user || !JSON.parse(user).is_admin) {
      navigate('/');
      return;
    }

    loadArtworks();
  }, [navigate]);

  const loadArtworks = async () => {
    try {
      const data = await fetchArtworks();
      setArtworks(data);
      // Restaurer les sélections précédentes
      setSelectedArtworks(data.filter(a => a.selectionne).map(a => a.id));
    } catch (err) {
      setError('Erreur lors du chargement des œuvres');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleArtworkSelection = (id: number, selected: boolean) => {
    setSelectedArtworks(prev => 
      selected 
        ? [...prev, id]
        : prev.filter(artworkId => artworkId !== id)
    );
  };

  const handleView3D = (id: number) => {
    const artwork = artworks.find(a => a.id === id);
    if (artwork) {
      setCurrentArtwork(artwork);
      setViewer3DOpen(true);
    }
  };

  const handleViewDetails = (id: number) => {
    const artwork = artworks.find(a => a.id === id);
    if (artwork) {
      setCurrentArtwork(artwork);
      setDetailsOpen(true);
    }
  };

  const handleSaveSelection = async () => {
    try {
      await finalizeSelection(selectedArtworks);
      setSnackbar({
        open: true,
        message: 'Sélection enregistrée avec succès',
        severity: 'success',
      });
      loadArtworks(); // Recharger pour mettre à jour les statuts
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Erreur lors de l\'enregistrement de la sélection',
        severity: 'error',
      });
    }
  };

  const handleGeneratePDF = async () => {
    try {
      const pdfBlob = await generateCatalog();
      
      // Créer un URL pour le blob
      const url = window.URL.createObjectURL(pdfBlob);
      
      // Créer un lien temporaire pour le téléchargement
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'catalogue_oeuvres.pdf');
      
      // Déclencher le téléchargement
      document.body.appendChild(link);
      link.click();
      
      // Nettoyer
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      setSnackbar({
        open: true,
        message: 'Catalogue PDF généré avec succès',
        severity: 'success',
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Erreur lors de la génération du PDF',
        severity: 'error',
      });
    }
  };

  const filteredArtworks = artworks.filter(artwork => {
    const searchLower = searchTerm.toLowerCase();
    return (
      artwork.nom.toLowerCase().includes(searchLower) ||
      artwork.artist.nom_artiste.toLowerCase().includes(searchLower) ||
      artwork.type_oeuvre.toLowerCase().includes(searchLower)
    );
  });

  const currentTabArtworks = tabValue === 0
    ? filteredArtworks
    : filteredArtworks.filter(a => selectedArtworks.includes(a.id));

  if (loading) {
    return (
      <Box 
        sx={{ 
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '80vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard Administrateur
        </Typography>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="Toutes les œuvres" />
            <Tab label={`Œuvres sélectionnées (${selectedArtworks.length})`} />
          </Tabs>
        </Box>
      </Box>

      <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
        <TextField
          placeholder="Rechercher une œuvre..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ flexGrow: 1 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
        
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleSaveSelection}
          disabled={selectedArtworks.length === 0}
        >
          Enregistrer la sélection
        </Button>
        
        <Button
          variant="outlined"
          startIcon={<FileDownloadIcon />}
          disabled={selectedArtworks.length === 0}
          onClick={handleGeneratePDF}
        >
          Générer le PDF
        </Button>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          {currentTabArtworks.map((artwork) => (
            <Grid item key={artwork.id} xs={12} sm={6} md={4} lg={3}>
              <ArtworkCard
                artwork={artwork}
                onSelect={handleArtworkSelection}
                onView3D={handleView3D}
                onViewDetails={handleViewDetails}
                isSelected={selectedArtworks.includes(artwork.id)}
              />
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          {currentTabArtworks.map((artwork) => (
            <Grid item key={artwork.id} xs={12} sm={6} md={4} lg={3}>
              <ArtworkCard
                artwork={artwork}
                onSelect={handleArtworkSelection}
                onView3D={handleView3D}
                onViewDetails={handleViewDetails}
                isSelected={true}
              />
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      {/* Dialogue de visualisation 3D */}
      <Dialog
        open={viewer3DOpen}
        onClose={() => setViewer3DOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <Box sx={{ p: 2 }}>
          {currentArtwork && (
            <ArtworkViewer3D
              imageUrl={`/api/artwork/${currentArtwork.id}/image`}
              width={800}
              height={600}
            />
          )}
        </Box>
      </Dialog>

      {/* Dialogue de détails */}
      <ArtworkDetails
        artwork={currentArtwork}
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
      />

      {/* Snackbar pour les notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
      >
        <Alert severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default AdminDashboard;
