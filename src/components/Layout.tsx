import React from 'react';
import { Toaster } from 'sonner';
import Header from './Header';
import Footer from './Footer';

interface LayoutProps {
  children: React.ReactNode;
  showHeader?: boolean;
  showFooter?: boolean;
  className?: string;
}

const Layout: React.FC<LayoutProps> = ({ 
  children, 
  showHeader = true, 
  showFooter = true,
  className = '' 
}) => {
  return (
    <div className="min-h-screen flex flex-col">
      {showHeader && <Header />}
      <main className={`flex-1 ${className}`}>
        {children}
      </main>
      {showFooter && <Footer />}
      <Toaster position="top-right" richColors />
    </div>
  );
};

export default Layout;