import { create } from 'zustand';

interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  phone?: string;
  preferences: {
    language: string;
    currency: string;
    interests: string[];
    budgetMin: number;
    budgetMax: number;
    transportation: string;
  };
  notifications: {
    planReminder: boolean;
    friendInvite: boolean;
    weatherAlert: boolean;
    promotions: boolean;
  };
  privacy: {
    publicProfile: boolean;
    shareItinerary: boolean;
  };
}

interface UserState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  setUser: (user: User) => void;
  updateUser: (updates: Partial<User>) => void;
  updatePreferences: (preferences: Partial<User['preferences']>) => void;
  updateNotifications: (notifications: Partial<User['notifications']>) => void;
  updatePrivacy: (privacy: Partial<User['privacy']>) => void;
  login: (user: User) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
}

export const useUserStore = create<UserState>((set, get) => ({
  user: {
    id: 'current_user',
    name: '我',
    email: 'user@example.com',
    avatar: '👨‍💼',
    phone: '138****8888',
    preferences: {
      language: 'zh-CN',
      currency: 'CNY',
      interests: ['文化', '美食', '自然'],
      budgetMin: 1000,
      budgetMax: 5000,
      transportation: 'mixed'
    },
    notifications: {
      planReminder: true,
      friendInvite: true,
      weatherAlert: true,
      promotions: false
    },
    privacy: {
      publicProfile: true,
      shareItinerary: true
    }
  },
  isAuthenticated: true,
  isLoading: false,

  setUser: (user) => set({ user, isAuthenticated: true }),
  
  updateUser: (updates) => set((state) => ({
    user: state.user ? { ...state.user, ...updates } : null
  })),
  
  updatePreferences: (preferences) => set((state) => ({
    user: state.user ? {
      ...state.user,
      preferences: { ...state.user.preferences, ...preferences }
    } : null
  })),
  
  updateNotifications: (notifications) => set((state) => ({
    user: state.user ? {
      ...state.user,
      notifications: { ...state.user.notifications, ...notifications }
    } : null
  })),
  
  updatePrivacy: (privacy) => set((state) => ({
    user: state.user ? {
      ...state.user,
      privacy: { ...state.user.privacy, ...privacy }
    } : null
  })),
  
  login: (user) => set({ user, isAuthenticated: true, isLoading: false }),
  
  logout: () => set({ user: null, isAuthenticated: false, isLoading: false }),
  
  setLoading: (isLoading) => set({ isLoading })
}));