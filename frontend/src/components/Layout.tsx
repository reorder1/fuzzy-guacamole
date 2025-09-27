'use client';

import Link from 'next/link';
import { Container, Nav, Navbar } from 'react-bootstrap';
import { useAuth } from '../lib/auth';

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  return (
    <>
      <Navbar bg="dark" variant="dark" expand="lg">
        <Container>
          <Navbar.Brand href="/">OMR Portal</Navbar.Brand>
          <Nav className="me-auto">
            <Nav.Link as={Link} href="/batches">Batches</Nav.Link>
            <Nav.Link as={Link} href="/exams">Exams</Nav.Link>
          </Nav>
          <Nav>
            {user ? (
              <Nav.Link onClick={logout}>Logout ({user.username})</Nav.Link>
            ) : (
              <Nav.Link as={Link} href="/login">
                Login
              </Nav.Link>
            )}
          </Nav>
        </Container>
      </Navbar>
      <Container className="py-4">{children}</Container>
    </>
  );
}
