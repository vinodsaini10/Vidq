import React, { useState } from 'react';
import { Search, Bell, Shield, User, LogOut, AlertTriangle, X } from 'lucide-react';
import { useAppState } from '../../store/useStore';

interface AdminHeaderProps {
  onSearch: (term: string) => void;
  impersonatedUser: any;
  onExitImpersonation: () => void;
}

export const AdminHeader: React.FC<AdminHeaderProps> = ({
  onSearch,
  impersonatedUser,
  onExitImpersonation
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const { userProfile } = useAppState();

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    onSearch(e.target.value);
  };

  return (
    <div className="space-y-3">
      {/* Impersonation Banner if Active */}
      {impersonatedUser && (
        <div className="bg-amber-500 text-slate-950 px-4 py-2.5 rounded-xl font-black text-xs flex items-center justify-between shadow-lg animate-pulse">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-slate-950 flex-shrink-0" />
            <span>
              IMPERSONATION ACTIVE: You are viewing VidPulse as <strong>{impersonatedUser.email}</strong> ({impersonatedUser.fullName || 'User'}).
            </span>
          </div>
          <button
            onClick={onExitImpersonation}
            className="px-3 py-1 rounded-lg bg-slate-950 text-white hover:bg-slate-900 text-[11px] font-extrabold flex items-center gap-1 transition-all"
          >
            <X className="w-3.5 h-3.5" />
            <span>Exit Impersonation</span>
          </button>
        </div>
      )}

      {/* Main Admin Top Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900/80 p-4 rounded-2xl border border-slate-800 shadow-md">
        <div className="relative w-full sm:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Global Search (Users, Emails, Channels, Payments...)"
            value={searchTerm}
            onChange={handleSearchChange}
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 transition-all"
          />
        </div>

        <div className="flex items-center gap-3 self-end sm:self-auto">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs font-bold">
            <Shield className="w-3.5 h-3.5 text-purple-400" />
            <span>Role: {userProfile.role || 'SUPER_ADMIN'}</span>
          </div>

          <div className="flex items-center gap-2 pl-3 border-l border-slate-800">
            <div className="w-7 h-7 rounded-full bg-purple-600 flex items-center justify-center font-black text-white text-xs">
              {(userProfile.name || 'Admin')[0].toUpperCase()}
            </div>
            <span className="text-xs font-extrabold text-white hidden sm:inline">{userProfile.name || 'Admin'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
