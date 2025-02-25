import {
  Card,
  CardContent,
  CardMedia,
  Typography,
  Button,
  Box,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Check as CheckIcon,
  Close as CloseIcon,
  ThreeDRotation as ThreeDIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { Artwork } from '../types/artwork';

interface ArtworkCardProps {
  artwork: Artwork;
  onSelect: (id: number, selected: boolean) => void;
  onView3D: (id: number) => void;
  onViewDetails: (id: number) => void;
  isSelected: boolean;
}

const ArtworkCard = ({
  artwork,
  onSelect,
  onView3D,
  onViewDetails,
  isSelected,
}: ArtworkCardProps) => {
  return (
    <Card 
      sx={{ 
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        border: isSelected ? '2px solid #1976d2' : 'none',
      }}
    >
      <CardMedia
        component="img"
        height="200"
        image={`/api/artwork/${artwork.id}/image`}
        alt={artwork.nom}
        sx={{ objectFit: 'cover' }}
      />
      
      <Box 
        sx={{ 
          position: 'absolute',
          top: 8,
          right: 8,
          display: 'flex',
          gap: 1,
        }}
      >
        <Tooltip title="Voir en 3D">
          <IconButton
            onClick={() => onView3D(artwork.id)}
            sx={{ 
              bgcolor: 'background.paper',
              '&:hover': { bgcolor: 'action.hover' },
            }}
          >
            <ThreeDIcon />
          </IconButton>
        </Tooltip>
        
        <Tooltip title="Détails">
          <IconButton
            onClick={() => onViewDetails(artwork.id)}
            sx={{ 
              bgcolor: 'background.paper',
              '&:hover': { bgcolor: 'action.hover' },
            }}
          >
            <InfoIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <CardContent sx={{ flexGrow: 1 }}>
        <Typography gutterBottom variant="h6" component="div" noWrap>
          {artwork.nom}
        </Typography>
        
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {artwork.artist.nom_artiste}
        </Typography>
        
        <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip
            label={artwork.type_oeuvre}
            size="small"
            color="primary"
            variant="outlined"
          />
          <Chip
            label={`${artwork.prix} €`}
            size="small"
            color="secondary"
            variant="outlined"
          />
        </Box>

        <Box sx={{ mt: 2 }}>
          <Button
            variant={isSelected ? "contained" : "outlined"}
            color={isSelected ? "success" : "primary"}
            fullWidth
            onClick={() => onSelect(artwork.id, !isSelected)}
            startIcon={isSelected ? <CheckIcon /> : <CloseIcon />}
          >
            {isSelected ? "Sélectionné" : "Sélectionner"}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ArtworkCard;
