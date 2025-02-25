import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  FormControl,
  FormControlLabel,
  RadioGroup,
  Radio,
  Typography,
  Grid,
  Checkbox,
  Paper,
  Alert,
} from '@mui/material';
import { styled } from '@mui/material/styles';

const Input = styled('input')({
  display: 'none',
});

interface ArtworkFields {
  titre: string;
  technique: string;
  dimensions: string;
  prix: string;
  photo: File | null;
}

interface FormData {
  numeroDossier: string;
  civilite: string;
  nom: string;
  categorie: string;
  prenom: string;
  nomArtiste: string;
  prenomArtiste: string;
  adresse: string;
  codePostal: string;
  ville: string;
  pays: string;
  telephone: string;
  email: string;
  siteInternet: string;
  facebook: string;
  numeroMDA: string;
  numeroSIRET: string;
  editionAdresse: boolean;
  editionTelephone: boolean;
  editionEmail: boolean;
  editionSite: boolean;
  editionFacebook: boolean;
  nomCatalogue: string;
  oeuvres: ArtworkFields[];
}

const initialArtworkFields: ArtworkFields = {
  titre: '',
  technique: '',
  dimensions: '',
  prix: '',
  photo: null,
};

export default function ArtistSubmissionForm() {
  const [formData, setFormData] = useState<FormData>({
    numeroDossier: '',
    civilite: 'Madame',
    nom: '',
    categorie: '',
    prenom: '',
    nomArtiste: '',
    prenomArtiste: '',
    adresse: '',
    codePostal: '',
    ville: '',
    pays: '',
    telephone: '',
    email: '',
    siteInternet: '',
    facebook: '',
    numeroMDA: '',
    numeroSIRET: '',
    editionAdresse: false,
    editionTelephone: false,
    editionEmail: false,
    editionSite: false,
    editionFacebook: false,
    nomCatalogue: '',
    oeuvres: Array(10).fill(null).map(() => ({ ...initialArtworkFields })),
  });

  const [submitStatus, setSubmitStatus] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: checked,
    }));
  };

  const handleArtworkChange = (index: number, field: keyof ArtworkFields, value: string | File | null) => {
    setFormData((prev) => {
      const newOeuvres = [...prev.oeuvres];
      newOeuvres[index] = {
        ...newOeuvres[index],
        [field]: value,
      };
      return {
        ...prev,
        oeuvres: newOeuvres,
      };
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const formDataToSend = new FormData();
      
      // Ajouter les données de l'artiste
      Object.entries(formData).forEach(([key, value]) => {
        if (key !== 'oeuvres') {
          formDataToSend.append(key, value.toString());
        }
      });

      // Ajouter les œuvres
      formData.oeuvres.forEach((oeuvre, index) => {
        if (oeuvre.titre) {
          Object.entries(oeuvre).forEach(([key, value]) => {
            if (key === 'photo' && value) {
              formDataToSend.append(`oeuvre${index + 1}_photo`, value);
            } else {
              formDataToSend.append(`oeuvre${index + 1}_${key}`, value.toString());
            }
          });
        }
      });

      const response = await fetch('/api/submit-artwork', {
        method: 'POST',
        body: formDataToSend,
      });

      const result = await response.json();

      if (response.ok) {
        setSubmitStatus({
          success: true,
          message: 'Votre dossier a été soumis avec succès. Un email de confirmation vous a été envoyé.',
        });
      } else {
        throw new Error(result.message || 'Une erreur est survenue');
      }
    } catch (error) {
      setSubmitStatus({
        success: false,
        message: error instanceof Error ? error.message : 'Une erreur est survenue',
      });
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Formulaire d'Inscription
        </Typography>

        {submitStatus && (
          <Alert severity={submitStatus.success ? 'success' : 'error'} sx={{ mb: 3 }}>
            {submitStatus.message}
          </Alert>
        )}

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          Numéro de Dossier
        </Typography>
        <TextField
          fullWidth
          name="numeroDossier"
          label="Numéro de dossier"
          value={formData.numeroDossier}
          onChange={handleInputChange}
          sx={{ mb: 3 }}
        />

        <Typography variant="h6" gutterBottom>
          Coordonnées Personnelles
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <FormControl component="fieldset">
              <RadioGroup
                row
                name="civilite"
                value={formData.civilite}
                onChange={handleInputChange}
              >
                <FormControlLabel value="Madame" control={<Radio />} label="Madame" />
                <FormControlLabel value="Mademoiselle" control={<Radio />} label="Mademoiselle" />
                <FormControlLabel value="Monsieur" control={<Radio />} label="Monsieur" />
              </RadioGroup>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="nom"
              label="Nom"
              value={formData.nom}
              onChange={handleInputChange}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="categorie"
              label="Catégorie"
              value={formData.categorie}
              onChange={handleInputChange}
            />
          </Grid>

          {/* Autres champs personnels */}
          {[
            { name: 'prenom', label: 'Prénom' },
            { name: 'nomArtiste', label: 'Nom Artiste' },
            { name: 'prenomArtiste', label: 'Prénom Artiste' },
            { name: 'adresse', label: 'Adresse' },
            { name: 'codePostal', label: 'Code Postal' },
            { name: 'ville', label: 'Ville' },
            { name: 'pays', label: 'Pays' },
            { name: 'telephone', label: 'Téléphone Mobile' },
            { name: 'email', label: 'Email' },
            { name: 'siteInternet', label: 'Site Internet' },
            { name: 'facebook', label: 'Facebook/Autres' },
            { name: 'numeroMDA', label: 'Numéro MDA' },
            { name: 'numeroSIRET', label: 'Numéro SIRET' },
          ].map((field) => (
            <Grid item xs={12} sm={6} key={field.name}>
              <TextField
                fullWidth
                name={field.name}
                label={field.label}
                value={formData[field.name as keyof FormData]}
                onChange={handleInputChange}
              />
            </Grid>
          ))}
        </Grid>

        <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
          Edition sur le Catalogue et sur notre Site Internet
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              name="nomCatalogue"
              label="Nom à afficher sur le catalogue"
              value={formData.nomCatalogue}
              onChange={handleInputChange}
            />
          </Grid>
          {[
            { name: 'editionAdresse', label: 'Edition Adresse' },
            { name: 'editionTelephone', label: 'Edition Téléphone' },
            { name: 'editionEmail', label: 'Edition Email' },
            { name: 'editionSite', label: 'Edition Site Internet' },
            { name: 'editionFacebook', label: 'Edition Facebook/Autres' },
          ].map((field) => (
            <Grid item xs={12} sm={6} key={field.name}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData[field.name as keyof FormData] as boolean}
                    onChange={handleCheckboxChange}
                    name={field.name}
                  />
                }
                label={field.label}
              />
            </Grid>
          ))}
        </Grid>

        <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
          Œuvres à Exposer
        </Typography>
        {formData.oeuvres.map((oeuvre, index) => (
          <Paper key={index} elevation={1} sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Œuvre N°{index + 1}
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label={`Titre ${index + 1}`}
                  value={oeuvre.titre}
                  onChange={(e) => handleArtworkChange(index, 'titre', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Technique"
                  value={oeuvre.technique}
                  onChange={(e) => handleArtworkChange(index, 'technique', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Dimensions (L x H x P en cm)"
                  value={oeuvre.dimensions}
                  onChange={(e) => handleArtworkChange(index, 'dimensions', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Prix (euros)"
                  type="number"
                  value={oeuvre.prix}
                  onChange={(e) => handleArtworkChange(index, 'prix', e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <label htmlFor={`photo-${index}`}>
                  <Input
                    accept="image/*"
                    id={`photo-${index}`}
                    type="file"
                    onChange={(e) => {
                      const file = e.target.files?.[0] || null;
                      handleArtworkChange(index, 'photo', file);
                    }}
                  />
                  <Button variant="contained" component="span">
                    Télécharger Photo
                  </Button>
                </label>
                {oeuvre.photo && (
                  <Typography variant="body2" sx={{ ml: 2, display: 'inline' }}>
                    {oeuvre.photo.name}
                  </Typography>
                )}
              </Grid>
            </Grid>
          </Paper>
        ))}

        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            size="large"
          >
            Envoyer le Dossier
          </Button>
        </Box>
      </Paper>
    </Box>
  );
}
