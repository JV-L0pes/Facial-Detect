// User types
export interface User {
  id: number;
  name: string;
  email: string;
  passage_count: number;
  created_at: string;
  is_active: boolean;
}

// Access Log types
export interface AccessLog {
  id: number;
  user_id?: number;
  user_name?: string;
  confidence?: number;
  access_granted: boolean;
  liveness_passed: boolean;
  timestamp: string;
  ip_address?: string;
  error_message?: string;
}

// Stats types
export interface SystemStats {
  total_users: number;
  total_logs: number;
  successful_access: number;
  success_rate: number;
  face_recognition: {
    device: string;
    model_loaded: boolean;
    index_size: number;
  };
}

export interface PassageStats {
  total_passages: number;
  total_users: number;
  average_passages: number;
  most_active_user?: {
    name: string;
    passage_count: number;
  };
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
}

export interface UsersResponse extends ApiResponse {
  users: User[];
}

export interface LogsResponse extends ApiResponse {
  logs: AccessLog[];
}

export interface StatsResponse extends ApiResponse {
  stats: SystemStats;
}

export interface PassageStatsResponse extends ApiResponse {
  stats: PassageStats;
}

// Validation types
export interface ValidationRequest {
  image: string; // base64 encoded image
}

export interface ValidationResponse extends ApiResponse {
  access_granted: boolean;
  liveness_passed: boolean;
  confidence: number;
  user_id?: number;
  user_name?: string;
  passage_count?: number;
}

// Register types
export interface RegisterRequest {
  name: string;
  email: string;
  photo: File;
}

export interface RegisterResponse extends ApiResponse {
  user_id: number;
}

// Webcam types
export interface WebcamState {
  isActive: boolean;
  stream: MediaStream | null;
  error: string | null;
}

// Store types
export interface AppState {
  // Webcam state
  webcam: WebcamState;
  
  // UI state
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setWebcamActive: (active: boolean) => void;
  setWebcamStream: (stream: MediaStream | null) => void;
  setWebcamError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

// Form types
export interface RegisterFormData {
  name: string;
  email: string;
  photo: File | null;
}

// Component props types
export interface StatsCardProps {
  icon: React.ReactNode;
  title: string;
  value: string | number;
  description?: string;
  trend?: 'up' | 'down' | 'neutral';
}

export interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  gradient?: string;
}

export interface ValidationStatusProps {
  status: 'waiting' | 'processing' | 'success' | 'error';
  user?: string;
  confidence?: number;
  liveness?: boolean;
  passageCount?: number;
}
