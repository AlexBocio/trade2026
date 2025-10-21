/**
 * Root App component
 */

import { RouterProvider } from 'react-router-dom';
import { router } from './Router';
import { useAppStore } from './store/useAppStore';
import { useEffect } from 'react';

function App() {
  const { setTheme } = useAppStore();

  // Initialize dark theme on mount
  useEffect(() => {
    setTheme('dark');
  }, [setTheme]);

  return <RouterProvider router={router} />;
}

export default App;
