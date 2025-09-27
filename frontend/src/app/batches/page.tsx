'use client';

import { useMutation, useQuery } from '@tanstack/react-query';
import { FormEvent, useState } from 'react';
import { Button, Form, Table } from 'react-bootstrap';
import Link from 'next/link';
import Layout from '../../components/Layout';
import { api } from '../../lib/api';

interface Batch {
  id: number;
  name: string;
  code: string;
}

export default function BatchesPage() {
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const query = useQuery({
    queryKey: ['batches'],
    queryFn: async () => {
      const res = await api.get('/batches/');
      return res.data as Batch[];
    }
  });

  const mutation = useMutation({
    mutationFn: async () => {
      await api.post('/batches/', { name, code });
    },
    onSuccess: () => {
      setName('');
      setCode('');
      query.refetch();
    }
  });

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    mutation.mutate();
  };

  return (
    <Layout>
      <h1>Batches</h1>
      <Form onSubmit={handleSubmit} className="mb-4 d-flex gap-2">
        <Form.Control placeholder="Batch name" value={name} onChange={(e) => setName(e.target.value)} required />
        <Form.Control placeholder="Code" value={code} onChange={(e) => setCode(e.target.value)} required />
        <Button type="submit">Add</Button>
      </Form>
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>Name</th>
            <th>Code</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {query.data?.map((batch) => (
            <tr key={batch.id}>
              <td>{batch.name}</td>
              <td>{batch.code}</td>
              <td>
                <Link href={`/batches/${batch.id}/students`}>Students</Link>
                {' | '}
                <Link href={`/batches/${batch.id}/exams`}>Exams</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Layout>
  );
}
