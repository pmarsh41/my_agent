import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  Card, 
  CardContent, 
  Typography, 
  Alert, 
  LinearProgress,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  Paper,
  Divider,
  Tabs,
  Tab
} from '@mui/material';
import { 
  CloudUpload, 
  PhotoCamera, 
  ExpandMore,
  Restaurant,
  Scale,
  PlayArrow
} from '@mui/icons-material';
import axios from 'axios';
import QuickDemo from './QuickDemo';

interface PortionSuggestion {
  food_name: string;
  food_id: string;
  suggested_portion: string;
  portion_details: {
    grams: number;
    description: string;
  };
  protein_estimate: {
    protein_grams: number;
    food_name: string;
    portion_description: string;
  };
  alternative_portions: Record<string, { grams: number; description: string }>;
  confidence: number;
  explanation: string;
  visual_reasoning: string;
  preparation: string;
}

interface SmartAnalysisResponse {
  success: boolean;
  conversation_response: string;
  identified_foods: any[];
  portion_suggestions: PortionSuggestion[];
  unmatched_foods: any[];
  total_protein_estimate: number;
  confidence_level: string;
  requires_user_input: boolean;
}

/**
 * SmartMealAnalyzer - Main component for AI-powered meal analysis
 * 
 * This component provides a comprehensive interface for analyzing meal images
 * using OpenAI Vision API and LangGraph workflows. It handles image upload,
 * AI analysis, portion adjustment, and meal confirmation.
 * 
 * Features:
 * - Image upload and preview
 * - AI-powered food identification
 * - Interactive portion size adjustment
 * - Protein calculation and tracking
 * - Meal confirmation and logging
 * 
 * @returns {JSX.Element} The SmartMealAnalyzer component
 */
