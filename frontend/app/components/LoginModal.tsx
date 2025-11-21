/**
 * Login Modal Component
 *
 * Shows a modal with Google sign-in and email/password options.
 * Appears when user tries to generate a cheat sheet without being logged in.
 */

'use client';

import { useState } from 'react';
import { X, LogIn } from 'lucide-react';
import { signInWithGoogle, signInWithEmail, signUpWithEmail } from '../auth/firebase';

interface LoginModalProps {
  isOpen: boolean;           // Controls whether modal is visible
  onClose: () => void;       // Called when user closes modal
  onSuccess: () => void;     // Called after successful login
}

export default function LoginModal({ isOpen, onClose, onSuccess }: LoginModalProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);  // Toggle between login/signup
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Don't render anything if modal is closed
  if (!isOpen) return null;

  // Convert Firebase error codes to user-friendly messages
  const getFriendlyErrorMessage = (errorMessage: string): string => {
    if (errorMessage.includes('auth/invalid-credential')) {
      return 'Invalid email or password. Please try again.';
    }
    if (errorMessage.includes('auth/user-not-found')) {
      return 'No account found with this email.';
    }
    if (errorMessage.includes('auth/wrong-password')) {
      return 'Incorrect password. Please try again.';
    }
    if (errorMessage.includes('auth/email-already-in-use')) {
      return 'This email is already registered. Try signing in instead.';
    }
    if (errorMessage.includes('auth/weak-password')) {
      return 'Password should be at least 6 characters.';
    }
    if (errorMessage.includes('auth/invalid-email')) {
      return 'Please enter a valid email address.';
    }
    if (errorMessage.includes('auth/popup-closed-by-user')) {
      return 'Sign-in cancelled. Please try again.';
    }
    // Generic fallback
    return 'Sign-in failed. Please try again.';
  };

  // Handle Google Sign-In
  const handleGoogleSignIn = async () => {
    setLoading(true);
    setError(null);

    const { user, error } = await signInWithGoogle();

    if (error) {
      setError(getFriendlyErrorMessage(error));
      setLoading(false);
    } else if (user) {
      onSuccess();  // Login successful, close modal and proceed
    }
  };

  // Handle Email/Password Login or Sign-Up
  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Choose sign-in or sign-up based on toggle
    const { user, error } = isSignUp
      ? await signUpWithEmail(email, password)
      : await signInWithEmail(email, password);

    if (error) {
      setError(getFriendlyErrorMessage(error));
      setLoading(false);
    } else if (user) {
      onSuccess();  // Login successful, close modal and proceed
    }
  };

  return (
    // Modal backdrop - semi-transparent overlay that covers entire screen
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      {/* Modal content */}
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 p-8 relative">

        {/* Close button (X in top-right corner) */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
        >
          <X className="w-6 h-6" />
        </button>

        {/* Header */}
        <div className="text-center mb-6">
          <LogIn className="w-12 h-12 text-blue-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900">
            Sign in to continue
          </h2>
          <p className="text-gray-600 mt-2">
            Create an account or sign in to generate your cheat sheet
          </p>
        </div>

        {/* Error message - only shows if there's an error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        {/* Google Sign-In Button */}
        <button
          onClick={handleGoogleSignIn}
          disabled={loading}
          className="w-full bg-white border-2 border-gray-300 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-all flex items-center justify-center gap-3 mb-4"
        >
          {/* Google logo SVG */}
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Continue with Google
        </button>

        {/* Divider with "or" text */}
        <div className="flex items-center gap-4 mb-4">
          <div className="flex-1 border-t border-gray-300"></div>
          <span className="text-gray-500 text-sm">or</span>
          <div className="flex-1 border-t border-gray-300"></div>
        </div>

        {/* Email/Password Form */}
        <form onSubmit={handleEmailAuth} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••"
            />
          </div>

          {/* Submit button - text changes based on sign-in vs sign-up */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition-all"
          >
            {loading ? 'Processing...' : (isSignUp ? 'Sign Up' : 'Sign In')}
          </button>
        </form>

        {/* Toggle between Sign In and Sign Up */}
        <div className="text-center mt-4">
          <button
            onClick={() => {
              setIsSignUp(!isSignUp);
              setError(null);
            }}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            {isSignUp ? 'Already have an account? Sign in' : "Don't have an account? Sign up"}
          </button>
        </div>
      </div>
    </div>
  );
}
