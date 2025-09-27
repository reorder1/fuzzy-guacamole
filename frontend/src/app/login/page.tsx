'use client';

import { FormEvent, useState } from 'react';
import { Alert, Button, Card, Form } from 'react-bootstrap';
import { useRouter } from 'next/navigation';
import Layout from '../../components/Layout';
import { useAuth } from '../../lib/auth';

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    try {
      await login(username, password);
      router.push('/');
    } catch (err) {
      setError('Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <Card className="mx-auto" style={{ maxWidth: 400 }}>
        <Card.Body>
          <Card.Title>Login</Card.Title>
          {error && <Alert variant="danger">{error}</Alert>}
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Username</Form.Label>
              <Form.Control value={username} onChange={(e) => setUsername(e.target.value)} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Password</Form.Label>
              <Form.Control type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </Form.Group>
            <Button type="submit" disabled={loading} className="w-100">
              {loading ? 'Signing in…' : 'Login'}
            </Button>
          </Form>
        </Card.Body>
      </Card>
    </Layout>
  );
}
