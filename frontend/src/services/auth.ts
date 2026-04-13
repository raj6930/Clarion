/**
 * Auth service — login, register, refresh, me, logout.
 */
import { api, setTokens, clearTokens } from './api';

export interface AuthUser {
  id: string;
  email: string;
  display_name: string;
  role: 'admin' | 'manager' | 'csm' | 'engineer';
  org_id: string;
  org_name: string;
  team_name?: string;
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  user: AuthUser;
}

export async function login(email: string, password: string): Promise<AuthUser> {
  const res = await api<TokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  setTokens(res.access_token, res.refresh_token);
  return res.user;
}

export async function register(email: string, password: string, displayName: string, orgDomain: string): Promise<AuthUser> {
  const res = await api<TokenResponse>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, display_name: displayName, org_domain: orgDomain }),
  });
  setTokens(res.access_token, res.refresh_token);
  return res.user;
}

export async function getMe(): Promise<AuthUser> {
  return api<AuthUser>('/auth/me');
}

export async function logout(): Promise<void> {
  try { await api('/auth/logout', { method: 'POST' }); } catch {}
  clearTokens();
}
