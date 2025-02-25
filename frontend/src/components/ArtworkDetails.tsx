import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Grid,
  Box,
  Divider,
  Chip,
} from '@mui/material';
import { Artwork } from '../types/artwork';

interface ArtworkDetailsProps {
  artwork: Artwork | null;
  open: boolean;
  onClose: () => void;
}

const ArtworkDetails = ({ artwork, open, onClose }: ArtworkDetailsProps) => {
  if (!artwork) return null;

  const renderDimensions = () => {
    if (artwork.type_oeuvre === 'Sculpture') {
      return (
        <>
          <Typography variant="body2">
            <strong>Dimensions:</strong> {artwork.dimension_hauteur}h x{' '}
            {artwork.dimension_largeur}l x {artwork.dimension_longueur}L cm
          </Typography>
          {artwork.poids && (
            <Typography variant="body2">
              <strong>Poids:</strong> {artwork.poids} kg
            </Typography>
          )}
          {artwork.dimension_socle && (
            <Typography variant="body2">
              <strong>Dimensions du socle:</strong> {artwork.dimension_socle}
            </Typography>
          )}
        </>
      );
    } else {
      return (
        <>
          <Typography variant="body2">
            <strong>Dimensions hors cadre:</strong>{' '}
            {artwork.dimension_hors_cadre_hauteur}h x{' '}
            {artwork.dimension_hors_cadre_largeur}l cm
          </Typography>
          {artwork.dimension_avec_cadre_hauteur && (
            <Typography variant="body2">
              <strong>Dimensions avec cadre:</strong>{' '}
              {artwork.dimension_avec_cadre_hauteur}h x{' '}
              {artwork.dimension_avec_cadre_largeur}l cm
            </Typography>
          )}
        </>
      );
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        <Typography variant="h5" component="div">
          {artwork.nom}
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          par {artwork.artist.nom_artiste}
        </Typography>
      </DialogTitle>

      <DialogContent>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Box
              component="img"
              src={`/api/artwork/${artwork.id}/image`}
              alt={artwork.nom}
              sx={{
                width: '100%',
                height: 'auto',
                maxHeight: 400,
                objectFit: 'contain',
                borderRadius: 1,
              }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <Box sx={{ mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                Informations
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Chip
                  label={artwork.type_oeuvre}
                  color="primary"
                  variant="outlined"
                />
                <Chip
                  label={`${artwork.prix} €`}
                  color="secondary"
                  variant="outlined"
                />
              </Box>
              
              <Typography variant="body2" paragraph>
                <strong>Technique:</strong> {artwork.technique}
              </Typography>

              {renderDimensions()}
            </Box>

            <Divider sx={{ my: 2 }} />

            <Box>
              <Typography variant="h6" gutterBottom>
                Artiste
              </Typography>
              <Typography variant="body2">
                <strong>Nom:</strong> {artwork.artist.nom} {artwork.artist.prenom}
              </Typography>
              <Typography variant="body2">
                <strong>Email:</strong> {artwork.artist.email}
              </Typography>
              {artwork.artist.telephone && (
                <Typography variant="body2">
                  <strong>Téléphone:</strong> {artwork.artist.telephone}
                </Typography>
              )}
              {artwork.artist.adresse && (
                <Typography variant="body2">
                  <strong>Adresse:</strong> {artwork.artist.adresse}
                </Typography>
              )}
            </Box>

            <Divider sx={{ my: 2 }} />

            <Box>
              <Typography variant="h6" gutterBottom>
                Statut
              </Typography>
              <Typography variant="body2">
                <strong>Date de soumission:</strong>{' '}
                {new Date(artwork.date_soumission).toLocaleDateString()}
              </Typography>
              <Typography variant="body2">
                <strong>Votes:</strong> {artwork.votes}
              </Typography>
              <Chip
                label={artwork.selectionne ? "Sélectionné" : "Non sélectionné"}
                color={artwork.selectionne ? "success" : "default"}
                sx={{ mt: 1 }}
              />
            </Box>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Fermer</Button>
      </DialogActions>
    </Dialog>
  );
};

export default ArtworkDetails;
