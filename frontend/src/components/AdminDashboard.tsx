import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  TextField,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import { Artist } from '../types/artwork';

interface AdminDashboardProps {
  onLogout: () => void;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ onLogout }) => {
  const [artists, setArtists] = useState<Artist[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [selectedArtist, setSelectedArtist] = useState<Artist | null>(null);
  const [viewerOpen, setViewerOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Ici, vous devriez charger les artistes depuis votre API
    const fetchArtists = async () => {
      try {
        const response = await fetch('/api/artists');
        const data = await response.json();
        setArtists(data);
      } catch (error) {
        console.error('Erreur lors du chargement des artistes:', error);
      }
    };
    fetchArtists();
  }, []);

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleViewArtist = (artist: Artist) => {
    setSelectedArtist(artist);
    setViewerOpen(true);
  };

  const handleCloseViewer = () => {
    setViewerOpen(false);
    setSelectedArtist(null);
  };

  const filteredArtists = artists.filter((artist) =>
    artist.nom_artiste.toLowerCase().includes(searchTerm.toLowerCase()) ||
    artist.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    artist.prenom.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Tableau de Bord Administrateur</Typography>
        <Button variant="contained" color="secondary" onClick={onLogout}>
          Déconnexion
        </Button>
      </Box>

      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Rechercher un artiste..."
          value={searchTerm}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: <SearchIcon sx={{ mr: 1 }} />,
          }}
        />
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Nom d'artiste</TableCell>
              <TableCell>Nom</TableCell>
              <TableCell>Prénom</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredArtists
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((artist) => (
                <TableRow key={artist.id}>
                  <TableCell>{artist.nom_artiste}</TableCell>
                  <TableCell>{artist.nom}</TableCell>
                  <TableCell>{artist.prenom}</TableCell>
                  <TableCell>{artist.type_artiste}</TableCell>
                  <TableCell>
                    <IconButton onClick={() => handleViewArtist(artist)}>
                      <VisibilityIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredArtists.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>

      <Dialog
        open={viewerOpen}
        onClose={handleCloseViewer}
        maxWidth="md"
        fullWidth
      >
        {selectedArtist && (
          <>
            <DialogTitle>
              Détails de l'artiste : {selectedArtist.nom_artiste}
            </DialogTitle>
            <DialogContent>
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6">Informations personnelles</Typography>
                <Typography>Nom : {selectedArtist.nom}</Typography>
                <Typography>Prénom : {selectedArtist.prenom}</Typography>
                <Typography>Email : {selectedArtist.email}</Typography>
                <Typography>Téléphone : {selectedArtist.telephone || 'Non renseigné'}</Typography>
                <Typography>Adresse : {selectedArtist.adresse || 'Non renseignée'}</Typography>
                <Typography>Type : {selectedArtist.type_artiste}</Typography>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseViewer}>Fermer</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default AdminDashboard;
