import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import './index.css';
// اگر از LanguageProvider استفاده می‌کنید، آن را از کامنت خارج کنید:
// import { LanguageProvider } from './components/eco/i18n';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {/* <LanguageProvider> */}
          <App />
        {/* </LanguageProvider> */}
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);