const SmartMealAnalyzer: React.FC = () => {
  // Tab state for switching between analysis and demo modes
  const [tabValue, setTabValue] = useState(0);
  
  // File upload and preview state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  
  // Analysis state
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<SmartAnalysisResponse | null>(null);
  
  // Portion confirmation state
  const [confirmedPortions, setConfirmedPortions] = useState<any[]>([]);
  const [isConfirming, setIsConfirming] = useState(false);

  /**
   * Handles tab changes between analysis and demo modes
   * @param {React.SyntheticEvent} event - The tab change event
   * @param {number} newValue - The new tab index
   */
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  /**
   * Handles file selection for image upload
   * Creates a preview of the selected image and resets analysis state
   * @param {React.ChangeEvent<HTMLInputElement>} event - File input change event
   */
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setAnalysisResult(null);
      setConfirmedPortions([]);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  /**
   * Analyzes the selected image using the smart meal analysis API
   * Sends the image to the backend for AI-powered food identification
   * and portion estimation using LangGraph workflows
   */
  const analyzeImage = async () => {
    if (!selectedFile) return;
    
    setIsAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      // Send image to backend for AI analysis using LangGraph workflow
      const response = await axios.post('/analyze-meal-smart/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        params: { user_id: 1 } // Demo user ID
      });
      
      const result = response.data as SmartAnalysisResponse;
      setAnalysisResult(result);
      
      // Initialize confirmed portions with suggested values
      if (result.portion_suggestions) {
        setConfirmedPortions(result.portion_suggestions.map(suggestion => ({
          food_id: suggestion.food_id,
          food_name: suggestion.food_name,
          selected_portion: suggestion.suggested_portion,
          protein_grams: suggestion.protein_estimate.protein_grams,
          portion_description: suggestion.portion_details.description
        })));
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      setAnalysisResult({
        success: false,
        conversation_response: "Sorry, I couldn't analyze this image. Please try again or enter your meal manually.",
        identified_foods: [],
        portion_suggestions: [],
        unmatched_foods: [],
        total_protein_estimate: 0,
        confidence_level: "error",
        requires_user_input: true
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  /**
   * Updates portion size for a specific food item and recalculates protein
   * @param {number} foodIndex - Index of the food in the portion suggestions
   * @param {string} newPortion - New portion size (small/medium/large)
   */
  const updatePortionSize = (foodIndex: number, newPortion: string) => {
    if (!analysisResult) return;
    
    const suggestion = analysisResult.portion_suggestions[foodIndex];
    const newPortionDetails = suggestion.alternative_portions[newPortion] || suggestion.portion_details;
    
    // Recalculate protein based on new portion size
    const proteinPer100g = suggestion.protein_estimate.protein_grams / (suggestion.portion_details.grams / 100);
    const newProtein = (proteinPer100g * newPortionDetails.grams / 100);
    
    const updatedPortions = [...confirmedPortions];
    updatedPortions[foodIndex] = {
      ...updatedPortions[foodIndex],
      selected_portion: newPortion,
      protein_grams: newProtein,
      portion_description: newPortionDetails.description
    };
    
    setConfirmedPortions(updatedPortions);
  };

  /**
   * Confirms the meal by sending confirmed portions to the backend
   * Logs the meal to the database and updates daily protein tracking
   */
  const confirmMeal = async () => {
    if (!confirmedPortions.length) return;
    
    setIsConfirming(true);
    try {
      // Send confirmed portions to backend for meal logging
      const response = await axios.post('/confirm-meal-portions/', {
        user_id: 1,
        confirmed_portions: confirmedPortions
      });
      
      alert(`Meal logged successfully! Total protein: ${response.data.total_protein.toFixed(1)}g`);
      
      // Reset for next meal
      setSelectedFile(null);
      setImagePreview(null);
      setAnalysisResult(null);
      setConfirmedPortions([]);
    } catch (error) {
      console.error('Meal confirmation failed:', error);
      alert('Failed to log meal. Please try again.');
    } finally {
      setIsConfirming(false);
    }
  };

  /**
   * Gets the appropriate color for confidence level display
   * @param {number} confidence - Confidence score (1-10)
   * @returns {string} Material-UI color name
   */
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 8) return 'success';
    if (confidence >= 6) return 'warning';
    return 'error';
  };

  /**
   * Gets a human-readable label for confidence level
   * @param {number} confidence - Confidence score (1-10)
   * @returns {string} Confidence level description
   */
  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 8) return 'Very Confident';
    if (confidence >= 6) return 'Fairly Confident';
    return 'Less Certain';
  };

  /**
   * Calculates total protein from all confirmed portions
   * @returns {number} Total protein in grams
   */
  const getTotalConfirmedProtein = () => {
    return confirmedPortions.reduce((total, portion) => total + portion.protein_grams, 0);
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ textAlign: 'center', mb: 2 }}>
        🍽️ Smart Meal Analyzer
      </Typography>
      
      <Typography variant="subtitle1" sx={{ textAlign: 'center', mb: 4, color: 'text.secondary' }}>
        AI-assisted food identification and portion estimation
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange} centered>
          <Tab label="📸 Upload Photo" icon={<PhotoCamera />} />
          <Tab label="🚀 Try Demo" icon={<PlayArrow />} />
        </Tabs>
      </Box>

      {tabValue === 0 && (
        <Box>
          {/* File Upload Section */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ textAlign: 'center' }}>
                <input
                  accept="image/*"
                  style={{ display: 'none' }}
                  id="photo-upload"
                  type="file"
                  onChange={handleFileSelect}
                />
                <label htmlFor="photo-upload">
                  <Button
                    variant="outlined"
                    component="span"
                    startIcon={<PhotoCamera />}
                    sx={{ mr: 2 }}
                  >
                    Choose Photo
                  </Button>
                </label>
                
                {selectedFile && (
                  <Button
                    variant="contained"
                    onClick={analyzeImage}
                    disabled={isAnalyzing}
                    startIcon={<CloudUpload />}
                  >
                    {isAnalyzing ? 'Analyzing...' : 'Analyze Meal'}
                  </Button>
                )}
              </Box>
              
              {isAnalyzing && (
                <Box sx={{ mt: 2 }}>
                  <LinearProgress />
                  <Typography variant="body2" sx={{ textAlign: 'center', mt: 1 }}>
                    🔍 Identifying foods and estimating portions...
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>

          {/* Image Preview */}
          {imagePreview && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>📸 Your Meal Photo</Typography>
                <Box sx={{ textAlign: 'center' }}>
                  <img 
                    src={imagePreview} 
                    alt="Meal preview" 
                    style={{ maxWidth: '100%', maxHeight: '300px', borderRadius: '8px' }}
                  />
                </Box>
              </CardContent>
            </Card>
          )}

          {/* Analysis Results */}
          {analysisResult && (
            <React.Fragment>
              {/* Conversational Response */}
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>🤖 Analysis Results</Typography>
                  <Alert 
                    severity={analysisResult.success ? "info" : "warning"}
                    sx={{ mb: 2 }}
                  >
                    {analysisResult.conversation_response}
                  </Alert>
                  
                  {analysisResult.success && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                      <Chip 
                        label={`${analysisResult.portion_suggestions.length} foods identified`}
                        color="primary"
                        icon={<Restaurant />}
                      />
                      <Chip 
                        label={`${analysisResult.total_protein_estimate.toFixed(1)}g protein`}
                        color="secondary"
                        icon={<Scale />}
                      />
                      <Chip 
                        label={analysisResult.confidence_level}
                        color={analysisResult.confidence_level.includes('confident') ? 'success' : 'warning'}
                      />
                    </Box>
                  )}
                </CardContent>
              </Card>

              {/* Portion Suggestions */}
              {analysisResult.portion_suggestions.length > 0 && (
                <Card sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>🍽️ Adjust Portions</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Review and adjust the portion sizes below. The protein estimates will update automatically.
                    </Typography>
                    
                    {analysisResult.portion_suggestions.map((suggestion, index) => (
                      <Accordion key={index} sx={{ mb: 1 }}>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                            <Typography sx={{ flexGrow: 1 }}>
                              <strong>{suggestion.food_name}</strong> - {confirmedPortions[index]?.portion_description}
                            </Typography>
                            <Chip 
                              label={`${confirmedPortions[index]?.protein_grams.toFixed(1)}g protein`}
                              size="small"
                              color="secondary"
                              sx={{ mr: 2 }}
                            />
                            <Chip 
                              label={getConfidenceLabel(suggestion.confidence)}
                              size="small"
                              color={getConfidenceColor(suggestion.confidence)}
                            />
                          </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Typography variant="body2" sx={{ mb: 2, fontStyle: 'italic' }}>
                            💭 {suggestion.explanation}
                          </Typography>
                          
                          <Typography variant="subtitle2" gutterBottom>Portion Size:</Typography>
                          <Grid container spacing={1} sx={{ mb: 2 }}>
                            {Object.entries({
                              [suggestion.suggested_portion]: suggestion.portion_details,
                              ...suggestion.alternative_portions
                            }).map(([portionKey, portionData]) => (
                              <Grid key={portionKey}>
                                <Button
                                  variant={confirmedPortions[index]?.selected_portion === portionKey ? 'contained' : 'outlined'}
                                  size="small"
                                  onClick={() => updatePortionSize(index, portionKey)}
                                >
                                  {portionData.description}
                                </Button>
                              </Grid>
                            ))}
                          </Grid>
                          
                          {suggestion.visual_reasoning && (
                            <Typography variant="body2" color="text.secondary">
                              👁️ <strong>What I see:</strong> {suggestion.visual_reasoning}
                            </Typography>
                          )}
                        </AccordionDetails>
                      </Accordion>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Final Confirmation */}
              {confirmedPortions.length > 0 && (
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>✅ Confirm & Log Meal</Typography>
                    
                    <Paper sx={{ p: 2, bgcolor: 'grey.50', mb: 2 }}>
                      <Typography variant="h4" sx={{ textAlign: 'center', color: 'primary.main' }}>
                        {getTotalConfirmedProtein().toFixed(1)}g
                      </Typography>
                      <Typography variant="body2" sx={{ textAlign: 'center', color: 'text.secondary' }}>
                        Total Protein
                      </Typography>
                    </Paper>
                    
                    <Divider sx={{ my: 2 }} />
                    
                    <Typography variant="subtitle2" gutterBottom>Meal Summary:</Typography>
                    {confirmedPortions.map((portion, index) => (
                      <Typography key={index} variant="body2" sx={{ mb: 0.5 }}>
                        • {portion.food_name} ({portion.portion_description}) - {portion.protein_grams.toFixed(1)}g protein
                      </Typography>
                    ))}
                    
                    <Button
                      variant="contained"
                      size="large"
                      fullWidth
                      onClick={confirmMeal}
                      disabled={isConfirming}
                      sx={{ mt: 3 }}
                    >
                      {isConfirming ? 'Logging Meal...' : 'Log This Meal'}
                    </Button>
                  </CardContent>
                </Card>
              )}
            </React.Fragment>
          )}
        </Box>
      )}

      {tabValue === 1 && <QuickDemo />}
    </Box>
  );
};

export default SmartMealAnalyzer;