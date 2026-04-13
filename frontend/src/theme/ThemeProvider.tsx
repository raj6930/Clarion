/**
 * Clarion Theme Provider
 * Three-layer token merge: base defaults → org-level theme_config → user preferences.
 * Injects CSS custom properties into :root.
 */
import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react';

export interface ThemeTokens {
  primaryColour: string;
  accentColour: string;
  fontFamily: string;
  cardRadius: number;
  density: 'compact' | 'comfortable' | 'spacious';
  darkMode: boolean;
  logoUrl?: string;
  companyName: string;
}

interface ThemeContextType {
  tokens: ThemeTokens;
  setTokens: (partial: Partial<ThemeTokens>) => void;
  toggleDarkMode: () => void;
}

const baseTokens: ThemeTokens = {
  primaryColour: '#2563EB',
  accentColour: '#3B82F6',
  fontFamily: "'Geist Sans', system-ui, sans-serif",
  cardRadius: 14,
  density: 'comfortable',
  darkMode: false,
  companyName: 'Clarion',
};

const densityMap = {
  compact:     { gap: '10px', padding: '12px', fontSize: '12px' },
  comfortable: { gap: '14px', padding: '18px', fontSize: '13px' },
  spacious:    { gap: '18px', padding: '24px', fontSize: '14px' },
};

const ThemeContext = createContext<ThemeContextType>({
  tokens: baseTokens,
  setTokens: () => {},
  toggleDarkMode: () => {},
});

function applyTokensToRoot(tokens: ThemeTokens) {
  const root = document.documentElement;
  const d = densityMap[tokens.density];

  root.style.setProperty('--clarion-primary', tokens.primaryColour);
  root.style.setProperty('--clarion-accent', tokens.accentColour);
  root.style.setProperty('--clarion-font', tokens.fontFamily);
  root.style.setProperty('--clarion-radius', `${tokens.cardRadius}px`);
  root.style.setProperty('--clarion-gap', d.gap);
  root.style.setProperty('--clarion-card-padding', d.padding);
  root.style.setProperty('--clarion-font-size', d.fontSize);

  root.setAttribute('data-theme', tokens.darkMode ? 'dark' : '');
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [tokens, setTokensState] = useState<ThemeTokens>(baseTokens);

  const setTokens = useCallback((partial: Partial<ThemeTokens>) => {
    setTokensState(prev => {
      const next = { ...prev, ...partial };
      applyTokensToRoot(next);
      return next;
    });
  }, []);

  const toggleDarkMode = useCallback(() => {
    setTokens({ darkMode: !tokens.darkMode });
  }, [tokens.darkMode, setTokens]);

  useEffect(() => {
    applyTokensToRoot(tokens);
  }, []);

  return (
    <ThemeContext.Provider value={{ tokens, setTokens, toggleDarkMode }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => useContext(ThemeContext);
