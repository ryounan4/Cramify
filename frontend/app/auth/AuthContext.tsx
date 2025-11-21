/**
 * Authentication Context
 *
 * This provides user authentication state to the entire app.
 * Any component can access the current user and check if they're logged in.
 */

'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { User } from 'firebase/auth';
import { onAuthChange } from './firebase';

interface AuthContextType {
  user: User | null;              // The current logged-in user (null if not logged in)
  loading: boolean;                // True while Firebase is checking if user is logged in
  getAuthToken: () => Promise<string | null>;  // Gets JWT token to send to backend
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  getAuthToken: async () => null,
});

export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Subscribe to Firebase auth state changes
    // This fires whenever user logs in or out
    const unsubscribe = onAuthChange((user) => {
      setUser(user);           // Update user state
      setLoading(false);       // Done checking
    });

    // Cleanup subscription when component unmounts
    return () => unsubscribe();
  }, []);

  // Gets the user's Firebase ID token (JWT)
  // This token proves to your backend that the user is who they say they are
  const getAuthToken = async (): Promise<string | null> => {
    if (user) {
      try {
        return await user.getIdToken();
      } catch (error) {
        console.error('Error getting auth token:', error);
        return null;
      }
    }
    return null;
  };

  const value = {
    user,
    loading,
    getAuthToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
