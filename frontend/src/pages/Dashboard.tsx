import React, { useState, useEffect } from 'react';
import { Plus, TrendingUp, Target, AlertCircle, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

interface DailySummary {
  id: number;
  user_id: number;
  date: string;
  total_protein: number;
  goal: number;
  status: 'on_track' | 'met' | 'missed';
}

interface User {
  id: number;
  name: string;
  email: string;
  weight: number;
  age: number;
  activity_level: string;
  protein_goal: number;
}

const Dashboard: React.FC = () => {
  const [dailySummary, setDailySummary] = useState<DailySummary | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAddMeal, setShowAddMeal] = useState(false);
  const [mealForm, setMealForm] = useState({
    image_file: null as File | null,
    protein_estimate: '',
    foods_detected: '',
  });
  const [uploadingImage, setUploadingImage] = useState(false);
  const [analyzingImage, setAnalyzingImage] = useState(false);
  const [addingMeal, setAddingMeal] = useState(false);
  const fileInputRef = React.useRef<HTMLInputElement | null>(null);
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    // Mock data for now - replace with actual API calls
    const mockUser: User = {
      id: 1,
      name: "John Doe",
      email: "john@example.com",
      weight: 70,
      age: 30,
      activity_level: "moderate",
      protein_goal: 84
    };

    const mockSummary: DailySummary = {
      id: 1,
      user_id: 1,
      date: new Date().toISOString().split('T')[0],
      total_protein: 65,
      goal: 84,
      status: 'on_track'
    };

    setUser(mockUser);
    setDailySummary(mockSummary);
    setLoading(false);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'met':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'on_track':
        return <TrendingUp className="w-6 h-6 text-blue-500" />;
      case 'missed':
        return <AlertCircle className="w-6 h-6 text-red-500" />;
      default:
        return <Target className="w-6 h-6 text-gray-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'met':
        return 'Goal Met!';
      case 'on_track':
        return 'On Track';
      case 'missed':
        return 'Goal Missed';
      default:
        return 'Unknown';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'met':
        return 'text-green-600 bg-green-50';
      case 'on_track':
        return 'text-blue-600 bg-blue-50';
      case 'missed':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const progressPercentage = dailySummary ? (dailySummary.total_protein / dailySummary.goal) * 100 : 0;

  const handleImageChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setMealForm(f => ({ ...f, image_file: file }));
      // Analyze the image for protein estimate
      setAnalyzingImage(true);
      try {
        const formData = new FormData();
        formData.append('file', file);
        const res = await axios.post('/analyze-meal/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        if (res.data && typeof res.data.protein_estimate === 'number') {
          setMealForm(f => ({
            ...f,
            protein_estimate: res.data.protein_estimate.toString(),
            foods_detected: res.data.foods_detected ? res.data.foods_detected.join(', ') : ''
          }));
          toast.success('Protein estimate auto-filled!');
        } else {
          toast('Could not estimate protein from photo. Please enter manually.');
        }
      } catch (err) {
        toast.error('Image analysis failed. Please enter protein manually.');
      } finally {
        setAnalyzingImage(false);
      }
    }
  };

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await handleImageChange({ target: { files: e.dataTransfer.files } } as any);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleAddMeal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    setAddingMeal(true);
    let imageUrl = '';
    try {
      if (mealForm.image_file) {
        setUploadingImage(true);
        const formData = new FormData();
        formData.append('file', mealForm.image_file);
        const uploadRes = await axios.post('/upload/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        imageUrl = uploadRes.data.url;
        setUploadingImage(false);
      }
      const payload = {
        user_id: user.id,
        image_url: imageUrl,
        protein_estimate: parseFloat(mealForm.protein_estimate),
        foods_detected: mealForm.foods_detected.split(',').map(f => f.trim()).filter(f => f).join(', '),
        manual_adjustment: null,
      };
      await axios.post('/meals/', payload);
      toast.success('Meal added!');
      setShowAddMeal(false);
      setMealForm({ image_file: null, protein_estimate: '', foods_detected: '' });
      setDailySummary((prev) => prev ? {
        ...prev,
        total_protein: prev.total_protein + payload.protein_estimate
      } : prev);
    } catch (err) {
      toast.error('Failed to add meal');
    } finally {
      setAddingMeal(false);
      setUploadingImage(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Add Meal Modal */}
      {showAddMeal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
          <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">Add Meal</h2>
            <form onSubmit={handleAddMeal} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Meal Photo</label>
                <div
                  className={`w-full border-2 border-dashed rounded px-3 py-6 text-center cursor-pointer transition-colors ${dragActive ? 'border-primary bg-blue-50' : 'border-gray-300 bg-white'}`}
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onClick={() => fileInputRef.current?.click()}
                  style={{ position: 'relative' }}
                >
                  <input
                    type="file"
                    accept="image/*"
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    ref={fileInputRef}
                    onChange={handleImageChange}
                    required
                    disabled={analyzingImage}
                    tabIndex={-1}
                  />
                  <span className="block text-gray-500">{mealForm.image_file ? mealForm.image_file.name : 'Drag & drop or click to select a photo'}</span>
                  {analyzingImage && <div className="text-xs text-blue-600 mt-1">Analyzing photo...</div>}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Protein Estimate (g)</label>
                <input
                  type="number"
                  className="w-full border rounded px-3 py-2"
                  value={mealForm.protein_estimate}
                  onChange={e => setMealForm(f => ({ ...f, protein_estimate: e.target.value }))}
                  required
                  min="0"
                  step="0.1"
                  disabled={analyzingImage}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Foods Detected</label>
                <input
                  type="text"
                  className="w-full border rounded px-3 py-2"
                  value={mealForm.foods_detected}
                  onChange={e => setMealForm(f => ({ ...f, foods_detected: e.target.value }))}
                  required
                  disabled={analyzingImage}
                />
              </div>
              <div className="flex justify-end space-x-2 mt-4">
                <button type="button" className="px-4 py-2 rounded bg-gray-200" onClick={() => setShowAddMeal(false)} disabled={addingMeal || uploadingImage || analyzingImage}>Cancel</button>
                <button type="submit" className="px-4 py-2 rounded bg-primary text-white" disabled={addingMeal || uploadingImage || analyzingImage}>{addingMeal || uploadingImage || analyzingImage ? 'Adding...' : 'Add Meal'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-text">Welcome back, {user?.name}!</h1>
        <p className="text-gray-600 mt-2">Track your protein intake and stay on target</p>
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <button 
          onClick={() => setShowAddMeal(true)}
          className="inline-flex items-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
        >
          <Plus className="w-5 h-5 mr-2" />
          Add Meal
        </button>
      </div>

      {/* Daily Summary Card */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-text">Today's Progress</h2>
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(dailySummary?.status || '')}`}>
            {getStatusIcon(dailySummary?.status || '')}
            <span>{getStatusText(dailySummary?.status || '')}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-primary">{dailySummary?.total_protein}g</div>
            <div className="text-sm text-gray-600">Protein Consumed</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-text">{dailySummary?.goal}g</div>
            <div className="text-sm text-gray-600">Daily Goal</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-secondary">
              {dailySummary ? Math.max(0, dailySummary.goal - dailySummary.total_protein) : 0}g
            </div>
            <div className="text-sm text-gray-600">Remaining</div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{Math.round(progressPercentage)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-primary h-3 rounded-full transition-all duration-300"
              style={{ width: `${Math.min(100, progressPercentage)}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Target className="w-6 h-6 text-primary" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Weekly Goal</p>
              <p className="text-2xl font-bold text-text">588g</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-secondary" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Days Met</p>
              <p className="text-2xl font-bold text-text">5/7</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg Daily</p>
              <p className="text-2xl font-bold text-text">78g</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <AlertCircle className="w-6 h-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Streak</p>
              <p className="text-2xl font-bold text-text">3 days</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 