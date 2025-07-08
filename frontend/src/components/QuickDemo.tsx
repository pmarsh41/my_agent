import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  Card, 
  CardContent, 
  Typography, 
  Alert,
  Grid,
  Chip
} from '@mui/material';
import { PlayArrow, Restaurant } from '@mui/icons-material';
import axios from 'axios';

const QuickDemo: React.FC = () => {
  const [demoResult, setDemoResult] = useState<any>(null);
  const [isRunning, setIsRunning] = useState(false);

  const runDemo = async () => {
    setIsRunning(true);
    
    // Simulate a smart analysis result for demo purposes
    const mockResult = {
      success: true,
      conversation_response: "Here's what I can see in your meal:\n\n1. **Grilled Chicken Breast** - 5oz serving\n   🥩 Estimated protein: 38.8g\n   ✅ Very confident about this one\n   💭 Based on the visual size, this looks like 5oz serving (150g). I can see: white meat, grill marks visible, lean appearance. I'm very confident about this identification.\n\n2. **Steamed Broccoli** - 1 cup\n   🥩 Estimated protein: 4.2g\n   👍 Pretty sure about this\n   💭 Based on the visual size, this looks like 1 cup (150g). I can see: green florets, tree-like structure, stems. I'm fairly confident about this identification.\n\n**Total estimated protein: 43.0g**\n\nDoes this look accurate? You can adjust any portions that seem off!",
      identified_foods: [
        {
          name: "grilled chicken breast",
          confidence: 9,
          visual_cues: "white meat, grill marks visible, lean appearance",
          estimated_size: "medium",
          preparation: "grilled"
        },
        {
          name: "steamed broccoli",
          confidence: 8,
          visual_cues: "green florets, tree-like structure, stems",
          estimated_size: "medium",
          preparation: "steamed"
        }
      ],
      portion_suggestions: [
        {
          food_name: "Chicken Breast",
          food_id: "chicken_breast",
          suggested_portion: "medium",
          portion_details: {
            grams: 150,
            description: "5oz serving"
          },
          protein_estimate: {
            protein_grams: 38.8,
            food_name: "Chicken Breast",
            portion_description: "5oz serving"
          },
          alternative_portions: {
            small: { grams: 120, description: "4oz serving" },
            large: { grams: 180, description: "6oz serving" },
            extra_large: { grams: 240, description: "8oz serving" }
          },
          confidence: 9,
          explanation: "Based on the visual size, this looks like 5oz serving (150g). I can see: white meat, grill marks visible, lean appearance. I'm very confident about this identification.",
          visual_reasoning: "white meat, grill marks visible, lean appearance",
          preparation: "grilled"
        },
        {
          food_name: "Broccoli",
          food_id: "broccoli",
          suggested_portion: "medium",
          portion_details: {
            grams: 150,
            description: "1 cup"
          },
          protein_estimate: {
            protein_grams: 4.2,
            food_name: "Broccoli",
            portion_description: "1 cup"
          },
          alternative_portions: {
            small: { grams: 80, description: "1/2 cup" },
            large: { grams: 200, description: "1.5 cups" }
          },
          confidence: 8,
          explanation: "Based on the visual size, this looks like 1 cup (150g). I can see: green florets, tree-like structure, stems. I'm fairly confident about this identification.",
          visual_reasoning: "green florets, tree-like structure, stems",
          preparation: "steamed"
        }
      ],
      unmatched_foods: [],
      total_protein_estimate: 43.0,
      confidence_level: "I'm very confident about these identifications",
      requires_user_input: false
    };

    // Simulate API delay
    setTimeout(() => {
      setDemoResult(mockResult);
      setIsRunning(false);
    }, 2000);
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 8) return 'success';
    if (confidence >= 6) return 'warning';
    return 'error';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 8) return 'Very Confident';
    if (confidence >= 6) return 'Fairly Confident';
    return 'Less Certain';
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
      <Typography variant="h5" gutterBottom sx={{ textAlign: 'center', mb: 3 }}>
        🚀 Smart Analysis Demo
      </Typography>
      
      <Typography variant="body1" sx={{ textAlign: 'center', mb: 3, color: 'text.secondary' }}>
        See how the smart meal analyzer identifies foods and estimates portions with AI assistance
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ textAlign: 'center' }}>
          {!demoResult && (
            <>
              <Typography variant="h6" gutterBottom>
                📸 Sample Meal: Grilled Chicken & Broccoli
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Click below to see how the AI analyzes this meal
              </Typography>
              <Button
                variant="contained"
                size="large"
                onClick={runDemo}
                disabled={isRunning}
                startIcon={<PlayArrow />}
              >
                {isRunning ? 'Analyzing...' : 'Run Smart Analysis Demo'}
              </Button>
            </>
          )}
          
          {isRunning && (
            <Box>
              <Typography variant="body2" sx={{ mb: 2 }}>
                🔍 AI is analyzing the meal...
              </Typography>
              <Typography variant="caption" color="text.secondary">
                • Identifying foods with confidence scores<br/>
                • Matching to nutrition database<br/>
                • Estimating portions with visual reasoning<br/>
                • Generating conversational response
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {demoResult && (
        <>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>🤖 AI Analysis Results</Typography>
              <Alert severity="success" sx={{ mb: 2 }}>
                {demoResult.conversation_response.split('\n\n')[0]}
              </Alert>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                <Chip 
                  label={`${demoResult.portion_suggestions.length} foods identified`}
                  color="primary"
                  icon={<Restaurant />}
                />
                <Chip 
                  label={`${demoResult.total_protein_estimate.toFixed(1)}g protein`}
                  color="secondary"
                />
                <Chip 
                  label={demoResult.confidence_level}
                  color="success"
                />
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>🔍 Detailed Analysis</Typography>
              
              {demoResult.portion_suggestions.map((suggestion: any, index: number) => (
                <Card key={index} variant="outlined" sx={{ mb: 2, p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Typography variant="h6" sx={{ flexGrow: 1 }}>
                      {suggestion.food_name}
                    </Typography>
                    <Chip 
                      label={`${suggestion.protein_estimate.protein_grams.toFixed(1)}g protein`}
                      size="small"
                      color="secondary"
                      sx={{ mr: 1 }}
                    />
                    <Chip 
                      label={getConfidenceLabel(suggestion.confidence)}
                      size="small"
                      color={getConfidenceColor(suggestion.confidence)}
                    />
                  </Box>
                  
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Portion:</strong> {suggestion.portion_details.description} ({suggestion.portion_details.grams}g)
                  </Typography>
                  
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Preparation:</strong> {suggestion.preparation}
                  </Typography>
                  
                  <Typography variant="body2" sx={{ fontStyle: 'italic', color: 'text.secondary' }}>
                    💭 {suggestion.explanation}
                  </Typography>
                </Card>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>✨ Key Features Demonstrated</Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2 }}>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>🎯 Realistic Approach</Typography>
                  <Typography variant="body2" color="text.secondary">
                    No magic numbers - AI identifies foods and suggests portions for user confirmation
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>🤖 Confidence Scoring</Typography>
                  <Typography variant="body2" color="text.secondary">
                    AI tells you when it's certain vs. uncertain about identifications
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>👁️ Visual Reasoning</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Explains what visual cues led to food identification
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>💬 Conversational</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Friendly, helpful communication instead of robotic responses
                  </Typography>
                </Box>
              </Box>
              
              <Button
                variant="outlined"
                onClick={() => setDemoResult(null)}
                sx={{ mt: 2 }}
              >
                Run Demo Again
              </Button>
            </CardContent>
          </Card>
        </>
      )}
    </Box>
  );
};

export default QuickDemo;