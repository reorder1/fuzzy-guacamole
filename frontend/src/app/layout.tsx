import 'bootstrap/dist/css/bootstrap.min.css';
import './globals.css';
import { AuthProvider } from '../lib/auth';
import QueryProvider from '../components/QueryProvider';

export const metadata = {
  title: 'OMR Portal',
  description: 'Scan and analyse exam answer sheets'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <QueryProvider>{children}</QueryProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
