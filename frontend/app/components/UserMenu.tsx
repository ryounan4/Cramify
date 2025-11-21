/**
 * User Menu Component
 *
 * Displays "Sign In" button (if not logged in) or user info with logout button (if logged in)
 */

'use client';

import { User, LogOut, LogIn } from 'lucide-react';
import { useAuth } from '../auth/AuthContext';
import { signOut } from '../auth/firebase';

interface UserMenuProps {
  onSignInClick?: () => void;  // Called when user clicks "Sign In" button
}

export default function UserMenu({ onSignInClick }: UserMenuProps) {
  const { user } = useAuth();

  const handleLogout = async () => {
    await signOut();
  };

  // If user is NOT logged in, show "Sign In" button
  if (!user) {
    return (
      <button
        onClick={onSignInClick}
        className="flex items-center gap-2 bg-white/20 backdrop-blur-sm rounded-full px-4 py-2 hover:bg-white/30 transition-colors font-medium"
      >
        <LogIn className="w-5 h-5" />
        Sign In
      </button>
    );
  }

  // If user IS logged in, show user info and logout button
  const displayName = user.displayName || user.email || 'User';

  return (
    <div className="flex items-center gap-3 bg-white/20 backdrop-blur-sm rounded-full px-4 py-2">
      {/* User icon */}
      <User className="w-5 h-5" />

      {/* User name */}
      <span className="font-medium">{displayName}</span>

      {/* Logout button */}
      <button
        onClick={handleLogout}
        className="ml-2 p-2 hover:bg-white/20 rounded-full transition-colors"
        title="Log out"
      >
        <LogOut className="w-4 h-4" />
      </button>
    </div>
  );
}
